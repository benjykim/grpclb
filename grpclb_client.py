import logging
import time

import grpc

import grpclb_pb2
import grpclb_pb2_grpc
from hfc.fabric import Client

channelName = "mychannel"
chaincodeName = "fabcar"
functionName = "createCar"
numOfTxs = 10
address = "127.0.0.1:50051"

def run():
    for i in range(0, numOfTxs):
        channel = grpc.insecure_channel(address)
        stub = grpclb_pb2_grpc.GrpclbStub(channel)
        response = stub.Execute(grpclb_pb2.TxRequest(
            channelName = channelName,
            chaincodeName = chaincodeName,
            functionName = functionName,
            args = ["CAR2"+str(i), "xxxx"+str(i), "123", "456", "789"],
            numOfTxs = numOfTxs
        ))
        # print(response)

    for i in range(0, numOfTxs):
        channel = grpc.insecure_channel(address)
        stub = grpclb_pb2_grpc.GrpclbStub(channel)
        response = stub.Query(grpclb_pb2.TxRequest(
            channelName = channelName,
            chaincodeName = chaincodeName,
            functionName = 'queryCar',
            args = ["CAR2"+str(i)],
            numOfTxs = numOfTxs
        ))
        print(response)
if __name__ == '__main__':
    logging.basicConfig()
    run()
