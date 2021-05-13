import numpy as np
import scipy.signal as signal
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import wave as WAV
from src.synth_tools import *


def psola(x, alpha, beta, To, peak):
    segments = int(np.floor(len(x) / To))
    Lout = alpha * len(x)
    y = np.zeros(int(np.floor(Lout)))

    tk = To + peak
    while tk < Lout:
        k = abs((alpha * (peak + To) - tk))
        t = To + peak
        for j in range(2, segments - 1):
            if abs((alpha * ((To * j) + peak)) - tk) < k:
                t = (To * j) + peak
                k = (alpha * ((To * j) + peak)) - tk
        t = int(np.floor(t))
        gr = np.multiply(x[t - To:t + To + 1], np.hanning(2 * To + 1))
        if To + tk < Lout:
            y[tk - To:tk + To + 1] = np.add(y[tk - To:tk + To + 1], gr)
        tk += int(np.floor(To / beta))
    return y


def sample_syn(a, f, d, s):
    sample = frequency_selection(f)
    sample = os.path.dirname(os.path.abspath(__file__)) + "\\" + sample
    filename = sample + "_Analysis.txt"
    analysis = open(filename, "r")

    l = analysis.readline()
    To = int(l[0:len(l) - 1])
    l = analysis.readline()
    fo = float(l[0:len(l) - 1])
    l = analysis.readline()
    peak = int(l[0:len(l) - 1])
    l = analysis.readline()
    sampling_rate = float(l[0:len(l) - 1])

    filename = sample + "_Data.txt"
    x = np.loadtxt(filename)

    audio_duration = len(x) / sampling_rate
    alpha = d / audio_duration

    beta = f / fo

    y = psola(x, alpha, beta, To, peak)
    y = y / max(y)
    y = a * y

    t = np.linspace(0, d, len(y))
    envelope = [adsr_envelope(np.loadtxt(sample + "_A"), np.loadtxt(sample + "_D"), np.loadtxt(sample + "_S"),
                              np.loadtxt(sample + "_R"), d, ti) for ti in t]
    y = np.multiply(envelope, y)
    return y


def frequency_selection(f):
    if f > 300:
        sample = "Trumpet_C4"
    if f < 150:
        sample = "Trumpet_C3"
    else:
        sample = "Trumpet_C5"

    return sample
