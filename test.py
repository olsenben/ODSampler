import soundfile as sf
import numpy as np
import sounddevice as sd
# Load audio file
audio_data, sample_rate = sf.read(r"C:\Users\benol\Documents\GitHub\ODSampler\Trimmed_Audio.wav")

# Determine number of channels correctly
num_channels = 1 if audio_data.ndim == 1 else audio_data.shape[1]

audio_data = audio_data.reshape(-1, 1)

# Print for debugging
print(f"Sample rate: {sample_rate}, Channels: {num_channels}, Data shape: {audio_data.shape}")

def normalize_audio(audio_data):
    max_val = np.max(np.abs(audio_data))

    if max_val > 0:
        return audio_data / max_val
    return audio_data

data = normalize_audio(audio_data)


def callback(outdata, frames, time, status):
    global start
    chunksize = min(len(data) - start, frames)
    outdata[:chunksize] = data[start:start + chunksize]
    if chunksize < frames:
        outdata[chunksize:] = 0
        raise sd.CallbackStop()
    start += chunksize

filename = r"C:\Users\benol\Documents\GitHub\ODSampler\Trimmed_Audio.wav" # Replace with your audio file

try:
    data, fs = sf.read(filename, dtype='float32')
    print(data.shape, fs)
    start = 0
    with sd.OutputStream(samplerate=fs, channels=data.shape[1] if len(data.shape) > 1 else 1, callback=callback, blocksize=1024) as stream:
        stream.start() # Ensure the stream is started before the loop
        while start < len(data):
            pass
except sf.SoundFileError:
    print(f"Error: Could not open or read file '{filename}'. Please make sure the file exists and is a valid audio file.")
except sd.PortAudioError as e:
    print(f"Error: An error occurred with the audio device: {e}")
except Exception as e:
     print(f"An unexpected error occurred: {e}")
stream.start()