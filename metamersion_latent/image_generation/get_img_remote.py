#!/usr/bin/env python3


import time
import zmq
import numpy as np
from threading import Thread
import json
import matplotlib.pyplot as plt
from PIL import Image



IMAGE_DIMS = (400,400,3)
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

        self.code_last = "NONE"
        self.t_timeout = 600
        
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



    def run_image(self, dict_meta):
        
        # assemble message
        dict_meta['server_ip'] = self.server_ip
        dict_meta['call'] = 'run_image'
        
        image_ignore = (255*np.random.rand(5, 5, 3)).astype(np.uint8)
        dict_meta['dims'] = (5, 5, 3) #ignore this shit
        
        self.send_thread(dict_meta, image_ignore)
        
        t0 = time.time()
        
        while True:
            response = self.get_last_update()
            if response is not None and response["meta"]["code_sending"] != self.code_last:
                self.code_last = response["meta"]["code_sending"]
                img = response['image']
                img = Image.fromarray(img)
                return img
    
            if time.time() - t0 > self.t_timeout:
                print("FAIL! TIMEOUT! IS SERVER UP?")
                return



    def run_movie(self, dict_meta):
        
        # assemble message
        dict_meta['call'] = 'run_movie'
        dict_meta['server_ip'] = self.server_ip
        
        image_ignore = (255*np.random.rand(5, 5, 3)).astype(np.uint8)
        dict_meta['dims'] = (5, 5, 3) #ignore this shit
        
        self.send_thread(dict_meta, image_ignore)
        
        t0 = time.time()
        
        while True:
            response = self.get_last_update()
            if response is not None and response["meta"]["code_sending"] != self.code_last:
                self.code_last = response["meta"]["code_sending"]
                img = response['image']
                img = Image.fromarray(img)
                return response["meta"]["scp_cmd"]
    
            if time.time() - t0 > self.t_timeout:
                print("FAIL! TIMEOUT! IS SERVER UP?")
                return

if False:
    #%%
    xxx
    #%%
    # spawn remote connection to server
    ip_server = "138.2.229.216"
    zmq_client = Client(ip_server, 7555, 7556, image_dims=IMAGE_DIMS, verbose=True)
    
    duration_single_trans = 15
    ChosenSet = 1 #music set! needs to be between 1 and 13
    
    silence_begin = -3
    speaker_indx = 0
    
    quality = 'lowest'
    depth_strength = 0.5
    tts_length_scale = 1.2
    
    duration_fade = 20
    seed = 420
    
    width = 768
    height = 512
    
    list_prompts = []
    list_prompts.append("painting of a forest")
    list_prompts.append("painting of a house")
    list_prompts.append("painting of a ocean")
    
    narration_list = []
    narration_list.append("painting of a forest. it was like really beautiful and stuff")
    narration_list.append("painting of a house. super nice house. really.")
    narration_list.append("painting of a ocean. the ocean was very cold and blue")
    
    
    negative_prompt = "ugly, blurry"
    
    dict_meta = {}
    dict_meta['list_prompts'] = list_prompts
    dict_meta['narration_list'] = narration_list
    dict_meta['duration_single_trans'] = duration_single_trans
    dict_meta['ip_server'] = "138.2.229.216"
    dict_meta['negative_prompt'] = negative_prompt
    dict_meta['quality'] = quality
    dict_meta['depth_strength'] = depth_strength
    dict_meta['silence_begin'] = silence_begin
    dict_meta['speaker_indx'] = speaker_indx
    dict_meta['tts_length_scale'] = tts_length_scale
    dict_meta['ChosenSet'] = ChosenSet
    dict_meta['width'] = width
    dict_meta['height'] = height
    dict_meta['duration_fade'] = duration_fade
    dict_meta['seed'] = seed
    
    scp_cmd = zmq_client.run_movie(dict_meta)
    
    print(scp_cmd)
    
    
    #%%
    ip_server = "138.2.229.216"
    zmq_client = Client(ip_server, 7555, 7556, image_dims=IMAGE_DIMS, verbose=True)

    prompt = "painting of a forest"
    negative_prompt = "ugly, blurry"
    seed = 420
    width = 768
    height = 512
    
    dict_meta = {}
    dict_meta['prompt'] = prompt
    dict_meta['neg_prompt'] = negative_prompt
    dict_meta['seed'] = seed
    dict_meta['width'] = width
    dict_meta['height'] = height
    
    img = zmq_client.run_image(dict_meta)
    
