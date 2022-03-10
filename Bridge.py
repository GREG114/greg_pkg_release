import grpc
import json
import isearch_pb2 as pb2
import isearch_pb2_grpc as pb2_grpc


class Bridge():
    def __init__(self,host):
        self.host=host
    
    def run(self,url,req,headers,method):
        conn = grpc.insecure_channel(self.host)
        client = pb2_grpc.HelloStub(channel=conn)
        res =client.apiBridge(pb2.req(
        url=url,
        req=req,        
        headers=headers,
        method=method,
        ))
        return res



