import os
import wave

import numpy as np
from TTS.api import TTS


def generate_tts_audio_from_list(narration_list, tts_model, speaker_indx, output_path):
    """Generate audio from a list of conversation strings using a TTS model.
    Args:
        narration_list (list): List of narration strings.
        tts_model (str): Name of TTS model.
        output_path (str): Path to output file.
    """
    # Initialize the TTS model
    tts = TTS(tts_model)
    # Generate audio for each conversation string
    for i, narration in enumerate(narration_list):
        wav = tts.tts(narration, speaker=tts.speakers[speaker_indx])
        filepath = os.path.join(output_path, f"narration_seg_{i}.wav")
        tts.synthesizer.save_wav(wav=wav, path=filepath)


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


def assemble_audio_files(file_paths, silence_duration, output_filepath):
    """Assemble audio files into a single audio file with silence between each file.
    Args:
        file_paths (list): List of paths to audio files.
        silence_duration (float): Duration of silence between audio files.
        output_filepath (str): Path to output file.
    """
    # Open the first audio file
    with wave.open(file_paths[0], "rb") as audio_file:
        # Get the audio parameters
        sample_rate = audio_file.getframerate()
        sample_width = audio_file.getsampwidth()
        channels = audio_file.getnchannels()
        # Create a numpy array to hold the audio data
        audio_data = np.frombuffer(audio_file.readframes(-1), np.int16)
        # Iterate through the remaining audio files
        for file_path in file_paths[1:]:
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
        output_audio_file.writeframes(
            audio_data.tobytes()
        )  # Write the audio data to the output file
        output_audio_file.writeframes(audio_data.tobytes())
        output_audio_file.writeframes(audio_data.tobytes())
