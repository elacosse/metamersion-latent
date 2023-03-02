#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("../../../latentblending/")
sys.path.append("../audio")
from latent_blending import LatentBlending
from utils import interpolate_spherical, interpolate_linear, add_frames_linear_interp, yml_load, yml_save
from movie_util import concatenate_movies
from stable_diffusion_holder import StableDiffusionHolder
from tts import assemble_tts_for_video

import time
import zmq
import numpy as np
from threading import Thread
import json
import uuid
import random
from pydub import AudioSegment
import librosa
import os
import requests
from huggingface_hub import hf_hub_download



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




def download_music():
    filename = "Silence.mp3"
    url_base_folder = "http://andregoncalves.info/LatentSpace/"
    wav_base_folder= "/home/ubuntu/wavs"
    success = download_file(filename, url_base_folder, wav_base_folder)

    set_tags = [] #first comes the description, then the id_set
    set_tags.append(["Orchestral", 1])
    set_tags.append(["Mirage__RhodesMirage", 2])
    set_tags.append(["Lx2_2", 3])     
    set_tags.append(["Lx1_1", 4])     
    set_tags.append(["LX3_2", 5])     
    set_tags.append(["BraidsCuts", 6])     
    set_tags.append(["Waldorf", 7])     
    set_tags.append(["SynthyHarp", 8])     
    set_tags.append(["synthLeads", 9])     
    set_tags.append(["SynthPad", 10])     
    set_tags.append(["SynthyDrone", 11])     
    set_tags.append(["Braga_Synthy", 12])     
    set_tags.append(["Sunshine", 13])     
    set_tags.append(["Barcelos", 14])     

    list_downloads = []
    for x in set_tags:
        descrip = x[0]
        id_set = x[1]
        for i in range(1, 100):
                filename = f"{descrip}_{i}.mp3"
                dn_remote = f"Set{id_set}"
                dn_local = f"set{id_set}"
                success = download_file(filename, url_base_folder+"/"+dn_remote, wav_base_folder+"/"+dn_local)
                if not success:
                    break
                else: 
                    list_downloads.append(filename)

    print(f"All Downloads completed. Had to download {len(list_downloads)} files.")


def generate_soundtrack(fp_mp3, ChosenSet):
    print("Chosen Set is {}".format(ChosenSet))

    #Number of files per set
    SetFiles = [17, 17, 7, 12, 10, 8, 6, 6, 8, 7, 12, 12, 21, 29]

    #Load chosen set
    for i in range(18):
      if i == ChosenSet:
        if i == 1: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set1/Orchestral_{i}.mp3") for i in range(1, 18)]
        if i == 2: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set2/Mirage__RhodesMirage_{i}.mp3") for i in range(1, 18)]
        if i == 3: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set3/Lx2_2_{i}.mp3") for i in range(1, 8)]
        if i == 4: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set4/Lx1_1_{i}.mp3") for i in range(1, 13)]
        if i == 5: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set5/LX3_2_{i}.mp3") for i in range(1, 11)]
        if i == 6: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set6/BraidsCuts_{i}.mp3") for i in range(1, 9)]
        if i == 7: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set7/Waldorf_{i}.mp3") for i in range(1, 7)]
        if i == 8: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set8/SynthyHarp_{i}.mp3") for i in range(1, 7)]
        if i == 9: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set9/synthLeads_{i}.mp3") for i in range(1, 9)]
        if i == 10: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set10/SynthPad_{i}.mp3") for i in range(1, 8)]
        if i == 11: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set11/SynthyDrone_{i}.mp3") for i in range(1, 13)]
        if i == 12: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set12/Braga_Synthy_{i}.mp3") for i in range(1, 13)]
        if i == 13: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set13/Sunshine_{i}.mp3") for i in range(1, 22)]
        if i == 14: files = [AudioSegment.from_mp3(f"/home/ubuntu/wavs/set14/Barcelos_{i}.mp3") for i in range(1, 30)]


    # Create a list to hold the snippet samples
    samples = []
    # wav file with 90 seconds of silence to be the mix placeholder
    silence = AudioSegment.from_mp3(file = "/home/ubuntu/wavs/Silence.mp3")
     
    # Randomly iterate through files 15 times, randomly select a 15-30 second sample, and append it to the samples list
    files_used = []
    for i in range(17):
        which_file = random.randint(0, SetFiles[ChosenSet-1]-1)
        files_used.append(which_file)
        #print("Files used: {}".format(which_file))
        length = random.randint(15, 30) 
        #start_time = random.randint(0, len(files[which_file]) - length * 1000)
        start_time = random.randint(0, int(len(files[which_file])/1000 - length)) *1000
        samples.append(files[which_file][start_time:start_time + length * 1000])
    print("Files used: {}".format(files_used))


    # Apply a random fade-in and fade-out to each sample
    for i, sample in enumerate(samples):
        samples[i] = sample.fade_in(random.randint(1000, 8000)).fade_out(random.randint(5000, 10000))

    # Create an "empty" audio file to hold the mixed samples
    mixed = silence

    # Iterate through the samples, randomly adjust start position, pan, volume and add them to the mixed file
    sample_lengths = []
    n = 0
    for sample in samples:
        sample_lengths.append(sample.duration_seconds)
        pan = random.uniform(-0.8, 0.8)
        volume_change = random.uniform(-18, 0)
        max_position = int((len(silence) - len(sample))/1000)
        #start_position = random.randint(0, 700)/1000.0 # need to correct bug to fade out before 90seconds
        start_position = random.randint(0, max_position ) 
        if n  < 3 : start_position=0
        if n >= 15 : start_position = max_position 
        n+=1
        #mixed = mixed.overlay(sample.pan(pan).apply_gain(volume_change), position=start_position*len(mixed))
        mixed = mixed.overlay(sample.pan(pan).apply_gain(volume_change), position=start_position*1000)

    print(f"Sample lengths: {sample_lengths}")


    # Save the mixed file
    mixed.export(fp_mp3, format="mp3")
    print(f"Mixed audio length: {mixed.duration_seconds} seconds")
    print("")


def download_file(filename, url_folder, local_folder):
    r"""Downloads a file from a url to a local folder.

    Args:
        filename (str): Name of the file to download.
        url_folder (str): Url of the folder containing the file.
        local_folder (str): Local folder to download the file to.
    """

    # Check if folder dp_target exists. make otherwise
    if not os.path.isdir(local_folder):
        os.makedirs(local_folder)
    url = f"{url_folder}/{filename}"
    fp_target = os.path.join(local_folder, filename)

    # Check if file exists
    if os.path.isfile(fp_target):
        print(f"Already on disk: {fp_target}")
        return True


    # Check if url exists
    response = requests.head(url)
    if response.status_code != 200:
        print(f"File could not be downloaded: {url} = {response.status_code}")
        return False

    if os.path.isfile(fp_target):
        print(f"Downloaded: {url}")
        return True
    else:
        return False
    



# LATENT BLENDING
fp_ckpt = hf_hub_download(repo_id="stabilityai/stable-diffusion-2-1", filename="v2-1_768-ema-pruned.ckpt")
fp_config = "../../../latentblending/configs/v2-inference-v.yaml"
sdh = StableDiffusionHolder(fp_ckpt, fp_config)
lb = LatentBlending(sdh)

list_prompts = ["painting of a super nice house", "painting of a hell landscape, terrible"]
neg_prompt = ""
width = 768
height = 768
duration_single_trans = 10
depth_strength = 0.5
t_compute_max_allowed = 45 # seconds per segment
code_subject = 'STARTX'

lb.set_width(width)
lb.set_height(height)

fps = 30

# Specify a list of prompts below
list_prompts = [l for l in list_prompts if len(l) > 10]
print(f"found {len(list_prompts)} prompts. generating movie now")

# You can optionally specify the seeds
name_video = "test_video.mp4"
fp_movie = f"{name_video}"

list_movie_parts = []
for i in range(len(list_prompts) - 1):
    # For a multi transition we can save some computation time and recycle the latents
    if i == 0:
        lb.set_prompt1(list_prompts[i])
        lb.set_prompt2(list_prompts[i + 1])
        recycle_img1 = False
    else:
        lb.swap_forward()
        lb.set_prompt2(list_prompts[i + 1])
        recycle_img1 = True

    fp_movie_part = f"tmp_part_{str(i).zfill(3)}.mp4"
    # Run latent blending
    lb.run_transition(
        depth_strength=depth_strength,
        t_compute_max_allowed=t_compute_max_allowed)

    # Save movie
    lb.write_movie_transition(fp_movie_part, duration_single_trans)
    list_movie_parts.append(fp_movie_part)

# Finally, concatente the result
concatenate_movies(fp_movie, list_movie_parts)


# lb.run_multi_transition(
#         fp_movie, 
#         list_prompts, 
#         list_seeds=None, 
#         fps=fps, 
#         duration_single_trans=duration_single_trans
#     )







# VOICE TEST
narration_list = []
narration_list.append("hello hello")
narration_list.append("oh hello again")
silence_begin = 3
transition_duration = 10
start_times = list(np.arange(0,transition_duration*len(narration_list),transition_duration)+silence_begin)

# segment_duration = generate_tts_audio_from_list_onsets(narration_list, start_times, audio_duration, tts_model, speaker_indx, fp_voice)
preset = "fast"
voice = "train_dreams"
devices = ["cuda:0"]
audio_duration = (len(list_prompts)+1)*duration_single_trans
fp_voice = "/home/ubuntu/test_voice.wav"
assemble_tts_for_video(narration_list, audio_duration, start_times, fp_voice, preset, voice, devices)





# SOUND TEST
download_music()
ChosenSet = random.randint(1, 14) 
generate_soundtrack("/home/ubuntu/test_music.mp3", ChosenSet)




