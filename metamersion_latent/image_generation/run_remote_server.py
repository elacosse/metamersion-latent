#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("/home/ubuntu/latentblending/")
from latent_blending import LatentBlending, add_frames_linear_interp, get_time
from stable_diffusion_holder import StableDiffusionHolder

import time
import zmq
import numpy as np
from threading import Thread
import json
import uuid
import vimeo 

ACCESS_TOKEN="230393bc5ca14fbb51ff851b6a88bd11"
SECRET="mMsciVQU5bknMO6dB+6Sf2gERlOyiBALub1I3fsVMS7v/UNNO4KVpMyz1xrzPePzydDExnqp9qA9Uf99tO1AgqLqA7B1Dcq47JqDUVbu4xwa3gOsuMbHR69glgrtbMz1"
CLIENT_ID="0a777a38782e37bcad956b2c405e23b34f931968"

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



def upload_vimeo(fp_movie, name_video):
    v = vimeo.VimeoClient(
        token=ACCESS_TOKEN,
        key=CLIENT_ID,
        secret=SECRET
    )

    # Make the request to the server for the "/me" endpoint.
    about_me = v.get('/me')

    # Make sure we got back a successful response.
    assert about_me.status_code == 200
    video_uri = v.upload(
        fp_movie,
        data={'name': name_video, 'description': 'ls1', 'privacy': 'unlisted', 'chunk_size': 512 * 1024}
                )

    return video_uri

# 512
if False:
    fp_ckpt = "latentblending/v2-1_512-ema-pruned.ckpt"
    fp_config = 'latentblending/configs/v2-inference.yaml'

# 768
fp_ckpt = "latentblending/v2-1_768-ema-pruned.ckpt"
fp_config = 'latentblending/configs/v2-inference-v.yaml'

sdh = StableDiffusionHolder(fp_ckpt, fp_config)

lb = LatentBlending(sdh)




server = Server(7555, 7556, image_dims=IMAGE_DIMS, verbose=True)




# Multi Movie Generation
print("STARTED SERVER... LISTENING")
while True:
    msg = server.get_last_request()
    if msg is not None:
        try:
            print("GOT MESSAGE")
            list_prompts = msg['meta']['list_prompts']
            neg_prompt = msg['meta']['neg_prompt']
            width = int(msg['meta']['width'])
            height = int(msg['meta']['height'])
            duration_single_trans = int(msg['meta']['duration_single_trans'])
            depth_strength = float(msg['meta']['depth_strength'])
            quality = msg['meta']['quality']
            code_subject = msg['meta']['code_subject']

            # lb.set_width(width)
            # lb.set_height(height)

            lb.load_branching_profile(quality=quality, depth_strength=depth_strength)
            fps = 30

            # Specify a list of prompts below
            list_prompts = [l for l in list_prompts if len(l) > 10]
            print(f"found {len(list_prompts)} prompts. generating movie now")

            # You can optionally specify the seeds
            list_seeds = None
            name_video = f"ls1_{get_time('second')}_{code_subject}"
            fp_movie = f"/home/ubuntu/{name_video}.mp4"

            lb.run_multi_transition(
                    fp_movie, 
                    list_prompts, 
                    list_seeds=None, 
                    fps=fps, 
                    duration_single_trans=duration_single_trans
                )


            video_uri = upload_vimeo(fp_movie, name_video)
            video_url = f"https://vimeo.com/{video_uri.split("/")[-1]}"

            print(f"Upload complete. URI: {video_url}")
            meta = {}
            img = (255*np.random.rand(5, 5, 3)).astype(np.uint8)
            meta["dims"] = (img.shape[0], img.shape[1], 3)
            meta["code_sending"] = str(uuid.uuid4())[:5]
            meta["fp_movie"] = fp_movie
            server.publish_thread(meta, img)



        except Exception as e:
            print(f"EXCEPTION! {e}")





# Single Image Generation
if False:
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


    

    

