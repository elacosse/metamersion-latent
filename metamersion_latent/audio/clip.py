import wave


def clip_wav_file(file_name, a, b, new_file_name):
    # Open the original wav file
    with wave.open(file_name, "rb") as original_file:
        # Get the number of frames in the original file
        num_frames = original_file.getnframes()
        # Convert a and b from minutes and seconds to frames
        a_frames = (
            a[0] * 60 * original_file.getframerate()
            + a[1] * original_file.getframerate()
        )
        b_frames = (
            b[0] * 60 * original_file.getframerate()
            + b[1] * original_file.getframerate()
        )
        # Make sure a and b are within the range of the original file
        if (
            a_frames < 0
            or a_frames >= num_frames
            or b_frames < 0
            or b_frames >= num_frames
        ):
            raise ValueError("Invalid time range")
        # Create a new wav file with the same parameters as the original file
        with wave.open(new_file_name, "wb") as new_file:
            new_file.setparams(original_file.getparams())

            # Read the frames from the original file between a and b
            original_file.setpos(a_frames)
            frames = original_file.readframes(b_frames - a_frames)
            # Write the frames to the new file
            new_file.writeframes(frames)


# Example usage:
clip_wav_file("resampled_watts.wav", (0, 45), (0, 57), "sample_1.wav")
clip_wav_file("resampled_watts.wav", (0, 33), (0, 41), "sample_2.wav")
clip_wav_file("resampled_watts.wav", (7, 33), (7, 43), "sample_3.wav")
clip_wav_file("resampled_watts.wav", (1, 21), (1, 32), "sample_4.wav")
clip_wav_file("resampled_watts.wav", (1, 32), (1, 49), "sample_5.wav")
clip_wav_file("resampled_watts.wav", (2, 33), (2, 40), "sample_5.wav")
