import pyaudio
import wave
import numpy as np
import time

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "/home/paradox/file.wav"

audio = pyaudio.PyAudio()
frames = []


def callback(in_data, frame_count, time_info, status):
    global frames
    data = np.zeros(frame_count * 2).tostring()
    frames.append(in_data)
    # data = wf.readframes(frame_count)
    return data, pyaudio.paContinue


# start Recording

stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

print("recording...")

time.sleep(5)
print("finished recording")

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
print("Frame length",len(frames))
waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()
