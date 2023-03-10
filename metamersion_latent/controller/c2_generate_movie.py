#!/usr/bin/env python3


import json
import sys
import time
from threading import Thread

import numpy as np
import zmq
from dotenv import find_dotenv, load_dotenv
from PIL import Image

sys.path.append("../..")
sys.path.append("..")
import os
import shutil
import subprocess

from metamersion_latent.llm.config import Config
from metamersion_latent.utils import load_yaml, user_choice
import argparse

IMAGE_DIMS = (400, 400, 3)
EMO_STRING_LEN = 2  # In bytes
TOPIC = b"\x00"
TOPIC_LEN = 1  # In bytes
BYTES_FOR_META_LEN = 4
TIMEOUT = 3000


def conpr(ver: bool, msg):
    if ver:
        print(msg)


def ser_req(meta: dict, a: np.ndarray):
    meta_json = json.dumps(meta)
    meta_len = len(meta_json)
    full_msg = bytearray(meta_len.to_bytes(BYTES_FOR_META_LEN, byteorder="big"))
    full_msg.extend(meta_json.encode("UTF-8"))
    full_msg.extend(a.tobytes())
    return bytes(full_msg)


def deser_ndarray(a: bytes, dims: tuple, offset: int):
    a = np.frombuffer(a, dtype=np.uint8, offset=offset)
    a.shape = dims
    return a


def deser_req(req: bytes):
    meta_len = int.from_bytes(req[:BYTES_FOR_META_LEN], byteorder="big")
    meta_json = req[BYTES_FOR_META_LEN : BYTES_FOR_META_LEN + meta_len].decode("UTF-8")
    meta_dict = json.loads(meta_json)

    image = deser_ndarray(req, meta_dict["dims"], BYTES_FOR_META_LEN + meta_len)
    return {"meta": meta_dict, "image": image}


class Client:
    def __init__(
        self,
        server_ip: str,
        server_port: int,
        publisher_port: int,
        image_dims: tuple,
        req_timeout=3000,
        max_upd_interval=1500,
        verbose=False,
    ):
        self.TIMEOUT = req_timeout
        self.STABILITY_TIMEOUT = max_upd_interval

        self.lu_tstamp = time.time() * 1000
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

        self.client = self.__init_req_socket(self.context)
        conpr(
            self.verbose,
            f'[ZMQ-client]: "Ready to send requests to tcp://{server_ip}:{server_port}."',
        )

        updates_listener = Thread(target=self.__listen_to_updates)
        updates_listener.start()
        conpr(
            self.verbose,
            f'[ZMQ-client]: "Started listening to publisher from tcp://{server_ip}:{publisher_port}."',
        )

        self.code_last = "NONE"
        self.t_timeout = 1000

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
                self.lu_tstamp = time.time() * 1000
                msg_bytes = resp[TOPIC_LEN:]
                msg = deser_req(msg_bytes)
                self.last_update = msg
                conpr(
                    self.verbose,
                    f'[ZMQ-client]: "Received a published message\n{msg["meta"]}"',
                )
            except zmq.Again as e:
                print(f"There is no message yet ({e})")
                pass

    def __send(self, meta: dict, image: np.ndarray):
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
            conpr(
                self.verbose, f'[ZMQ-client]: "Server has received the request: {meta}"'
            )
            self.allow_request = True
        except zmq.Again:
            self.req_suc = False
            conpr(
                self.verbose,
                '[ZMQ-client]: "Wating time for a response exceeded timeout."',
            )
            self.client = self.__init_req_socket(self.context)
            self.allow_request = True

    def send_thread(self, meta: dict, image: np.ndarray):
        if self.allow_request:
            self.allow_request = False
            request_sender = Thread(target=self.__send, args=[meta, image])
            request_sender.start()

    def get_last_update(self):
        return self.last_update

    def is_stable(self):
        if not self.req_suc:
            return False
        if time.time() * 1000 - self.lu_tstamp >= self.STABILITY_TIMEOUT:
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
        subscriber.setsockopt(
            zmq.CONFLATE, 1
        )  # Get only last published message, cancel queueing
        subscriber.connect(f"tcp://{self.server_ip}:{self.publisher_port}")
        subscriber.setsockopt(zmq.SUBSCRIBE, TOPIC)
        return subscriber

    def reinit_sockets(self):
        self.sub_reinit_requested = True
        self.req_reinit_requested = True

    def run_image(self, dict_meta):

        # assemble message
        dict_meta["server_ip"] = self.server_ip
        dict_meta["call"] = "run_image"

        image_ignore = (255 * np.random.rand(5, 5, 3)).astype(np.uint8)
        dict_meta["dims"] = (5, 5, 3)  # ignore this shit

        self.send_thread(dict_meta, image_ignore)

        t0 = time.time()

        while True:
            response = self.get_last_update()
            if (
                response is not None
                and response["meta"]["code_sending"] != self.code_last
            ):
                self.code_last = response["meta"]["code_sending"]
                img = response["image"]
                img = Image.fromarray(img)
                return img

            if time.time() - t0 > self.t_timeout:
                print("FAIL! TIMEOUT! IS SERVER UP?")
                return

    def run_movie(self, dict_meta):

        # assemble message
        dict_meta["call"] = "run_movie"
        dict_meta["server_ip"] = self.server_ip

        image_ignore = (255 * np.random.rand(5, 5, 3)).astype(np.uint8)
        dict_meta["dims"] = (5, 5, 3)  # ignore this shit

        self.send_thread(dict_meta, image_ignore)

        t0 = time.time()

        while True:
            response = self.get_last_update()
            if (
                response is not None
                and response["meta"]["code_sending"] != self.code_last
            ):
                self.code_last = response["meta"]["code_sending"]
                img = response["image"]
                img = Image.fromarray(img)
                return response["meta"]["scp_cmd"]

            if time.time() - t0 > self.t_timeout:
                print("FAIL! TIMEOUT! IS SERVER UP?")
                return


parser = argparse.ArgumentParser(description="c2_generate_movies")
parser.add_argument("--id_server", type=int)
parser.add_argument("--fp_config", type=str, default="../configs/chat/ls1_version_4_exp.py")
args = parser.parse_args()

id_server = args.id_server
if id_server == 0:
    ip_server = "129.146.109.171"
elif id_server == 1:
    ip_server = "129.146.3.236" #b
elif id_server == 2:
    ip_server = "129.146.110.17"
elif id_server == 3:
    ip_server = "129.213.23.33"

load_dotenv(find_dotenv(), verbose=False)
dp_base = os.getenv("DIR_SUBJ_DATA")
list_dns = os.listdir(dp_base)
list_dns = [l for l in list_dns if l[0] == "2"]
list_dns = [l for l in list_dns if os.path.isfile(os.path.join(dp_base, l, "chat_analysis.yaml"))]
list_dns = [l for l in list_dns if not os.path.isfile(os.path.join(dp_base, l, "started_movie_comp.txt"))]
list_dns.sort(reverse=True)
list_dns = list_dns[0:10]
dn = user_choice(list_dns, sort=False, suggestion=list_dns[0])
dp_session = f"{dp_base}/{dn}"

fp_chat_analysis = os.path.join(dp_session, "chat_analysis.yaml")
config = Config.fromfile(args.fp_config)
# config = Config.fromfile("../configs/chat/ls1_version_4.py")
dict_meta = load_yaml(fp_chat_analysis)

# ip_server = "138.2.229.216"
zmq_client = Client(ip_server, 7555, 7556, image_dims=IMAGE_DIMS, verbose=True)

dict_meta["duration_single_trans"] = config.duration_single_trans
dict_meta["negative_prompt"] = config.negative_prompt
dict_meta["ip_server"] = ip_server
dict_meta["negative_prompt"] = config.negative_prompt
dict_meta["quality"] = config.quality
dict_meta["depth_strength"] = config.depth_strength
dict_meta["silence_begin"] = config.silence_begin
dict_meta["ChosenSet"] = config.ChosenSet
dict_meta["width"] = 1280#config.width
dict_meta["height"] = 768 #config.height
dict_meta["duration_fade"] = config.duration_fade
dict_meta["seed"] = config.seed
dict_meta["code_subject"] = dn

def txt_save(fp_txt, list_blabla, append=False):
    if append:
        mode = "a+"
    else:
        mode = "w"
    with open(fp_txt, mode) as fa:
        for item in list_blabla:
            fa.write("%s\n" % item)
# Save movie started!
fp_txt = os.path.join(dp_session, "started_movie_comp.txt")
txt_save(fp_txt, [f"adsf"])

scp_cmd = zmq_client.run_movie(dict_meta)

print(scp_cmd)

#%% Download
ts_server = scp_cmd[:-2].split("/")[-1]
dp_computed = os.path.join(dp_session, f"computed_{ts_server}")
os.makedirs(dp_computed)
# copy the chat analysis
shutil.copyfile(
    os.path.join(dp_session, "chat_analysis.yaml"),
    os.path.join(dp_computed, "chat_analysis.yaml"),
)

# SCP everything
scp_cmd_mod = scp_cmd[:-2] + f"/current.mp4 {dp_session}/"
subprocess.call(scp_cmd_mod, shell=True)
scp_cmd_mod = scp_cmd[:-2] + f"/current.mp3 {dp_session}/"
subprocess.call(scp_cmd_mod, shell=True)
print("SCP DONE!")

# try:
#     shutil.copyfile(os.path.join(dp_computed, "current.mp4"), os.path.join(dp_session, "current.mp4"))
# except Exception as e:
#     print(f"FAIL! VOICE? {e}.")
#     shutil.copyfile(os.path.join(dp_computed, "current_nosound.mp4"), os.path.join(dp_session, "current.mp4"))

# try:
#     shutil.copyfile(os.path.join(dp_computed, "current.mp3"), os.path.join(dp_session, "current.mp3"))
# except Exception as e:
#     print(f"FAIL! VOICE? {e}.")
#     shutil.copyfile(os.path.join(dp_computed, "music.mp3"), os.path.join(dp_session, "current.mp3"))
    
print("COPYING DONE!")
print("It's safe to hit CTRl+C TO GET OUT OF HERE :)")
