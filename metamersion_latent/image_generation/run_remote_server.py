#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("/home/ubuntu/latentblending/")
from stable_diffusion_holder import StableDiffusionHolder


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 18 11:16:14 2022

@author: lugo
"""

import time
import zmq
import numpy as np
from threading import Thread
import json
import uuid


# Emotions
HAPPY = "ha"
SAD = "sa"
SCARED = "sc"
ANGRY = "an"

IMAGE_DIMS = (512,512,3)
EMO_STRING_LEN = 2 # In bytes
TOPIC = b'\x00'
TOPIC_LEN = 1 # In bytes
BYTES_FOR_META_LEN = 4
TIMEOUT = 3000


def conpr(ver:bool, msg):
    if ver:
        print(msg)


def ser_req(meta:dict, a:np.ndarray):
    meta_json = json.dumps(meta)
    meta_len = len(meta_json)
    full_msg = bytearray(meta_len.to_bytes(BYTES_FOR_META_LEN, byteorder="big"))
    full_msg.extend(meta_json.encode("UTF-8"))
    full_msg.extend(a.tobytes())
    return bytes(full_msg)


def deser_ndarray(a:bytes, dims:tuple, offset:int):
    a = np.frombuffer(a, dtype=np.uint8, offset=offset)
    a.shape = dims
    return a


def deser_req(req:bytes):
    meta_len = int.from_bytes(req[:BYTES_FOR_META_LEN], byteorder="big")
    meta_json = req[BYTES_FOR_META_LEN:BYTES_FOR_META_LEN + meta_len].decode("UTF-8")
    meta_dict = json.loads(meta_json)
    
    image = deser_ndarray(req, meta_dict["dims"], BYTES_FOR_META_LEN + meta_len)
    return {
        "meta": meta_dict,
        "image": image
    }




class Server():
    def __init__(self, server_port:int, publisher_port: int, image_dims: tuple, verbose=False):
        self.last_request = {
            "is_new": False,
            "body": {
                "image": None,
                "emotion": None
            }
        }
        self.verbose = verbose
        self.server_port = server_port
        self.publisher_port = publisher_port
        self.image_dims = image_dims

        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(f"tcp://0.0.0.0:{publisher_port}")
        conpr(self.verbose, f'[ZMQ-server]: "Ready to publish to port {publisher_port}."')
        
        requests_listener = Thread(target = self.__listen_to_requests)
        requests_listener.start()
        conpr(self.verbose, f'[ZMQ-server]: "Started listening to client requests at port {server_port}."')


    def __listen_to_requests(self):
        self.server = self.context.socket(zmq.REP)
        self.server.bind(f"tcp://0.0.0.0:{self.server_port}")

        while True:
            req = self.server.recv()
            desreq = deser_req(req)
            self.last_request["body"] = desreq
            self.last_request["is_new"] = True
            conpr(self.verbose, f'[ZMQ-server]: "Received a request: {self.last_request["body"]["meta"]}"')
            self.server.send(b"Success!")

    
    def __publish(self, meta:dict, image:np.ndarray):
        msg = bytearray(TOPIC) #byte to identify the topic which  subscriber subscribes to; read zeromq details about PUB/SUB topics
        msg.extend(ser_req(meta, image))
        self.publisher.send(msg)
        conpr(self.verbose, f'[ZMQ-server]: "Published message"')
   

    def publish_thread(self, meta:dict, image:np.ndarray):
        publisher = Thread(target = self.__publish, args=[meta, image])
        publisher.start()

    
    def get_last_request(self):
        if self.last_request["is_new"]:
            self.last_request["is_new"] = False
            return self.last_request["body"]
        else:
            return None


class Client():
    def __init__(self, server_ip:str, server_port:int, publisher_port:int, image_dims:tuple, req_timeout=3000, max_upd_interval=1500, verbose=False):
        self.TIMEOUT = req_timeout
        self.STABILITY_TIMEOUT = max_upd_interval

        self.lu_tstamp = time.time()*1000
        self.req_suc = True

        self.verbose = verbose
        self.image_dims = image_dims
        self.last_update = None

        self.server_ip = server_ip
        self.server_port = server_port
        self.publisher_port = publisher_port
        
        self.allow_request = True
        self.allow_recv = True
        self.sub_reinit_requested = False
        self.req_reinit_requested = False

        self.context = zmq.Context()
        self.client = None
        self.subscriber = None

        self.client = self.__init_req_socket(self.context);
        conpr(self.verbose, f'[ZMQ-client]: "Ready to send requests to tcp://{server_ip}:{server_port}."')

        updates_listener = Thread(target = self.__listen_to_updates)
        updates_listener.start()
        conpr(self.verbose, f'[ZMQ-client]: "Started listening to publisher from tcp://{server_ip}:{publisher_port}."')


    def __listen_to_updates(self):
        self.subscriber = self.__init_sub_socket(self.context)
        
        while True:
            try:
                if self.sub_reinit_requested:
                    conpr(self.verbose, "[ZMQ-client]: Reiniting sub socket")
                    self.subscriber = self.__init_sub_socket(self.context)
                    self.sub_reinit_requested = False
                resp = self.subscriber.recv()
                # resp = self.subscriber.recv(flags=zmq.NOBLOCK)
                self.lu_tstamp = time.time()*1000
                msg_bytes = resp[TOPIC_LEN:]
                msg = deser_req(msg_bytes) 
                self.last_update = msg
                conpr(self.verbose, f'[ZMQ-client]: "Received a published message\n{msg["meta"]}"')
            except zmq.Again as e:
                print(f"There is no message yet ({e})")
                pass

    
    def __send(self, meta:dict, image:np.ndarray):
        try:
            if self.req_reinit_requested:
                conpr(self.verbose, "[ZMQ-client]: Reiniting req socket")
                self.client = self.__init_req_socket(self.context)
                self.req_reinit_requested = False
            msg = ser_req(meta, image) 
            self.client.send(msg)
            conpr(self.verbose, f'[ZMQ-client]: "Sent a request to the server: {meta}"')
            self.client.recv()
            self.req_suc = True
            conpr(self.verbose, f'[ZMQ-client]: "Server has received the request: {meta}"')
            self.allow_request = True
        except zmq.Again:
            self.req_suc = False
            conpr(self.verbose, f'[ZMQ-client]: "Wating time for a response exceeded timeout."')
            self.client = self.__init_req_socket(self.context)
            self.allow_request = True


    def send_thread(self, meta:dict, image:np.ndarray):
        if self.allow_request:
            self.allow_request = False 
            request_sender = Thread(target = self.__send, args=[meta, image])
            request_sender.start()


    def get_last_update(self):
        return self.last_update


    def is_stable(self):
        if not self.req_suc:
            return False
        if time.time()*1000-self.lu_tstamp >= self.STABILITY_TIMEOUT:
            self.req_suc = False
            return False
        return True


    def __configure_client(self, client):
        # Options needed to set a timeout to a socket.
        # https://stackoverflow.com/questions/26915347/zeromq-reset-req-rep-socket-state
        client.setsockopt(zmq.RCVTIMEO, TIMEOUT)
        client.setsockopt(zmq.REQ_CORRELATE, 1)
        client.setsockopt(zmq.REQ_RELAXED, 1) 
        # Don't keep outstanding messages after closing a socket
        client.setsockopt(zmq.LINGER, 0)

    
    def __init_req_socket(self, context):
        if self.client is not None:
            self.client.close()
        client = context.socket(zmq.REQ)
        self.__configure_client(client)
        client.connect(f"tcp://{self.server_ip}:{self.server_port}")
        return client


    def __init_sub_socket(self, context):
        if self.subscriber is not None:
            self.subscriber.close()
        subscriber = context.socket(zmq.SUB)
        subscriber.setsockopt(zmq.CONFLATE, 1) # Get only last published message, cancel queueing
        subscriber.connect(f"tcp://{self.server_ip}:{self.publisher_port}")
        subscriber.setsockopt(zmq.SUBSCRIBE, TOPIC)
        return subscriber


    def reinit_sockets(self):
        self.sub_reinit_requested = True
        self.req_reinit_requested = True
#%%
if __name__ == "XX__main__":
    client = Client("0.0.0.0", 7555, 7556, image_dims=IMAGE_DIMS, verbose=True)
    server = Server(7555, 7556, image_dims=IMAGE_DIMS, verbose=True)

    # Dummy data:
    image = (255*np.random.rand(IMAGE_DIMS[0], IMAGE_DIMS[1],3)).astype(np.uint8)
    meta = {
        "dims": (400, 400, 3) # Mandatory field
    }

    # To publish image from server:
    server.publish_thread(meta, image)
    
    # To get last request from client:
    # Returns {"meta": dict, "image": np.ndarray} if
    # there is a new request, otherwise returns None
    server.get_last_request()

    # To send request to server:
    meta["emotion"] = "happy"
    client.send_thread(meta, image)

    # To get last published message on client:
    # Return {"meta": dict, "image": np.ndarray}
    client.get_last_update()



# 512
if False:
    fp_ckpt = "latentblending/v2-1_512-ema-pruned.ckpt"
    fp_config = 'latentblending/configs/v2-inference.yaml'

# 768
fp_ckpt = "latentblending/v2-1_768-ema-pruned.ckpt"
fp_config = 'latentblending/configs/v2-inference-v.yaml'

sdh = StableDiffusionHolder(fp_ckpt, fp_config)

server = Server(7555, 7556, image_dims=IMAGE_DIMS, verbose=True)

#%%
# receive
print("STARTED SERVER... LISTENING")
while True:
    msg = server.get_last_request()
    if msg is not None:
        try:
            print("STARTING DIFFUSION!")
            prompt = msg['meta']['prompt']
            neg_prompt = msg['meta']['neg_prompt']
            seed = int(msg['meta']['seed'])
            width = int(msg['meta']['width'])
            height = int(msg['meta']['height'])
            sdh.width = width
            sdh.height = height
            sdh.seed = seed
            sdh.set_negative_prompt(neg_prompt)
            te = sdh.get_text_embedding(prompt)
            img = sdh.run_diffusion_standard(te, return_image=True).astype(np.uint8)
            print("YES! GOT MESSAGE AND RAN DIFF. SENDING...")
            meta = {}
            meta["dims"] = (img.shape[0], img.shape[1], 3)
            meta["code"] = str(uuid.uuid4())[:5]
            server.publish_thread(meta, img)
        except Exception as e:
            print(f"EXCEPTION! {e}")


    

    

