from scipy import signal
import random as rand
from src.synth_tools import *


def add_guitar_body(xin, body_name):
    body_impulse = open_impulse_response(body_name)
    return signal.convolve(xin, body_impulse)


def KS_string(A, f, duration, sampling_rate):
    p = int((sampling_rate/f)-0.5)
    x = [rand.gauss(0, 1)*A for _ in range(p)]

    for n2 in range(p + 1, int(duration * sampling_rate)):
        x.append(0.5 * (x[n2 - p] + x[n2 - p - 1]))

    maxX = max(x)
    x = [x_i / maxX for x_i in x]

    return add_guitar_body(x[p:], "collins_IR")


def KS_drum(A, f, duration, sampling_rate):
    p = int((sampling_rate/f)-0.5)
    x = []
    for n in range(p):
        x.append(rand.gauss(0,1)*A)

    for n2 in range(p+1, int(duration*sampling_rate)):
        d = rand.uniform(0,1)
        if d < 0.5:
            x.append(0.5*(x[n2-p]+x[n2-p-1]))
        else:
            x.append(-0.5 * (x[n2 - p] + x[n2 - p - 1]))

    maxX = max(x)
    for i in range(len(x)):
        x[i] = x[i]/maxX
    return x[p:]



def add_synth_instrument(harmonic_a, f0, harmonic_freq, duration, sample_rate, A, D, S, R):
    t = np.linspace(0, 1 / f0, int(sample_rate / f0))
    duration = duration + (1 - R[1])*duration
    N = int(duration * f0)
    sine_o = np.zeros(int(sample_rate * 1 / f0))
    for i in range(len(harmonic_freq)):
        sine_o = np.add(sine_o, harmonic_a[i] * np.sin(2 * np.pi * harmonic_freq[i] * t))
    sine_o = sine_o / max(sine_o)
    sine_out = []
    for i in range(N):
        sine_out = sine_out + list(sine_o)
    t2 = np.linspace(0, len(sine_out)/sample_rate, len(sine_out))
    env = np.array([adsr_envelope(A, D, S, R, len(sine_out)/sample_rate, ti) for ti in t2])
    return np.multiply(sine_out, env)


def add_synthesis(instrument, a, f, duration, sampling_rate):
    source = ""
    if instrument == "guitar":
        source = "Ensoniq-ClassicGuitar"
    elif instrument == "bass":
        source = "Korg-Bass"
    elif instrument == "violin":
        source = "Alesis-Violin"
    elif instrument == "sax":
        source = "Alesis-SopranoSax"
    elif instrument == "french-horn":
        source = "Ensoniq-FrenchHorn"
    elif instrument == "organ":
        source = "Casio-Organ"
    elif instrument == "epiano":
        source = "Casio-EPiano"

    ADSR, ampsNfreqs = open_additive_instrument(source)
    A = ADSR[0]
    D = ADSR[1]
    S = ADSR[2]
    R = ADSR[3]
    freqs = ampsNfreqs[1]
    amps = ampsNfreqs[0]
    for i, fr in enumerate(freqs):
        freqs[i] = f * (fr + 0.01*rand.gauss(0,1))
    for i, am in enumerate(amps):
        amps[i] = a * am

    return add_synth_instrument(amps, f, freqs, duration, sampling_rate, A, D, S, R)


def add_synth_epiano(a, f, duration, sampling_rate):
    return add_synthesis("epiano", a, f, duration, sampling_rate)


def add_synth_organ(a, f, duration, sampling_rate):
    return add_synthesis("organ", a, f, duration, sampling_rate)


def add_synth_bass(a, f, duration, sampling_rate):
    return add_synthesis("bass", a, f, duration, sampling_rate)


def add_synth_violin(a, f, duration, sampling_rate):
    return add_synthesis("violin", a, f, duration, sampling_rate)


def add_synth_horn(a, f, duration, sampling_rate):
    return add_synthesis("french-horn", a, f, duration, sampling_rate)


def add_synth_sax(a, f, duration, sampling_rate):
    return add_synthesis("sax", a, f, duration, sampling_rate)


def add_synth_guitar(a, f, duration, sampling_rate):
    return add_synthesis("guitar", a, f, duration, sampling_rate)