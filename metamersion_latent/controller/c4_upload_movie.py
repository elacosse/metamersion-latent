#!/usr/bin/env python3
import time
import zmq
import numpy as np
from threading import Thread
import json
from PIL import Image
import signal
import time

import click
from dotenv import find_dotenv, load_dotenv
import sys
sys.path.append("../..")
sys.path.append("..")
from metamersion_latent.llm.config import Config
from metamersion_latent.utils import save_to_yaml, load_yaml, user_choice
import os
import subprocess
import shutil
import vimeo #pip install PyVimeo


load_dotenv(find_dotenv(), verbose=False)

ACCESS_TOKEN = os.getenv("VIMEO_ACCESS_TOKEN")
SECRET = os.getenv("VIMEO_SECRET")
CLIENT_ID = os.getenv("VIMEO_CLIENT_ID")


dp_base = os.getenv("DIR_SUBJ_DATA") # to .env add  DIR_SUBJ_DATA='/Volumes/LXS/test_sessions/'
list_dns = os.listdir(dp_base)
list_dns = [l for l in list_dns if l[0]=="2"]
list_dns = [l for l in list_dns if os.path.isfile(os.path.join(dp_base, l, 'current.mp4'))]
list_dns.sort(reverse=True)
list_dns = list_dns[0:10]
dn = user_choice(list_dns, sort=False, suggestion=list_dns[0])

dp_session = f'{dp_base}/{dn}'
fp_chat_analysis = os.path.join(dp_session, "chat_analysis.yaml")
dict_meta = load_yaml(fp_chat_analysis)
name_video = dn[0:13]
fp_movie = os.path.join(dp_session, "current.mp4")

v = vimeo.VimeoClient(
    token=ACCESS_TOKEN,
    key=CLIENT_ID,
    secret=SECRET
)
# Make the request to the server for the "/me" endpoint.
about_me = v.get('/me')

# Make sure we got back a successful response.
assert about_me.status_code == 200

print("STARTING VIMEO UPLOAD")
video_uri = v.upload(
    fp_movie,
    data={'name': name_video, 'description': 'latent_space1', 'chunk_size': 512 * 1024}#, 'privacy':{'view':'anybody', 'embed':'public'}}
)

video_id = video_uri.split("/")[-1] 
video_url = "https://vimeo.com/{}".format(video_id)
print("DONE VIMEO UPLOAD. URL:")
print(video_url)



