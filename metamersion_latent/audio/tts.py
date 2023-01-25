import math
import os

import numpy as np
import soundfile as sf
import torchaudio
from pydub import AudioSegment  # got that anyway from andre

# from metamersion_latent.audio.my_tortoise import TextToSpeech
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_voice


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
    # MAX_CHAR_LENGTH = 220
    # # Get length of narrations and truncate if too long
    # new_narration_list = []
    # for i, narration in enumerate(narration_list):
    #     while len(narration) > MAX_CHAR_LENGTH:
    #         # Get rid of the last sentence assuming formatting with \n
    #         narration = narration[: narration.rfind("\n") + 1]
    #     new_narration_list.append(narration)
    output_dir = os.path.dirname(output_filepath)
    segment_filepaths = [
        os.path.join(output_dir, f"segment{i}.wav") for i in range(len(narration_list))
    ]
    for i, narration in enumerate(narration_list):
        create_tts_from_text(narration, segment_filepaths[i], voice, preset, devices[0])

    # for i, narration_list in enumerate(narration_list):
    #     device = devices[i % len(devices)]
    #     thread_list.append(threading.Thread(target=create_tts_from_thread,args=(narration_list[0], segment_filepaths[0], voice, preset, device)))
    #     thread_list[-1].start()

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

    narration_list = []
    narration_list.append(
        "painting of a forest. it was like really beautiful and stuff"
    )
    narration_list.append("painting of a house. super nice house. really.")
    narration_list.append("painting of a ocean. the ocean was very cold and blue.")

    segment_duration = 30  # seconds
    start_after = 3  # seconds after beginning of segment
    fade_in_segment = 30  # seconds
    fade_out_segment = 30  # seconds
    n_segments = len(narration_list)
    start_times = [
        fade_in_segment + start_after + (i * segment_duration)
        for i in range(n_segments)
    ]
    audio_duration = (
        fade_in_segment + fade_out_segment + (n_segments * segment_duration)
    )
    print(start_times, audio_duration)

    preset = "fast"
    voice = "train_dreams"
    devices = ["cuda:0"]
    fp_voice = "bubu.wav"

    assemble_tts_for_video(
        narration_list, audio_duration, start_times, fp_voice, preset, voice, devices
    )
