import numpy as np
from scipy import signal, special, integrate, fft
import random as rand
import synth_tools as st


def add_guitar_body(xin, body_name):
    body_impulse = st.open_impulse_response(body_name)
    return signal.convolve(xin, body_impulse)


def KS_string(A, f, duration, sampling_rate):
    p = int((sampling_rate/f)-0.5)
    x = []
    for n in range(p):
        x.append(rand.gauss(0, 1)*A)

    for n2 in range(p+1, int(duration*sampling_rate)):
        x.append(0.5*(x[n2-p]+x[n2-p-1]))

    maxX = max(x)
    for i in range(len(x)):
        x[i] = x[i]/maxX
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

