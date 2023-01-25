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

# OCTI COPYING
try:
	dp_top_projection = os.path.join(dp_session, "top_projection")
	os.makedirs(dp_top_projection)

	fp_current = os.path.join(dp_session, 'current.mp4')
	fp_cropped = os.path.join(dp_top_projection, 'current_cropped.mp4')

	# first crop the video into half
	p = subprocess.Popen(['ffmpeg', '-i', fp_current, '-filter:v', 'crop=256:512:0:0', 'playback_crop.mp4'], cwd=dp_top_projection)

	# wait for the process to finish
	p.wait()

	# now create a mirror of the cropped video
	p = subprocess.Popen(['ffmpeg', '-i', 'playback_crop.mp4', '-vf', 'hflip', '-c:a', 'copy', 'playback_crop2.mp4'], cwd=dp_top_projection)

	# wait for the process to finish
	p.wait()

	# concatenate the two videos together
	# and call it "playback.mp4"
	p = subprocess.Popen(['ffmpeg', '-i', 'playback_crop.mp4', '-i', 'playback_crop2.mp4', '-filter_complex', '[0:v:0]pad=iw*2:ih[bg]; [bg][1:v:0]overlay=w', fp_cropped], cwd=dp_top_projection)

	# wait for the process to finish
	p.wait()

	# define the raspberrypi address:
	host = 'raspberrypi14.local'

	# upload the video to raspberrypi14 in the /home/pi/LS1 using scp
	p = subprocess.Popen(['scp', fp_cropped, 'pi@'+host+':/home/pi/LS1'], cwd=dp_top_projection)

	# wait for the process to finish
	p.wait()
except Exception as e:
	print(f"Bad Octi: {e}")

fp = os.path.join(dp_session, 'current.mp*')
scp_cmd = f"scp {fp} CCU-VROOM-WIN10@192.168.50.254:/C:/media/"
print("RUN THE FOLLOWING COMMAND:\n")
print(scp_cmd)
print("Hint: If this doesnt work: did you start openssh server on windows")
