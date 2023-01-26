import math

# import threading
import multiprocessing
import os
import wave

import numpy as np
import soundfile as sf
import torchaudio
from pydub import AudioSegment  # got that anyway from andre
from tortoise.utils.audio import load_voice

from metamersion_latent.audio.my_tortoise import TextToSpeech


def resample_wav(filepath, new_filepath, sr=44100):
    from scipy.io import wavfile
    from scipy.signal import resample
    # Open the wav file using the wave module
    with wave.open(filepath, "rb") as wav_file:
        # Get the current sample rate of the wav file
        current_rate = wav_file.getframerate()
        
        data = wavfile.read(filepath)[1]
        
        # Resample the wav file to 44.1kHz using the scipy.signal.resample function
        resampled_data = resample(data, int(data.shape[0] * sr / current_rate))
        wavfile.write(new_filepath, sr, resampled_data)


def create_tts_from_text(
    text: str, output_path: str, voice: str, preset="fast", device: str = "cuda:0"
) -> None:
    """Generate audio from text using a TTS model.
    Args:
        text (str): Text to generate audio from.
        output_path (str): Path to output file.
        voice (str): Name of TTS voice.
        preset (str): TTS preset.
        device (str): Device to use for TTS.
    """
    tts = TextToSpeech(device=device)
    voice_samples, conditioning_latents = load_voice(voice)
    gen = tts.tts_with_preset(
        text,
        voice_samples=voice_samples,
        conditioning_latents=conditioning_latents,
        preset=preset,
    )
    data = gen.squeeze(0).cpu()
    torchaudio.save(output_path, data, 24000, format="wav")


def assemble_tts_for_video(
    narration_list: list,
    audio_duration: float,
    start_times: list,
    output_filepath: str,
    preset: str,
    voice: str,
    devices: list,
) -> None:
    """Assemble TTS audio files into a single audio file with silence between each file.
    Args:
        narration_list (list): List of narration strings.
        audio_duration (float): length of total audio clip
        start_times (list): List of start times for each transition.
        output_filepath (str): Path to output file.
        preset (str): Quality of TTS audio.
        voice (str): Voice of speaker.
        devices (list): List of cuda devices to use for TTS.
    """

    output_dir = os.path.dirname(output_filepath)
    segment_filepaths = [
        os.path.join(output_dir, f"segment{i}.wav") for i in range(len(narration_list))
    ]

    if len(devices) > 1:
        narration_stack = narration_list.copy()
        i = 0
        process_list = []
        while len(narration_stack) > 0:
            text_segment = narration_stack.pop()
            device = devices[i % len(devices)]
            process = multiprocessing.Process(target=create_tts_from_text,args=(text_segment, segment_filepaths[i], voice, preset, device,))
            # thread = threading.Thread(target=create_tts_from_text,args=(text_segment, segment_filepaths[i], voice, preset, device,))
            process.start()
            process_list.append(process)
            if len(process_list) == len(devices):
                for process in process_list:
                    process.join()
                process_list = []
            i += 1
    else:
        for i, narration in enumerate(narration_list):
            create_tts_from_text(narration, segment_filepaths[i], voice, preset, devices[0])
    
    assemble_audio_files_with_silence_and_save(
        segment_filepaths, audio_duration, start_times, output_filepath
    )
    # check if too long
    check_tts_output_concatenation_and_clip(output_filepath, audio_duration)
    # convert to mp3 44.1khz 2 channels
    sound = AudioSegment.from_wav(output_filepath)
    sound = sound.set_channels(2)
    sound = sound.set_frame_rate(44100)
    sound = sound.set_sample_width(2)
    sound.export(output_filepath.replace(".wav", ".mp3"), format="mp3")


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

    # Assert that audio_data is approximately equal to audio_duration
    assert math.isclose(len(audio_data) / sample_rate, audio_duration, rel_tol=0.1)

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
        # Check that the end time is not greater than the length of the audio_data array
        if (end_time_indx <= len(audio_data)) and (
            (end_time_indx - start_time_indx) == len(next_audio_data)
        ):
            # Insert the audio data into the audio_data array
            audio_data[start_time_indx:end_time_indx] = next_audio_data

    sf.write(output_filepath, audio_data, sample_rate)
    return list_onsets, list_durations


def check_tts_output_concatenation_and_clip(
    filepath: str, audio_duration: float
) -> None:
    """Clips wav file if necessary to given length because of madness..."""
    data, sample_rate = sf.read(filepath, dtype="float32")
    if len(data) * sample_rate > audio_duration:
        # clip!
        end_indx = audio_duration * sample_rate
        data = data[:end_indx]
        sf.write(filepath, data, sample_rate)


if __name__ == "__main__":

    from metamersion_latent.utils import load_yaml

    analysis = load_yaml("metamersion_latent/examples/analysis/Caligula.yaml")
    narration_list = analysis["narration_list"]
    config_path = analysis["config_path"]
    from metamersion_latent.llm.config import Config

    config = Config.fromfile(config_path)

    segment_duration = 25  # seconds
    start_after = 3  # seconds after beginning of segment
    fade_in_segment = 15  # seconds
    fade_out_segment = 15  # seconds
    n_segments = len(narration_list)
    start_times = [
        fade_in_segment + start_after + (i * segment_duration)
        for i in range(n_segments)
    ]
    audio_duration = (
        fade_in_segment + fade_out_segment + (n_segments * segment_duration)
    )
    import time
    t0 = time.time()
    preset = "fast"
    voice = "train_dreams"
    num_gpus = 1
    devices = [f"cuda:{i}" for i in range(num_gpus)]
    fp_voice = "res1.wav"
    # assemble_tts_for_video(
    #     narration_list, audio_duration, start_times, fp_voice, preset, voice, devices
    # )
    t1 = time.time()
    print("TIME") # multi - 170.02198219299316, 526.7729606628418
    print(t1 - t0)    print("TIME") # multi - 170.02198219299316, 526.7729606628418
    print(t1 - t0)