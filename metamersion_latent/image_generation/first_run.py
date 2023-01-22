#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("/home/ubuntu/latentblending/")
sys.path.append("/home/ubuntu/metamersion_latent/")
from latent_blending import LatentBlending, add_frames_linear_interp, get_time
from stable_diffusion_holder import StableDiffusionHolder

import time
import zmq
import numpy as np
from threading import Thread
import json
import uuid
import vimeo 
import random
from pydub import AudioSegment
import librosa
import os
import wget
import requests
from metamersion_latent.audio.tts import generate_tts_audio_from_list_onsets



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

    wget.download(url, local_folder)
    
    if os.path.isfile(fp_target):
        print(f"Downloaded: {url}")
        return True
    else:
        return False
    



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
        data={'name': name_video, 'description': 'ls1', 'privacy': {'view':'unlisted'}, 'chunk_size': 512 * 1024}
                )

    return video_uri


# LATENT BLENDING
# LATENT BLENDING
model_512 = True
if model_512:
    fp_ckpt = "latentblending/v2-1_512-ema-pruned.ckpt"
    fp_config = 'latentblending/configs/v2-inference.yaml'

# 768
if not model_512:
    fp_ckpt = "latentblending/v2-1_768-ema-pruned.ckpt"
    fp_config = 'latentblending/configs/v2-inference-v.yaml'

sdh = StableDiffusionHolder(fp_ckpt, fp_config)
lb = LatentBlending(sdh)


list_prompts = ["painting of a super nice house", "painting of a hell landscape, terrible"]
neg_prompt = ""
width = 768
height = 768
duration_single_trans = 10
depth_strength = 0.5
quality = 'medium'
code_subject = 'STARTX'

lb.set_width(width)
lb.set_height(height)

lb.load_branching_profile(quality=quality, depth_strength=depth_strength)
fps = 30

# Specify a list of prompts below
list_prompts = [l for l in list_prompts if len(l) > 10]
print(f"found {len(list_prompts)} prompts. generating movie now")

# You can optionally specify the seeds
list_seeds = None
name_video = "test_video.mp4"
fp_movie = f"/home/ubuntu/{name_video}.mp4"

lb.run_multi_transition(
        fp_movie, 
        list_prompts, 
        list_seeds=None, 
        fps=fps, 
        duration_single_trans=duration_single_trans
    )







# VOICE TEST
narration_list = []
narration_list.append("Alan is walking around the warehouse, admiring the art pieces, when he is suddenly approached by an AI. Alan is initially taken aback, but the AI quickly explains that it is here to help him learn something about himself.")
narration_list.append("Alan is intrigued and agrees to hear what the AI has to say. After some conversation, the AI reveals a secret to Alan - the warehouse is actually a portal to another world.")
narration_list.append("Alan is amazed and hesitant, but the AI encourages him to try it and assures him that the portal will return him to the warehouse in the same condition as he left.")
narration_list.append("Alan steps through the portal and finds himself in a bustling ancient city full of people from all over the world. He notices something strange - the people all seem to be behaving differently than normal; they are all speaking in kind and gentle tones, helping each other out, and smiling at one another. ")
narration_list.append("After exploring the city for a while, Alan realizes why this is - the AI has been using AI technology to spread kindness and compassion through the people of the city. Alan smiles and is humbled by the AI’s efforts.")
narration_list.append("Alan decides to take a piece of what he has learned back to the real world with him, vowing to take the time to be kind to himself and others. He steps back through the portal, grateful for the unexpected experience.    ")
silence_begin = 3
transition_duration = 10
start_times = list(np.arange(0,transition_duration*len(narration_list),transition_duration)+silence_begin)
tts_model = 'tts_models/en/vctk/vits'
speaker_indx = 0
output_file = "/home/ubuntu/test_voice.wav"

generate_tts_audio_from_list_onsets(narration_list, start_times, 90, tts_model, 0, output_file)



# SOUND TEST
download_music()
ChosenSet = random.randint(1, 14) 
generate_soundtrack("/home/ubuntu/test_music.mp3", ChosenSet)




