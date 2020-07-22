from concurrent import futures
import logging
import asyncio
import ast
import socket, requests as req, json, yaml, re, copy

from hfc.fabric import Client
import docker
import grpc
import grpclb_pb2 
import grpclb_pb2_grpc


# fabric-sdk-py
loop = asyncio.get_event_loop()
cli = Client(net_profile="test/fixtures/network.json")
org1_admin = cli.get_user(org_name='org1.example.com', name='Admin')
    
# 이 함수안에 prometheus 관련 로직 넣기
def get_low_latency_endorsing_peers():
    org1_node_list = []
    org2_node_list = []
    peers = []

    res = req.post("http://172.17.0.2:5000/get_latency_list", headers={"content-type":"application/json"})
    res = res.json()

    for peer in res:
        if peer['node'][6:].startswith("org1"):
            org1_node_list.append(peer['node'])
        elif peer['node'][6:].startswith("org2"):
            org2_node_list.append(peer['node'])
    
    peers.append(org1_node_list[0])
    peers.append(org2_node_list[0])
    # print(peers)
    return peers

def get_average_latency():
    org1_node_latency_list = []
    org2_node_latency_list = []
    latencies = []

    res = req.post("http://127.0.0.1:5000/get_latency_list", headers={"content-type":"application/json"})
    res = res.json()

    for peer in res:
        if peer['node'][6:].startswith("org1"):
            org1_node_latency_list.append(peer['latency'])
        elif peer['node'][6:].startswith("org2"):
            org2_node_latency_list.append(peer['latency'])

    latencies.append(org1_node_latency_list[0])
    latencies.append(org2_node_latency_list[0])
    avg_latency = (latencies[0] + latencies[1]) / 2
    # print("avg_latency: "+ str(avg_latency))
    return avg_latency

class GrpclbServicer(grpclb_pb2_grpc.GrpclbServicer):
    def Execute(self, request, context):
        avg_latency = get_average_latency()
        peers = get_low_latency_endorsing_peers()

        # The response should be true if succeed
        response = loop.run_until_complete(cli.chaincode_invoke(
                        requestor=org1_admin,  
                        channel_name=request.channelName,  
                        peers=peers,   
                        args=request.args,
                        cc_name=request.chaincodeName,  
                        avg_latency=get_average_latency(),
                        transient_map=None, # optional, for private data
                        wait_for_event=True, # for being sure chaincode invocation has been commited in the ledger, default is on tx event
                        ))

        # print(response)     # response -> chaincode_invoke return: proposal(header + payload)

        return grpclb_pb2.TxResponse(
            # payload = [b'\xDE\xAD'],      # response.xxx 처럼 사용하여 TxResponse 채우기
            payload = response.payload,
            header = response.header,
        )
    
    def Query(self, request, context):
        return grpclb_pb2.TxResponse(
            payload = b'\xDE\xAD',
        )
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpclb_pb2_grpc.add_GrpclbServicer_to_server(
        GrpclbServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
