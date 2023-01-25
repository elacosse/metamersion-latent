#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("/home/ubuntu/latentblending/")
sys.path.append("/home/ubuntu/metamersion_latent/")
from latent_blending import LatentBlending, add_frames_linear_interp, get_time, interpolate_linear
from movie_util import MovieSaver, concatenate_movies
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
from metamersion_latent.audio.tts import assemble_tts_for_video

import os
import wget
import requests
import subprocess
import yaml

import glob
import os
import pydub

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

def txt_save(fp_txt, list_blabla, append=False):
    if append:
        mode = "a+"
    else:
        mode = "w"
    with open(fp_txt, mode) as fa:
        for item in list_blabla:
            fa.write("%s\n" % item)




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


def yml_save(fp_yml, dict_stuff):
    """
    Helper function for saving yaml files
    """
    with open(fp_yml, 'w') as f:
        data = yaml.dump(dict_stuff, f, sort_keys=False, default_flow_style=False)
    print("yml_save: saved {}".format(fp_yml))



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

def segment_voice(audio_file, frame_rate=1000, thresh_vol=0.1, thresh_len_seconds=3.5):
    """Identify pauses in audio file, return array that is False at pause locations."""
    # Load file and convert to audio segemnt
    if type(audio_file) == str:
        if audio_file.lower().endswith('.mp3'):
            audio_segment =  AudioSegment.from_mp3(audio_file)
        elif audio_file.lower().endswith('.wav'):
            audio_segment =  AudioSegment.from_wav(audio_file)
        else:
            raise TypeError
    elif type(audio_file) == pydub.audio_segment.AudioSegment:
        audio_segment = audio_file
    else:
        raise TypeError
    
    # Convert to numpy array
    audio_segment = audio_segment.set_frame_rate(frame_rate)
    array_audio_segment = np.array(audio_segment.get_array_of_samples())
    list_array_channels = []
    nr_channels = audio_segment.channels
    for c in range(nr_channels):
      list_array_channels.append(array_audio_segment[c::nr_channels])
    array_channels = np.stack(list_array_channels, axis=1)
    array_audio_mean = array_channels.mean(axis=1)
    thresh_samples = thresh_len_seconds * frame_rate
    
    list_pauses = []
    list_pause_start = []
    list_pause_end = []
    list_pause_duration = []
    
    list_voice = []
    list_voice_start = []
    list_voice_end = []
    list_voice_duration = []
    
    # Detect pauses
    array_is_voice = np.ones_like(array_audio_mean)
    idx = 0
    
    while idx < len(array_audio_mean):
        if abs(array_audio_mean[idx]) <= thresh_vol:
            pause_start = idx
            while idx < len(array_audio_mean) and abs(array_audio_mean[idx]) <= thresh_vol: # missed the abs()!!
                idx += 1
            pause_end = idx
            voice_start = idx
            pause_duration = pause_end - pause_start
            if pause_duration >= thresh_samples:
                return_onsets = pause_start
                voice_end = idx
                voice_duration = voice_end - voice_start
                print(voice_start, voice_end, voice_duration)
                #print(pause_start, pause_end, pause_duration)
                print('***')
                list_pauses.append([pause_start, pause_end, pause_duration])
                list_pause_start.append(pause_start)
                list_pause_end.append(pause_end)
                list_pause_duration.append(pause_duration)
    
                array_is_voice[pause_start:pause_end] = False
        else:
            idx += 1

    list_voice = []
    list_voice_start = []
    list_voice_duration = []
    
    list_voice_start.append(list_pause_end[0])
    list_voice_duration.append(list_pause_start[1]-list_pause_end[0])
    list_voice_start.append(list_pause_end[1])
    list_voice_duration.append(list_pause_start[2]-list_pause_end[1])
    list_voice_start.append(list_pause_end[2])
    list_voice_duration.append(list_pause_start[3]-list_pause_end[2])
    list_voice_start.append(list_pause_end[3])
    list_voice_duration.append(list_pause_start[4]-list_pause_end[3])
    list_voice_start.append(list_pause_end[4])
    list_voice_duration.append(list_pause_start[5]-list_pause_end[4])
    list_voice_start.append(list_pause_end[5])
    #list_voice_duration.append(len(audio_file)-list_pause_end[5])
    list_voice_duration.append(list_pause_start[6]-list_pause_end[5])
    return list_voice_start, list_voice_duration#, array_is_voice


def generate_soundtrack_new(fp_music, fp_voice, soundtrack_duration=180, segments=5):
    
    length_earlyStop = 0 
    length_overlap_float = 0.8
    chosen_set = random.randint(1, 14) 
    chosen_set2 = random.randint(1, 14) 
    while chosen_set == chosen_set2 :
      chosen_set2 = random.randint(1, 14) 
    print(f"Chosen Set is {chosen_set} + {chosen_set2}")
    
    list_sets = [d for d in glob.glob('/home/ubuntu/wavs/**') if os.path.isdir(d)]
    list_sets = sorted(list_sets, key=lambda x:int(x.split('set')[-1]))
    list_files = [glob.glob(s + '/**') for s in list_sets]
    list_nr_files = [len(s) for s in list_files]
    
    # ONSETS & DURATIONS -> INCOMING LIST
    onsets_in = []
    duration_in = []
    #incoming_list = [[25,5],[53,5],[81,4],[105,6],[137,6]]
    #onsets_in = [x[0] for x in incoming_list]
    #duration_in = [x[1] for x in incoming_list]
    #on_times = [x + y for x, y in incoming_list]
    
    
    # IMPORT VOICE AND GET SILENCES LIST
    voice = AudioSegment.from_wav(file = fp_voice)
    incoming_list2 = segment_voice(voice)
    #print(incoming_list2)
    
    onsets_in = incoming_list2[0]
    duration_in = incoming_list2[1]
    onsets_in = [int(x / 1000) for x in onsets_in]
    duration_in = [int(x / 1000) for x in duration_in]
    print("onsets_in:", onsets_in)
    print("duration_in", duration_in)
    
    on_times = [x + y for x, y in zip(onsets_in, duration_in)]
    print("on_times:", on_times)
    #array_is_voice
    
    files = [AudioSegment.from_mp3(f) for f in list_files[chosen_set-1]]
    files2 = [AudioSegment.from_mp3(f) for f in list_files[chosen_set2-1]]
    
    # Create a list to hold the snippet samples
    samples = []
    # wav file with 90 seconds of silence to be the mix placeholder
    silence = AudioSegment.from_mp3(file = "/home/ubuntu/wavs/Silence.mp3")
    silence = silence*3
    
    # Cut the audio segment to a lower length (in milliseconds)
    silence = silence[0:soundtrack_duration*1000]
    print(f"Generating Track - Final length: {silence.duration_seconds} seconds")
    
    # Randomly iterate through files 15 times, randomly select a 15-30 second sample, and append it to the samples list
    files_used = []
    files_used2 = []
    
    iterate_n = segments * 6 + 6
    change_set_at = random.randint(2,4)
    print(f"CHANGE AT: {change_set_at}")
    
    for i in range(iterate_n):
        if i < 3 : length = onsets_in[0] + random.randint(0, int(duration_in[0]*length_overlap_float))
        elif i < 3 + segments: length = onsets_in[1]-on_times[0] + random.randint(length_earlyStop, int(duration_in[1]*length_overlap_float))
        elif i < 3 + segments*2: length = onsets_in[2]-on_times[1] + random.randint(length_earlyStop, int(duration_in[2]*length_overlap_float))
        elif i < 3 + segments*3: length = onsets_in[3]-on_times[2] + random.randint(length_earlyStop, int(duration_in[3]*length_overlap_float))
        elif i < 3 + segments*4: length = onsets_in[4]-on_times[3] + random.randint(length_earlyStop, int(duration_in[4]*length_overlap_float))
        elif i < 3 + segments*5: length = onsets_in[5]-on_times[4] + random.randint(length_earlyStop, int(duration_in[5]*length_overlap_float))
        else : length = soundtrack_duration - on_times[len(on_times)-1] #+ random.randint(-2, 0)
    
        if i < 3 + change_set_at*segments :
          which_file = random.randint(0, len(files)-1)
          files_used.append(which_file)
          start_time = random.randint(0, int(len(files[which_file])/1000 - length)) *1000
          samples.append(files[which_file][start_time:start_time + length * 1000])
        else :
          which_file = random.randint(0, len(files2)-1)
          files_used2.append(which_file)
          max_start = int(len(files2[which_file])/1000 - length)
          if max_start < 0 : max_start = 0
          start_time = random.randint(0, max_start) *1000
          samples.append(files2[which_file][start_time:start_time + length * 1000])
    print(f"Files used {len(files_used)}: {files_used}")
    print(f"Files used {len(files_used2)}: {files_used2}")
    
    
    # Apply a random fade-in and fade-out to each sample
    for i, sample in enumerate(samples):
        if i % 3 == 0 : samples[i] = sample.speedup(1+random.randint(0,5)/2) #speedup(seg, playback_speed=1.5, chunk_size=150, crossfade=25):
        samples[i] = sample.fade_in(random.randint(1000, 3500)).fade_out(random.randint(4000, 10000))
    
    # Create an "empty" audio file to hold the mixed samples
    mixed = silence
    
    # Iterate through the samples, randomly adjust start position, pan, volume and add them to the mixed file
    sample_lengths = []
    n = 0
    state=0;
    for sample in samples:
        sample_lengths.append(sample.duration_seconds)
        pan = random.uniform(-0.8, 0.8)
        volume_change = random.uniform(-14, -2)
    
        if n  < 3 : 
            start_position=0
        
        #
        elif 3 <= n < 3+segments: # BLOCK 1 
            #state = 0;
            start_position = on_times[state] + random.randint(0,2)
        elif 3+segments <= n < 3+segments*2 : # BLOCK 2
            state = 1;
            start_position = on_times[state] + random.randint(0,2)
        elif 3+segments*2 <= n < 3+segments*3 : # BLOCK 3
            state = 2;
            start_position = on_times[state] + random.randint(0,2)
        elif 3+segments*3 <= n < 3+segments*4 : # BLOCK 4
            state = 3;
            start_position = on_times[state] + random.randint(0,2)
            #print(f"{n} : STATE: {state} = {start_position}")  
        elif 3+segments*4 <= n < 3+segments*5 : # BLOCK 5
            state = 4;
            start_position = on_times[state] + random.randint(0,2)
            #print(f"{n} : STATE: {state} = {start_position}")
        elif 3+segments*5 <= n < 3+segments*6 : # BLOCK 6
            state = 5;
            start_position = on_times[state] + random.randint(0,0)
            #print(f"{n} : STATE: {state} = {start_position}")
        #
        elif n >= 3+segments*6 : # last 2 samples
            state = 6;
            max_position = int((len(silence) - len(sample))/1000)
            start_position = max_position 
            #print(f"{n} : STATE: {state} = {start_position}")
        else :
          print("ELSE")
          max_position = int((len(silence) - len(sample))/1000)
          start_position = random.randint(0, max_position) 
        n+=1
        mixed = mixed.overlay(sample.pan(pan).apply_gain(volume_change), position=start_position*1000)
    
    print(f"Sample lengths: {sample_lengths}")
    
    mixed = mixed.overlay(voice)
    
    # Save the mixed file
    mixed.export(fp_music, format="mp3")
    
    

def generate_soundtrack(fp_mp3, ChosenSet):
    print("Chosen Set is {}".format(ChosenSet))

    
    #Number of files per set
    SetFiles = [17, 17, 7, 12, 10, 8, 6, 6, 8, 7, 12, 12, 21, 29]

    # ONSETS & DURATIONS -> INCOMING LIST
    onsets_in = []
    duration_in = []
    incoming_list = [[5,7],[23,6],[41,8],[55,6],[77,4]]
    onsets_in = [x[0] for x in incoming_list]
    duration_in = [x[1] for x in incoming_list]
    on_times = [x + y for x, y in zip(onsets_in, duration_in)]

    print("onsets_in:", onsets_in)
    print("duration_in", duration_in)
    print("on_times:", on_times)



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
    silence = silence*3
     
    # Randomly iterate through files 15 times, randomly select a 15-30 second sample, and append it to the samples list
    files_used = []
    segments = 15
    finish = (90*3 - 5) / 4
    iterate_n = segments * 4 + 5

    for i in range(iterate_n):
        which_file = random.randint(0, SetFiles[ChosenSet-1]-1)
        files_used.append(which_file)
        #print("Files used: {}".format(which_file))
        length = random.randint(10, 25) 
        #start_time = random.randint(0, len(files[which_file]) - length * 1000)
        start_time = random.randint(0, int(len(files[which_file])/1000 - length)) *1000
        samples.append(files[which_file][start_time:start_time + length * 1000])
    print("Files used: {}".format(files_used))


    # Apply a random fade-in and fade-out to each sample
    for i, sample in enumerate(samples):
        samples[i] = sample.fade_in(random.randint(1000, 2500)).fade_out(random.randint(4000, 8000))

    # Create an "empty" audio file to hold the mixed samples
    mixed = silence

    # Iterate through the samples, randomly adjust start position, pan, volume and add them to the mixed file
    sample_lengths = []
    n = 0
    state=0;
    for sample in samples:
        sample_lengths.append(sample.duration_seconds)
        pan = random.uniform(-0.8, 0.8)
        volume_change = random.uniform(-18, 0)

        if n  < 3 : 
            start_position=0
            """
        elif 3 <= n < 3+segments: # 18 - 36
            #state = 0;
            start_position = on_times[state] + random.randint(-2,2)
        elif 3+segments <= n < 3+segments*2 : # 36 - 54
            state = 1;
            start_position = on_times[state] + random.randint(-2,2)
        elif 3+segments*2 <= n < 3+segments*3 : # 54 - 72
            state = 2;
            start_position = on_times[state] + random.randint(-2,2)
        elif 3+segments*3 <= n < 3+segments*4 : # 72 - 90
            state = 3;
            start_position = on_times[state] + random.randint(-2,2)
            """
        elif n >= 3+segments*4 : # last 2 samples
            state = 4;
            max_position = int((len(silence) - len(sample))/1000)
            start_position = max_position 
            #start_position = 0#random.randint(0, max_position ) 
        else :
          max_position = int((len(silence) - len(sample))/1000)
          start_position = random.randint(0, max_position) 
        n+=1
        mixed = mixed.overlay(sample.pan(pan).apply_gain(volume_change), position=start_position*1000)

    print(f"Sample lengths: {sample_lengths}")


    # Save the mixed file
    #mixed.export("mixed.wav", format="wav")



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
    


# SOUND TEST
download_music()
# ChosenSet = random.randint(1, 14) 
# generate_soundtrack("/home/ubuntu/test.mp3", ChosenSet)
# fp_voice = "/home/ubuntu/movies/230125_172619_NONAME/voice.wav"
# fp_music = "/home/ubuntu/music.mp3"
# generate_soundtrack_new(fp_music, fp_voice, soundtrack_duration=180, segments=5)

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

def safe_dict_read(dict_stuff, key_load, default_value):
    if key_load in dict_stuff.keys():
        return dict_stuff[key_load]
    else:
        print(f"WARNING safe_dict_read: did not find {key_load}")
        return default_value

# RUNS
server = Server(7555, 7556, image_dims=IMAGE_DIMS, verbose=True)


# Multi Movie Generation
print("STARTED SERVER... LISTENING")
while True:
    msg = server.get_last_request()
    if msg is None:
        time.sleep(0.1)
        continue
    try:
        dict_meta = msg['meta']
        if dict_meta['call']=='run_movie':
            print("GOT MESSAGE")
            # Output files
            code_subject = safe_dict_read(dict_meta, 'code_subject', 'NONAME')
            name_base = f"{get_time('second')}_{code_subject}"
            dp_subj = f"/home/ubuntu/movies/{name_base}"
            os.makedirs(dp_subj)

            server_ip = safe_dict_read(dict_meta, 'server_ip', 'IP NOT PROVIDED')

            fp_movie = f"{dp_subj}/current_nofading.mp4"
            fp_movie_wfading = f"{dp_subj}/current_nosound.mp4"
            fp_movie_fadein = f"{dp_subj}/tmp_fadein.mp4"
            fp_movie_fadeout = f"{dp_subj}/tmp_fadeout.mp4"
            fp_voice = f"{dp_subj}/voice.wav"
            fp_music = f"{dp_subj}/music.mp3"
            fp_mixed = f"{dp_subj}/current.mp3"
            fp_yml = f"{dp_subj}/info.txt"

            # VIDEO
            list_prompts = safe_dict_read(dict_meta, 'list_prompts', 6*["painting of the moon"])
            list_prompts = [l for l in list_prompts if len(l) > 10]
            neg_prompt = safe_dict_read(dict_meta, 'neg_prompt', "")

            width = int(safe_dict_read(dict_meta, 'width', 768))
            height = int(safe_dict_read(dict_meta, 'height', 768))
            duration_single_trans = safe_dict_read(dict_meta, 'duration_single_trans', 20)
            depth_strength = safe_dict_read(dict_meta, 'depth_strength', 0.5)
            quality = safe_dict_read(dict_meta, 'quality', 'medium')
            seed = safe_dict_read(dict_meta, 'seed', 420)
            duration_fade = safe_dict_read(dict_meta, 'duration_fade', 10)
            if seed is None:
                list_seeds = len(list_prompts)*[np.random.randint(999999999999)]
            else:
                list_seeds = len(list_prompts)*[seed]


            # DEFINE SOME STUFF...
            audio_duration = (len(list_prompts)+1)*duration_single_trans


            # VOICE
            print("GENERATING VOICE...")
            try:
                silence_begin = safe_dict_read(dict_meta, 'silence_begin', 1)
                speaker_indx = safe_dict_read(dict_meta, 'speaker_indx', 1)
                narration_list = safe_dict_read(dict_meta, 'narration_list', len(list_prompts)*["nothing to say"])
                tts_length_scale = safe_dict_read(dict_meta, 'tts_length_scale', 1.0)
                tts_model = 'tts_models/en/vctk/vits'
                
                offset = duration_fade
                start_times = list(np.arange(0,duration_single_trans*len(narration_list),duration_single_trans)+silence_begin+offset)
                print(f"audio_duration={audio_duration} start_times={start_times}")

                print("BEFORE STARTING TTS:")
                print(f"narration_list {narration_list}")
                print(f"duration_single_trans {duration_single_trans}")
                print(f"start_times {start_times}")
                print(f"tts_length_scale {tts_length_scale}")
                # segment_duration = generate_tts_audio_from_list_onsets(narration_list, start_times, audio_duration, tts_model, speaker_indx, fp_voice)
                preset = "fast"
                voice = "train_dreams"
                devices = ["cuda:0"]
                assemble_tts_for_video(narration_list, audio_duration, start_times, fp_voice, preset, voice, devices)

            except Exception as e:
                print(f"EXCEPTION! {e}")

            print("DONE GENERATING VOICE")


            # MUSIC
            print("GENERATING MUSIC...")
            
            try:
                if os.path.isfile(fp_voice):
                    generate_soundtrack_new(fp_music, fp_voice, soundtrack_duration=audio_duration, segments=len(list_prompts)-1)
                else:
                    ChosenSet = np.random.randint(1, 13)
                    if ChosenSet < 1 or ChosenSet > 14:
                        print("WARNING! BAD ChosenSet! FORCING ChosenSet=1")
                        ChosenSet=1
                    generate_soundtrack(fp_music, ChosenSet)

            except Exception as e:
                print(f"EXCEPTION! {e}")
            print("DONE GENERATING MUSIC")
            # txt_save(f"{dp_subj}/voice_segment_onsets.txt", start_times)
            # txt_save(f"{dp_subj}/voice_segment_duration.txt", segment_duration)

            # MIX MUSIC AND VOICE
            # Load the audio tracks
            print("GENERATING MIX...")
            try:
                x = AudioSegment.from_mp3(fp_music)
                y = AudioSegment.from_wav(fp_voice)
                # Mix the tracks together
                mix = y.overlay(x)
                # Export the mixed audio to a new file
                mix.export(fp_mixed, format="mp3")
            except Exception as e:
                print(f"EXCEPTION! {e}")
            print("DONE GENERATING MIX")

            print("STARTING LATENT BLENDING...")
            try:
                # Start latent blending
                lb.set_width(width)
                lb.set_height(height)

                lb.load_branching_profile(quality=quality, depth_strength=depth_strength)
                fps = 30
                
                print(f"found {len(list_prompts)} prompts. They are:")
                for prompt in list_prompts:
                    print(prompt)

                lb.run_multi_transition(
                        fp_movie, 
                        list_prompts, 
                        list_seeds=list_seeds, 
                        fps=fps, 
                        duration_single_trans=duration_single_trans
                    )
            except Exception as e:
                print(f"EXCEPTION! {e}")
            print("DONE LATENT BLENDING.")

            print("STARTING FADING...")
            try:
                # Fading: black -> first image in the beginning, last_image -> black in the end
                
                nmb_frames_fade = int(duration_fade * fps)
                img_first = lb.multi_transition_img_first
                img_last = lb.multi_transition_img_last
                img_black = np.zeros_like(img_first)

                # save fade in
                ms = MovieSaver(fp_movie_fadein, fps=fps)
                for fract in np.linspace(0,1,nmb_frames_fade):
                    img_mix = interpolate_linear(img_black, img_first, fract)
                    ms.write_frame(img_mix)
                ms.finalize()

                # save fade out
                ms = MovieSaver(fp_movie_fadeout, fps=fps)
                for fract in np.linspace(0,1,nmb_frames_fade):
                    img_mix = interpolate_linear(img_last, img_black, fract)
                    ms.write_frame(img_mix)
                ms.finalize()

                # Concatente
                concatenate_movies(fp_movie_wfading, [fp_movie_fadein, fp_movie, fp_movie_fadeout])
            except Exception as e:
                print(f"EXCEPTION! {e}")
            print("DONE FADING")

            print("START MERGING SOUND...")
            try:
               # Put sound to movie
                subprocess.run(['ffmpeg', '-i', f'{dp_subj}/current_nosound.mp4', '-i', f'{dp_subj}/current.mp3', '-c', 'copy', '-map', '0:v:0', '-map', '1:a:0', f'{dp_subj}/current.mp4'], cwd=dp_subj)
            except Exception as e:
                print(f"EXCEPTION! {e}")
            print("DONE MERGING SOUND")

            print("START SAVING INFO FILE...")
            try:
               # Put sound to movie
                yml_save(fp_yml, dict_meta)
            except Exception as e:
                print(f"EXCEPTION! {e}")
            print("DONE SAVING INFO FILE")



            print("ALL DONE! SENDING BACK SCP COMMANDS")
            # str_base = f"/home/ubuntu/movies/{name_base}"
            scp_cmd = f"scp -r ubuntu@{server_ip}:/{dp_subj} ."
            print(scp_cmd)

            meta = {}
            img = (255*np.random.rand(5, 5, 3)).astype(np.uint8)
            meta["dims"] = (img.shape[0], img.shape[1], 3)

            meta["code_sending"] = str(uuid.uuid4())[:5]
            meta["scp_cmd"] = scp_cmd
            server.publish_thread(meta, img)






        if msg['meta']['call']=='run_image':
            print("GOT MESSAGE")
            # Output files
            server_ip = msg['meta']['server_ip']  
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
            meta["code_sending"] = str(uuid.uuid4())[:5]
            server.publish_thread(meta, img)


    except Exception as e:
        print(f"EXCEPTION! {e}")





    

