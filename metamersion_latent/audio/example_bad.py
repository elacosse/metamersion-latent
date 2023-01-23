#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 17:22:48 2023

@author: lunar
"""
# import sys
# sys.path.append("/home/lunar/git/metamersion_latent")
# from metamersion_latent.audio.tts import assemble_tts_for_video

import numpy as np

duration_single_trans=15
duration_fade = 20
silence_begin = -3
narration_list = []
narration_list.append("painting of a forest. it was like really beautiful and stuff")
narration_list.append("painting of a house. super nice house. really.")
narration_list.append("painting of a ocean. the ocean was very cold and blue")


audio_duration = (len(narration_list)+1)*duration_single_trans
offset = duration_fade
start_times = list(np.arange(0,duration_single_trans*len(narration_list),duration_single_trans)+silence_begin+offset)



preset = "fast"
voice = "train_dreams"
devices = ["cuda:0"]

fp_voice = "bubu.wav"
assemble_tts_for_video(narration_list, duration_single_trans, start_times, fp_voice, preset, voice, devices)
