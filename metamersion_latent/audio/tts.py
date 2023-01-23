import os
import wave

import numpy as np
import soundfile as sf
import torchaudio

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
    torchaudio.save(output_path, data, 24000)


def assemble_tts_for_video(
    narration_list: list,
    transition_duration: float,
    start_times: list,
    output_filepath: str,
    preset: str,
    voice: str,
    devices: list,
) -> None:
    """Assemble TTS audio files into a single audio file with silence between each file.
    Args:
        narration_list (list): List of narration strings.
        transition_duration (float): Duration of video segments (fixed)
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
    audio_duration = transition_duration * len(start_times)
    assemble_audio_files_with_silence_and_save(
        segment_filepaths, audio_duration, start_times, output_filepath
    )


def audio_length(file_path):
    """Get the length of an audio file in seconds.
    Args:
        file_path (str): Path to audio file.
    Returns:
        float: Length of audio file in seconds.
    """
    with wave.open(file_path, "r") as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()
    return frames / float(rate)


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
        audio_data[start_time_indx:end_time_indx] = next_audio_data

    sf.write(output_filepath, audio_data, sample_rate)
    return list_onsets, list_durations


def assemble_audio_files(filepaths, silence_duration, output_filepath):
    """Assemble audio files into a single audio file with silence between each file.
    Args:
        file_paths (list): List of paths to audio files.
        silence_duration (float): Duration of silence between audio files.
        output_filepath (str): Path to output file.
    """
    # Open the first audio file
    with wave.open(filepaths[0], "rb") as audio_file:
        # Get the audio parameters
        sample_rate = audio_file.getframerate()
        sample_width = audio_file.getsampwidth()
        channels = audio_file.getnchannels()
        # Create a numpy array to hold the audio data
        audio_data = np.frombuffer(audio_file.readframes(-1), np.int16)
        # Iterate through the remaining audio files
        for file_path in filepaths[1:]:
            # Open the next audio file
            with wave.open(file_path, "rb") as next_audio_file:
                # Check that the audio parameters match
                assert next_audio_file.getframerate() == sample_rate
                assert next_audio_file.getsampwidth() == sample_width
                assert next_audio_file.getnchannels() == channels
                # Read the audio data
                next_audio_data = np.frombuffer(
                    next_audio_file.readframes(-1), np.int16
                )
                # Create silence data
                silence_data = np.zeros(int(sample_rate * silence_duration), np.int16)
                # Concatenate the audio data and silence
                audio_data = np.concatenate((audio_data, silence_data, next_audio_data))
    # Open the output file for writing
    with wave.open(output_filepath, "wb") as output_audio_file:
        # Set the audio parameters
        output_audio_file.setframerate(sample_rate)
        output_audio_file.setsampwidth(sample_width)
        output_audio_file.setnchannels(channels)
        # Write the audio data to the output file
        output_audio_file.writeframes(audio_data.tobytes())


if __name__ == "__main__":

    # EXAMPLE OF WHAT WE HAVE NOW
    narration_list = []
    narration_list.append(
        "Alan is walking around the warehouse, admiring the art pieces, when he is suddenly approached by an AI. Alan is initially taken aback, but the AI quickly explains that it is here to help him learn something about himself."
    )
    narration_list.append(
        "Alan is intrigued and agrees to hear what the AI has to say. After some conversation, the AI reveals a secret to Alan - the warehouse is actually a portal to another world."
    )
    narration_list.append(
        "Alan is amazed and hesitant, but the AI encourages him to try it and assures him that the portal will return him to the warehouse in the same condition as he left."
    )
    narration_list.append(
        "Alan steps through the portal and finds himself in a bustling ancient city full of people from all over the world. He notices something strange - the people all seem to be behaving differently than normal; they are all speaking in kind and gentle tones, helping each other out, and smiling at one another. "
    )
    narration_list.append(
        "After exploring the city for a while, Alan realizes why this is - the AI has been using AI technology to spread kindness and compassion through the people of the city. Alan smiles and is humbled by the AI’s efforts."
    )
    narration_list.append(
        "Alan decides to take a piece of what he has learned back to the real world with him, vowing to take the time to be kind to himself and others. He steps back through the portal, grateful for the unexpected experience.    "
    )
    silence_begin = 3
    transition_duration = 20
    start_times = list(
        np.arange(0, transition_duration * len(narration_list), transition_duration)
        + silence_begin
    )
    output_file = "/tmp/test.wav"
    preset = "fast"
    voice = "train_dreams"
    devices = ["cuda:0"]
    assemble_tts_for_video(
        narration_list,
        transition_duration,
        start_times,
        output_file,
        preset,
        voice,
        devices,
    )
