import os
import wave

import numpy as np
from TTS.api import TTS


def generate_tts_audio_from_list_onsets(
    narration_list, start_times, total_length, tts_model, speaker_indx, output_file
):
    """Generate audio from a list of conversation strings using a TTS model.
    Args:
        narration_list (list): List of narration strings.
        tts_model (str): Name of TTS model.
        speaker_indx (int): idx speker
        output_path (str): Path to output file.
    Returns:
        list: List of paths to generated audio files.
    """
    output_path = "/tmp/"
    generate_tts_audio_from_list(narration_list, tts_model, speaker_indx, output_path)
    filepaths = os.listdir(output_path)
    filepaths = [l for l in filepaths if "narration_seg" in l]
    filepaths.sort()
    filepaths = filepaths[0 : len(narration_list)]
    filepaths = [os.path.join(output_path, l) for l in filepaths]
    segment_duration = [audio_length(l) for l in filepaths]
    assemble_audio_files_with_silence_and_save(
        filepaths, total_length, start_times, output_file
    )
    print("DONE!")
    return segment_duration


def generate_tts_audio_from_list(
    narration_list, tts_model, speaker_indx, output_path, length_scale=1.0
):
    """Generate audio from a list of conversation strings using a TTS model.
    Args:
        narration_list (list): List of narration strings.
        tts_model (str): Name of TTS model.
        output_path (str): Path to output file.
    Returns:
        list: List of paths to generated audio files.
    """
    # Initialize the TTS model
    tts = TTS(tts_model)
    tts.synthesizer.tts_model.length_scale = length_scale
    filepaths = []
    # get directory of output_path
    output_path = os.path.dirname(output_path)
    # Generate audio for each conversation string
    for i, narration in enumerate(narration_list):
        wav = tts.tts(narration, speaker=tts.speakers[speaker_indx])
        filepath = os.path.join(output_path, f"narration_seg_{i}.wav")
        tts.synthesizer.save_wav(wav=wav, path=filepath)
        filepaths.append(filepath)
    return filepaths


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
    with wave.open(filepaths[0], "rb") as audio_file:
        # Get the audio parameters
        sample_rate = audio_file.getframerate()
        sample_width = audio_file.getsampwidth()
        channels = audio_file.getnchannels()
    # Create audio_data
    audio_data = np.zeros(int(sample_rate * audio_duration), np.int16)
    # Iterate through the audio files
    for i, file_path in enumerate(filepaths):
        # Open the next audio file
        with wave.open(file_path, "rb") as next_audio_file:
            # Check that the audio parameters match
            assert next_audio_file.getframerate() == sample_rate
            assert next_audio_file.getsampwidth() == sample_width
            assert next_audio_file.getnchannels() == channels
            # Get the audio data
            next_audio_data = np.frombuffer(next_audio_file.readframes(-1), np.int16)
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
    # Open the output file for writing
    with wave.open(output_filepath, "wb") as output_audio_file:
        # Set the audio parameters
        output_audio_file.setframerate(sample_rate)
        output_audio_file.setsampwidth(sample_width)
        output_audio_file.setnchannels(channels)
        # Write the audio data to the output file
        output_audio_file.writeframes(audio_data.tobytes())

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


def assemble_tts_for_video(
    narration_list: list,
    transition_duration: float,
    start_times: list,
    output_filepath: str,
    tts_model: str,
    speaker_indx: int,
    length_scale: float = 1.0,
) -> None:
    """Assemble TTS audio files into a single audio file with silence between each file.
    Args:
        narration_list (list): List of narration strings.
        transition_duration (float): Duration of video segments (fixed)
        start_times (list): List of start times for each transition.
        output_filepath (str): Path to output file.
    """
    MAX_CHAR_LENGTH = 220
    # Get length of narrations and truncate if too long
    new_narration_list = []
    for i, narration in enumerate(narration_list):
        while len(narration) > MAX_CHAR_LENGTH:
            # Get rid of the last sentence assuming formatting with \n
            narration = narration[: narration.rfind("\n") + 1]
        new_narration_list.append(narration)

    segment_filepaths = generate_tts_audio_from_list(
        new_narration_list,
        tts_model,
        speaker_indx,
        os.path.dirname(output_filepath),
        length_scale,
    )
    audio_duration = transition_duration * len(start_times)
    assemble_audio_files_with_silence_and_save(
        segment_filepaths, audio_duration, start_times, output_filepath
    )


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
    transition_duration = 10
    start_times = list(
        np.arange(0, transition_duration * len(narration_list), transition_duration)
        + silence_begin
    )
    tts_model = "tts_models/en/vctk/vits"
    speaker_indx = 0
    output_file = "/tmp/test.wav"

    generate_tts_audio_from_list_onsets(
        narration_list, start_times, tts_model, 0, output_file
    )

    text = ""
    # get rid of last sentence in text
    text = text[: text.rfind(".") + 1]

    """
    COMMENT:
    the reason why this function will be nontrivial are the overlaps.
    if say the first segment is longer than 15s, what happens? 
    it will suck and it could always happen, especially when the content is llm gen.
    proposed solutions would be to check the length of each segment BEFORE concating
    and if it is too long, we need to re-run a shorter version of the segment
    """
