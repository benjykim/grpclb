from concurrent import futures
import logging
import asyncio
import ast
import time
import socket, requests as req, json, yaml, re, copy

from hfc.fabric import Client
import docker
import grpc
import grpclb_pb2 
import grpclb_pb2_grpc


# fabric-sdk-py
loop = asyncio.get_event_loop()
cli = Client(net_profile="./network.json")
org1_admin = cli.get_user(org_name='org1.example.com', name='Admin')


# if the CPU usage of endorsing peer exceeds 70%, then remove that peer from endorsing peer list
def exclude_endorsing_peer_with_cpu_usage(org1_node_list, org2_node_list):
    peers_to_be_excluded = []

    res = req.post("http://172.29.0.2:5001/get_cpu_list", headers={"content-type":"application/json"})
    json_data = res.json()

    for peer in json_data:
        if peer['cpu_usage'] > 70.0:
            peers_to_be_excluded.append(peer['node'])

    for peer in peers_to_be_excluded:
        if 'org1' in peer:
            org1_node_list.remove(peer)
        elif 'org2' in peer:
            org2_node_list.remove(peer)

    return org1_node_list, org2_node_list

# if the Memory usage of endorsing peer exceeds 60%, then remove that peer from endorsing peer list
def exclude_endorsing_peer_with_mem_usage(org1_node_list, org2_node_list):
    peers_to_be_excluded = []

    res = req.post("http://172.29.0.2:5001/get_mem_list", headers={"content-type":"application/json"})
    json_data = res.json()

    for peer in json_data:
        if peer['mem_usage'] > 60.0:
            peers_to_be_excluded.append(peer['node'])

    for peer in peers_to_be_excluded:
        if 'org1' in peer:
            org1_node_list.remove(peer)
        elif 'org2' in peer:
            org2_node_list.remove(peer)

    return org1_node_list, org2_node_list

def get_endorsing_peers_with_latency():
    org1_node_list = []
    org2_node_list = []
    peers = []

    res = req.post("http://172.29.0.5:5000/get_latency_list", headers={"content-type":"application/json"})
    json_data = res.json()

    for peer in json_data:
        if 'org1' in peer['node']:
            org1_node_list.append(peer['node'])
        elif 'org2' in peer['node']:
            org2_node_list.append(peer['node'])
    
    # exclude endorsing peers with cpu, memory usage (be used like filter...)
    org1_node_list, org2_node_list = exclude_endorsing_peer_with_cpu_usage(org1_node_list, org2_node_list)
    org1_node_list, org2_node_list = exclude_endorsing_peer_with_mem_usage(org1_node_list, org2_node_list)

    # select endorsing peers --> if there is any available endorsing peers, then error...(try&catch should be needed...)
    peers = select_endorsing_peers(org1_node_list, org2_node_list)

    # calculate the latency of selected peers
    latency = calculate_avg_latency(json_data, peers)

    return peers, latency

def select_endorsing_peers(org1_node_list, org2_node_list):
    peers = []
    if not org1_node_list:
        print("org1_node_list is a empty list!")
    else:
        peers.append(org1_node_list[0])
    
    if not org2_node_list:
        print("org2_node_list is a empty list!")
    else:
        peers.append(org2_node_list[0])
    
    return peers

def calculate_avg_latency(json_data, peers):
    latency = 0
    for selected_peer in peers:
        for peer in json_data:
            if selected_peer in peer['node']:
                latency += peer['latency']
    avg_latency = latency / 2
    return avg_latency

class GrpclbServicer(grpclb_pb2_grpc.GrpclbServicer):
    def Execute(self, request, context):
        peers, avg_latency = get_endorsing_peers_with_latency()

        # The response should be true if succeed
        response = loop.run_until_complete(cli.chaincode_invoke(
                            requestor=org1_admin,  
                            channel_name=request.channelName,  
                            peers=peers,   
                            fcn=request.functionName,
                            args=request.args,
                            cc_name=request.chaincodeName,  
                            avg_latency=avg_latency,
                            transient_map=None, # optional, for private data
                            wait_for_event=True, # for being sure chaincode invocation has been commited in the ledger, default is on tx event
                            ))
        # print(response)     # response -> chaincode_invoke return: proposal(header + payload)

        return grpclb_pb2.TxResponse(
            response = response
        )
    
    def Query(self, request, context):
        peers, avg_latency = get_endorsing_peers_with_latency()

        # The response should be true if succeed
        response = loop.run_until_complete(cli.chaincode_query(
               requestor=org1_admin,
               channel_name=request.channelName,
               peers=peers,
               args=request.args,
               fcn=request.functionName,
               cc_name=request.chaincodeName,
               avg_latency=avg_latency
               ))

        return grpclb_pb2.TxResponse(
            response = response
        )
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    grpclb_pb2_grpc.add_GrpclbServicer_to_server(
        GrpclbServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
