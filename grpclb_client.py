import logging

import grpc

import grpclb_pb2
import grpclb_pb2_grpc
from hfc.fabric import Client

channelName = "mychannel"
chaincodeName = "mycc"
functionName = "ping"
address = "127.0.0.1:50051"

def run():
    for i in range(1,1000000):
        channel = grpc.insecure_channel(address)
        stub = grpclb_pb2_grpc.GrpclbStub(channel)
        response = stub.Execute(grpclb_pb2.TxRequest(
            channelName = channelName,
            chaincodeName = chaincodeName,
            functionName = functionName,
            args = ['a', 'b', '1']
        ))
    # print(response)

if __name__ == '__main__':
    logging.basicConfig()
    run()
