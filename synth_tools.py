import numpy as np
from scipy import signal, special, integrate, fft
import wave as WAV


def upload_impulse_response(origin_filename, impulse_name):
    # Read file to get buffer
    ifile = WAV.open(origin_filename)
    samples = ifile.getnframes()
    audio = ifile.readframes(samples)
    ifile.close()
    # Convert buffer to float32 using NumPy
    audio_as_np_int16 = np.frombuffer(audio, dtype=np.int16)
    audio_as_np_float32 = audio_as_np_int16.astype(np.float32)

    # Normalise float32 array so that values are between -1.0 and +1.0
    max_int16 = 2 ** 15
    audio_normalised = audio_as_np_float32 / max_int16
    impulse_name = "impulse_responses\\" + impulse_name + ".txt"
    f = open(impulse_name, "w+")
    for val in audio_normalised:
        f.write(str(val) + "\n")
    f.close()


def open_impulse_response(impulse_name):
    impulse_name = "impulse_responses\\" + impulse_name + ".txt"
    f = open(impulse_name, "r")
    data = f.readlines()
    f.close()
    values = []
    for line in data:
        values.append(float(line))
    return values


