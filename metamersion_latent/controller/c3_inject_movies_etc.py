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
from dotenv import find_dotenv, load_dotenv
import os
import subprocess
import shutil
import ftplib
import vimeo #pip3 uninstall PyVimeo - if also https://stackoverflow.com/questions/44031471/importerror-cannot-import-name-urlencode-when-trying-to-install-flask-ext-sto
import requests

#%% SCP to windows computer
load_dotenv(find_dotenv(), verbose=False) 
dp_base = os.getenv("DIR_SUBJ_DATA") # to .env add  DIR_SUBJ_DATA='/Volumes/LXS/test_sessions/'
list_dns = os.listdir(dp_base)
list_dns = [l for l in list_dns if l[0]=="2"]
list_dns = [l for l in list_dns if os.path.isfile(os.path.join(dp_base, l, 'current.mp4'))]
list_dns = [l for l in list_dns if not os.path.isfile(os.path.join(dp_base, l, 'injected.txt'))]
list_dns.sort(reverse=True)
list_dns = list_dns[0:10]
dn = user_choice(list_dns, sort=False, suggestion=list_dns[0])

dp_session = f'{dp_base}/{dn}'
fp_chat_analysis = os.path.join(dp_session, "chat_analysis.yaml")


def txt_save(fp_txt, list_blabla, append=False):
    if append:
        mode = "a+"
    else:
        mode = "w"
    with open(fp_txt, mode) as fa:
        for item in list_blabla:
            fa.write("%s\n" % item)


def get_time(resolution=None):
    if resolution is None:
        resolution = "second"
    if resolution == "day":
        t = time.strftime("%y%m%d", time.localtime())
    elif resolution == "minute":
        t = time.strftime("%y%m%d_%H%M", time.localtime())
    elif resolution == "second":
        t = time.strftime("%y%m%d_%H%M%S", time.localtime())
    elif resolution == "millisecond":
        t = time.strftime("%y%m%d_%H%M%S", time.localtime())
        t += "_"
        t += str("{:03d}".format(int(int(datetime.utcnow().strftime("%f")) / 1000)))
    else:
        raise ValueError("bad resolution provided: %s" % resolution)
    return t


#%%

# OCTI part
try:
	dp_top_projection = os.path.join(dp_session, "top_projection")
	os.makedirs(dp_top_projection, exist_ok=True)

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
	p.wait()
	p = subprocess.Popen(['scp', fp_chat_analysis, 'pi@'+host+':/home/pi/LS1'], cwd=dp_top_projection)
	p.wait()
except Exception as e:
	print(f"Bad Octi / Johannes: {e}")
    

# SEND OVER TO WINDOWS VR PC
print("STARTING FTP COPY TO VR PC...")
list_transfer = ['current.mp4', 'current.mp3']
session = ftplib.FTP('192.168.50.254','vr','vr420')
for fn in list_transfer:
    fp = os.path.join(dp_session, fn)
    file = open(fp,'rb')
    session.storbinary(f'STOR {fn}', file)     
    file.close()    
session.quit()    
    
fp_txt = os.path.join(dp_session, "injected.txt")
txt_save(fp_txt, [f"injected at {get_time('second')}"])

print("ALL COPIED SUCCESSFULLY!")

# VIMEO UPLOAD
print("STARTING VIMEO UPLOAD")
load_dotenv(find_dotenv(), verbose=False) 

ACCESS_TOKEN = os.getenv("VIMEO_ACCESS_TOKEN")
SECRET = os.getenv("VIMEO_ACCESS_TOKEN")
CLIENT_ID = os.getenv("VIMEO_ACCESS_TOKEN")

v = vimeo.VimeoClient(
    token=ACCESS_TOKEN,
    key=CLIENT_ID,
    secret=SECRET
)

# Make the request to the server for the "/me" endpoint.
about_me = v.get('/me')

# Make sure we got back a successful response.
assert about_me.status_code == 200

fp_movie = os.path.join(dp_session, "current.mp4")
video_uri = v.upload(
    fp_movie,
    data={'name': dn[0:13], 'description': 'latent space 1', 'chunk_size': 512 * 1024, 'privacy':{'view':'anybody', 'embed':'public'}, "content_rating":["safe"]}
)

#%% verify
video_id = video_uri.split("/")[-1] 
video_url = "https://vimeo.com/{}".format(video_id)
while True:
    status_code = requests.get(video_url).status_code
    if status_code == 200:
        break
    else:
        time.sleep(10)
        
#%% 
import qrcode
import qrcode.image.svg
img = qrcode.make(video_url)

#, image_factory=qrcode.image.svg.SvgImage)
with open('qr.svg', 'wb') as qr:
    img.save(qr)




