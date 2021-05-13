import numpy as np
import scipy.signal as sig
from scipy.fft import fft, fftfreq


def sample_syn(x,sample_rate,alpha,beta):
    n = np.argmax(abs(fft(x)))
    size = fft(x).size

    fo = fftfreq(size,1/sample_rate)[n]
    To = 1/fo
    segments = int(np.floor(len(x)/To))

    y = np.zeros(np.ceil(len(x)*alpha))
    endgr = 0
    t = To
    while(endgr < len(y)):
        for i in range(segments):
            segment = x[To*i: To*i + 2*To]
            for j in range(t,len(y)):
                if abs((alpha*To*(i+1))-j) < t:
                    t = abs((alpha * To * (i + 1)) - j)
            # que pasa si t-To < 0
            out =  np.multiply(segment, np.hanning(2*To+1))
            endgr = t+To
            t += To/beta
            y[t-To:t+To]=out #overlapping










