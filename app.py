from flask import Flask, json
from flask_restful import Api, Resource
from apscheduler.schedulers.background import BackgroundScheduler
from pythonping import ping

import socket, requests as req, json
import docker
import ast
import copy
import random


# Flask
app = Flask(__name__)
api = Api(app)

# docker
client = docker.from_env()

global latency_list


def get_latency(ip_address):
    response_list = ping(ip_address, size=1000, count=50)
    return {'average_latency': response_list.rtt_avg_ms}

def set_latency_list():
    global latency_list
    temp_latency_list = []

    containers = client.containers.list()
    for container in containers:
        container_ip_address = container.attrs["NetworkSettings"]["IPAddress"]

        if str(container.name).startswith('peer'):
            res = get_latency(container_ip_address)
            node = container.name
            
            # peer0 & peer1 외의 다른 peerX 없음
            if str(container.name).startswith('peer0'):
                latency = str(res["average_latency"] + random.uniform(3,7))
            else:
                latency = str(res["average_latency"] + random.uniform(3,10))
            
            # ex: {'node': 'peer1.org2.example.com', 'latency': 0.0} 
            latency_str = ('{"node"' + ":" + '\"' + node + '\",' + '\"latency"' + ":" + latency + '}')
            temp_latency_list.append(ast.literal_eval(latency_str))

    temp_latency_list.sort(key=lambda item: item['latency'])
    latency_list = copy.deepcopy(temp_latency_list)
    print(latency_list)

# APScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(set_latency_list, 'interval', seconds=5)
scheduler.start()

class get_latency_list(Resource):
    def post(self):
        return latency_list

api.add_resource(get_latency_list, '/get_latency_list')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
