#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("../../../latentblending/")
sys.path.append("../audio")
from latent_blending import LatentBlending
from utils import interpolate_spherical, interpolate_linear, add_frames_linear_interp, yml_load, yml_save, get_time
from movie_util import concatenate_movies, MovieSaver
from stable_diffusion_holder import StableDiffusionHolder
from tts import assemble_tts_for_video

import time
import numpy as np
import json
import uuid
import random
import requests
from pydub import AudioSegment

import os
import subprocess
import yaml

import glob
import pydub
import wget  # pip install wget
from huggingface_hub import hf_hub_download


def txt_save(fp_txt, list_blabla, append=False):
    if append:
        mode = "a+"
    else:
        mode = "w"
    with open(fp_txt, mode) as fa:
        for item in list_blabla:
            fa.write("%s\n" % item)


def add_sound(fp_final, fp_silentmovie, fp_sound):
    cmd = f'ffmpeg -i {fp_silentmovie} -i {fp_sound} -c copy -map 0:v:0 -map 1:a:0 {fp_final}'
    subprocess.call(cmd, shell=True)
    if os.path.isfile(fp_final):
        print(f"add_sound: success! Watch here: {fp_final}")

def download_music():
    filename = "Silence.mp3"
    url_base_folder = "http://andregoncalves.info/LatentSpace/"
    wav_base_folder= "wavs"
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
    
    list_sets = [d for d in glob.glob('wavs/**') if os.path.isdir(d)]
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
    silence = AudioSegment.from_mp3(file = "wavs/Silence.mp3")
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
        if i == 1: files = [AudioSegment.from_mp3(f"wavs/set1/Orchestral_{i}.mp3") for i in range(1, 18)]
        if i == 2: files = [AudioSegment.from_mp3(f"wavs/set2/Mirage__RhodesMirage_{i}.mp3") for i in range(1, 18)]
        if i == 3: files = [AudioSegment.from_mp3(f"wavs/set3/Lx2_2_{i}.mp3") for i in range(1, 8)]
        if i == 4: files = [AudioSegment.from_mp3(f"wavs/set4/Lx1_1_{i}.mp3") for i in range(1, 13)]
        if i == 5: files = [AudioSegment.from_mp3(f"wavs/set5/LX3_2_{i}.mp3") for i in range(1, 11)]
        if i == 6: files = [AudioSegment.from_mp3(f"wavs/set6/BraidsCuts_{i}.mp3") for i in range(1, 9)]
        if i == 7: files = [AudioSegment.from_mp3(f"wavs/set7/Waldorf_{i}.mp3") for i in range(1, 7)]
        if i == 8: files = [AudioSegment.from_mp3(f"wavs/set8/SynthyHarp_{i}.mp3") for i in range(1, 7)]
        if i == 9: files = [AudioSegment.from_mp3(f"wavs/set9/synthLeads_{i}.mp3") for i in range(1, 9)]
        if i == 10: files = [AudioSegment.from_mp3(f"wavs/set10/SynthPad_{i}.mp3") for i in range(1, 8)]
        if i == 11: files = [AudioSegment.from_mp3(f"wavs/set11/SynthyDrone_{i}.mp3") for i in range(1, 13)]
        if i == 12: files = [AudioSegment.from_mp3(f"wavs/set12/Braga_Synthy_{i}.mp3") for i in range(1, 13)]
        if i == 13: files = [AudioSegment.from_mp3(f"wavs/set13/Sunshine_{i}.mp3") for i in range(1, 22)]
        if i == 14: files = [AudioSegment.from_mp3(f"wavs/set14/Barcelos_{i}.mp3") for i in range(1, 30)]


    # Create a list to hold the snippet samples
    samples = []
    # wav file with 90 seconds of silence to be the mix placeholder
    silence = AudioSegment.from_mp3(file = "wavs/Silence.mp3")
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

def safe_dict_read(dict_stuff, key_load, default_value):
    if key_load in dict_stuff.keys():
        return dict_stuff[key_load]
    else:
        print(f"WARNING safe_dict_read: did not find {key_load}")
        return default_value
    

def load_yaml(filepath):
    with open(filepath, "r") as f:
        items = yaml.safe_load(f)
    return items

# SOUND TEST
# download_music()





# %% IMPORTANT PARAMETERS
fp_chat_analysis = "/tmp/chat_analysis.yaml"
name_base = f"video_{get_time('second')}"
dp_subj = f"{name_base}" # prepend here, e.g. "/mnt/ls1_data/redbitches/"
t_compute_max_allowed = 45 # how much compute time (waiting time!) we grant each segment. 

# less important ones
width = 1280
height = 768
duration_single_trans = 20
depth_strength = 0.3

# %% inits load chat analysis. 

fp_ckpt = hf_hub_download(repo_id="stabilityai/stable-diffusion-2-1", filename="v2-1_768-ema-pruned.ckpt")
fp_config = "../../../latentblending/configs/v2-inference-v.yaml"
sdh = StableDiffusionHolder(fp_ckpt, fp_config)
lb = LatentBlending(sdh)
neg_prompt = ""
depth_strength = 0.5

lb.set_width(width)
lb.set_height(height)


dict_meta = load_yaml(fp_chat_analysis)

os.makedirs(dp_subj, exist_ok=True)

fp_movie = f"{dp_subj}/current_nofading.mp4"
fp_movie_wfading = f"{dp_subj}/current_nosound.mp4"
fp_movie_fadein = f"{dp_subj}/tmp_fadein.mp4"
fp_movie_fadeout = f"{dp_subj}/tmp_fadeout.mp4"
fp_voice = f"{dp_subj}/voice.wav"
fp_music = f"{dp_subj}/music.mp3"
fp_mixed = f"{dp_subj}/current.mp3"
fp_final = f"{dp_subj}/current.mp4"
fp_yml = f"{dp_subj}/info.txt"

# %% VIDEO
list_prompts = safe_dict_read(dict_meta, 'list_prompts', 6*["painting of the moon"])
list_prompts = [l for l in list_prompts if len(l) > 10]
neg_prompt = safe_dict_read(dict_meta, 'neg_prompt', "")
fps = 30

seed = safe_dict_read(dict_meta, 'seed', 420)
duration_fade = safe_dict_read(dict_meta, 'duration_fade', 10)
if seed is None:
    list_seeds = len(list_prompts)*[np.random.randint(999999999999)]
else:
    list_seeds = len(list_prompts)*[seed]

# DEFINE SOME STUFF...
audio_duration = len(list_prompts)*duration_single_trans + 2*duration_fade


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


# %% MUSIC
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

# %% MIX MUSIC AND VOICE
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

# %% Latent blendig movie
print("STARTING LATENT BLENDING...")
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
    
    if i == 0:
        multi_transition_img_first = lb.tree_final_imgs[0]
    elif i == len(list_prompts) - 2:
        multi_transition_img_last = lb.tree_final_imgs[-1]
        

# Finally, concatente the result
concatenate_movies(fp_movie, list_movie_parts)

# %% FADING TO AND FROM BLACK

print("STARTING FADING...")
    # Fading: black -> first image in the beginning, last_image -> black in the end

nmb_frames_fade = int(duration_fade * fps)
img_first = multi_transition_img_first
img_last = multi_transition_img_last
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
    img_mix = interpolate_linear(img_last, img_last, fract)
    ms.write_frame(img_mix)
ms.finalize()

# Concatente
concatenate_movies(fp_movie_wfading, [fp_movie_fadein, fp_movie, fp_movie_fadeout])

# add sound!
add_sound(fp_final, fp_movie_wfading, fp_mixed)

print(f"ALL GOOD! CHECK IT OUT: {fp_final}")