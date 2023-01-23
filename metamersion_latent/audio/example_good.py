#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 17:22:48 2023

@author: lunar
"""
# import sys
# sys.path.append("/home/lunar/git/metamersion_latent")
import numpy as np
import soundfile as sf

from metamersion_latent.audio.tts import assemble_tts_for_video


def assemble_audio_files_with_silence_and_save(
    filepaths,
    audio_duration,
    start_times,
    output_filepath,
):
    """Assemble audio files into a single audio file with silence between each file.
    Args:
        file_paths (list): List of paths to audio files.
        audio_duration (float): Duration of audio in seconds.
        start_times (list): List of start times for each audio file.
        output_filepath (str): Path to output file.
    """
    list_onsets = []
    list_durations = []

    # Open the first audio file

    data, sample_rate = sf.read(filepaths[0], dtype="float32")
    audio_data = np.zeros(int(sample_rate * audio_duration), np.float32)

    for i, file_path in enumerate(filepaths):
        next_audio_data, sample_rate = sf.read(filepaths[i], dtype="float32")
        # Get the start time
        start_time_indx = int(sample_rate * start_times[i])
        list_onsets.append(start_time_indx / sample_rate)
        # Get the end time
        end_time_indx = start_time_indx + len(next_audio_data)
        list_durations.append((end_time_indx - start_time_indx) / sample_rate)
        # make sure they are same length
        if end_time_indx - start_time_indx != len(next_audio_data):
            next_audio_data = next_audio_data[: end_time_indx - start_time_indx]
        # Insert the audio data into the audio_data array
        print(end_time_indx - start_time_indx, len(next_audio_data))
        audio_data[start_time_indx:end_time_indx] = next_audio_data

    sf.write(output_filepath, audio_data, sample_rate)
    return list_onsets, list_durations


duration_single_trans = 20
duration_fade = 20
silence_begin = 3
narration_list = []
narration_list.append("painting of a forest. it was like really beautiful and stuff")
narration_list.append("painting of a house. super nice house. really.")
narration_list.append("painting of a ocean. the ocean was very cold and blue.")


segment_duration = 30  # seconds
start_after = 3  # seconds after beginning of segment
fade_in_segment = 30  # seconds
fade_out_segment = 30  # seconds
n_segments = len(narration_list)
start_times = [
    fade_in_segment + start_after + i * segment_duration for i in range(n_segments)
]
audio_duration = fade_in_segment + fade_out_segment + n_segments * segment_duration
print(start_times, audio_duration)

preset = "fast"
voice = "train_dreams"
devices = ["cuda:0"]
fp_voice = "bubu.wav"

assemble_tts_for_video(
    narration_list, audio_duration, start_times, fp_voice, preset, voice, devices
)
