import asyncio
from hfc.fabric import Client

loop = asyncio.get_event_loop()

cli = Client(net_profile="network.json")
org1_admin = cli.get_user('org1.example.com', 'Admin')
print("============================")

# response = loop.run_until_complete(cli.get_channel_config(
#     requestor=org1_admin,
#     channel_name="mychannel",
#     peers=['peer0.org1.example.com']    
# ))
# print (response == True)



# Create a New Channel, the response should be true if succeed
# response = loop.run_until_complete(cli.channel_create(
#             orderer='orderer.exam
# print(response == True)
#             config_yaml='e2e_cli/',
#             channel_profile='TwoOrgsChannel'
#             ))
# print(response == True)

# # Join Peers into Channel, the response should be true if succeed
# orderer_admin = cli.get_user(org_name='orderer.example.com', name='Admin')
# responses = loop.run_until_complete(cli.channel_join(
#                requestor=org1_admin,
#                channel_name='mychannel',
#                peers=['peer0.org1.example.com',
#                       'peer1.org1.example.com'],
#                orderer='orderer.example.com'
#                ))


# # Invoke a chaincode
# args = ['a', 'b', '50']
# # The response should be true if succeed
# response = loop.run_until_complete(cli.chaincode_invoke(
#                requestor=org1_admin,
#                channel_name='mychannel',
#                peers=['peer0.org1.example.com','peer0.org2.example.com'],
#                args=args,
#                cc_name='mycc',
#                transient_map=None, # optional, for private data
#                wait_for_event=True, # for being sure chaincode invocation has been commited in the ledger, default is on tx event
#                #cc_pattern='^invoked*' # if you want to wait for chaincode event and you have a `stub.SetEvent("invoked", value)` in your chaincode
#                ))
# print(response)

# print('-----------')
# response = loop.run_until_complete(cli.query_instantiated_chaincodes(
#     requestor=org1_admin,
#     channel_name='mychannel',
#     peers=['peer0.org1.example.com'],
# ))
# print('-----------')
# print(response == True)

# Query a chaincode
args = ['a']
# The response should be true if succeed
response = loop.run_until_complete(cli.chaincode_query(
               requestor=org1_admin,
               channel_name='mychannel',
               peers=['peer0.org1.example.com'],
               args=args,
               cc_name='mycc'
               ))
print(response)