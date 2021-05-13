import numpy as np
import scipy.signal as sig
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import wave as WAV


def psola(x):
    data = open("samplebased_analysis.txt", "r")
    l = data.readline()
    To = int(l[0:len(l) - 1])
    l = data.readline()
    alpha = float(l[0:len(l) - 1])
    l = data.readline()
    peak = int(l[0:len(l) - 1])
    l = data.readline()
    beta = float(l[0:len(l) - 1])

    segments = int(np.floor(len(x) / To))
    Lout = alpha * len(x)
    y = np.zeros(int(np.floor(Lout)))

    tk = To + peak
    while tk < Lout:
        k = abs((alpha * (peak+To) - tk))
        t = To + peak
        for j in range(2, segments - 1):
            if abs((alpha * ((To*j) + peak)) - tk) < k:
                t = (To * j) + peak
                k = (alpha * ((To *j)+peak)) - tk
        t = int(np.floor(t))
        gr = np.multiply(x[t - To:t + To + 1], np.hanning(2 * To + 1))
        if To + tk < Lout:
            y[tk - To:tk + To + 1] = np.add(y[tk - To:tk + To + 1], gr)
        tk += int(np.floor(To / beta))
    return y


def sample_syn_analysis(x, sampling_rate, alpha,f):
    N2 = len(x)
    audio_fft = 2.0 / N2 * np.abs(fft(x)[1:N2 // 2])
    freqs = fftfreq(N2, 1 / sampling_rate)[1:N2 // 2]
    n = np.argmax(audio_fft)
    fo = freqs[n]
    Ton = int(np.floor(sampling_rate / fo))
    peak = np.argmax(x[0:Ton])
    beta = f/(fo/sampling_rate)

    data = open("samplebased_analysis.txt", "w")
    data.write("%a" % Ton)
    data.write("\n")
    data.write("%a" % alpha)
    data.write("\n")
    data.write("%a" % peak)
    data.write("\n")
    data.write("%a" % beta)

def sample_syn(ins, f, a, d, sampling_rate):
    filename = ins + ".wav"
    ifile = WAV.open(filename)
    samples = ifile.getnframes()
    audio = ifile.readframes(samples)
    ifile.close()
    # Convert buffer to float32 using NumPy
    audio_as_np_int16 = np.frombuffer(audio, dtype=np.int16)
    audio_as_np_float32 = audio_as_np_int16.astype(np.float32)
    # Normalise float32 array so that values are between -1.0 and +1.0
    max_int16 = 2 ** 15
    audio_normalised = audio_as_np_float32 / max_int16
    #está harcodeado
    audio_normalised = audio_normalised[25000:30000]
    plt.plot(audio_normalised)
    audio_duration = len(audio_normalised) / sampling_rate
    #calculo de alpha
    alpha = d / audio_duration

    sample_syn_analysis(audio_normalised, sampling_rate, alpha, f)

    y = psola(audio_normalised)

    #amplitud
    y = y / max(y)
    y = a * y
    return y
