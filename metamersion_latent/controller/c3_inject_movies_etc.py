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



#%% SCP to windows computer
load_dotenv(find_dotenv(), verbose=False) 
dp_base = os.getenv("DIR_SUBJ_DATA") # to .env add  DIR_SUBJ_DATA='/Volumes/LXS/test_sessions/'
list_dns = os.listdir(dp_base)
list_dns = [l for l in list_dns if l[0]=="2"]
list_dns = [l for l in list_dns if os.path.isfile(os.path.join(dp_base, l, 'current.mp4'))]
list_dns.sort(reverse=True)
dn = user_choice(list_dns, sort=False, suggestion=list_dns[0])
dp_session = f'{dp_base}/{dn}'


# THIS AINT WORKING
# files_copy_win = ['current.mp4', 'current.mp3']

# print("STARTING UPLOAD TO VR WINDOWS COMPUTER...")
# for fn in files_copy_win:
#     fp = os.path.join(dp_session, fn)
#     scp_cmd = f"scp {fp} CCU-VROOM-WIN10@192.168.50.254:/C:/media/"
#     # subprocess.call(scp_cmd, shell=True)
fp = os.path.join(dp_session, 'current.mp*')
scp_cmd = f"scp {fp} CCU-VROOM-WIN10@192.168.50.254:/C:/media/"
print("RUN THE FOLLOWING COMMAND:\n")
print(scp_cmd)

print("\nCOMPLETED UPLOAD TO VR WINDOWS COMPUTER.")
print("If this doesnt work: start the openssh server on windows")
