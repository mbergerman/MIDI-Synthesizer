import numpy as np
from scipy import signal, special, integrate, fft
import wave as WAV
import os


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
    current_path = os.path.dirname(os.path.abspath(__file__))
    impulse_name = os.path.join(current_path, "resources", "impulse_responses", str(impulse_name) + ".txt")
    f = open(impulse_name, "w+")
    for val in audio_normalised:
        f.write(str(val) + "\n")
    f.close()


def open_impulse_response(impulse_name):
    current_path = os.path.dirname(os.path.abspath(__file__))
    impulse_name = os.path.join(current_path, "resources", "impulse_responses", str(impulse_name) + ".txt")
    f = open(impulse_name, "r")
    data = f.readlines()
    f.close()
    values = []
    for line in data:
        values.append(float(line))
    return values


def save_additive_instrument(origin_filename, file_sampling_rate, instrument_name):
    A, D, S, R = get_adsr(origin_filename, file_sampling_rate)
    amp, freq = get_partial(D[1], S[1], origin_filename, file_sampling_rate)

    current_path = os.path.dirname(os.path.abspath(__file__))
    ADSR_filename = os.path.join(current_path, "resources", "add_synth_instruments", str(instrument_name) + "ADSR.txt")
    partials_filename = os.path.join(current_path, "resources", "add_synth_instruments", str(instrument_name) + "partials.txt")

    f = open(ADSR_filename, "w+")
    f.write(str(A[0]) + "," + str(A[1]) + "\n")
    f.write(str(D[0]) + "," + str(D[1]) + "\n")
    f.write(str(S[0]) + "," + str(S[1]) + "\n")
    f.write(str(R[0]) + "," + str(R[1]) + "\n")
    f.close()

    f = open(partials_filename, "w+")
    for fr, a in zip(freq, amp):
        f.write(str(a) + "," + str(fr) + "\n")
    f.close()


def open_additive_instrument(instrument_name):
    current_path = os.path.dirname(os.path.abspath(__file__))
    ADSR_filename = os.path.join(current_path, "resources", "add_synth_instruments", str(instrument_name) + "ADSR.txt")
    partials_filename = os.path.join(current_path, "resources", "add_synth_instruments", str(instrument_name) + "partials.txt")

    f = open(ADSR_filename, "r")
    data = f.readlines()
    f.close()
    t = []
    a = []
    for line in data:
        t.append(float(line.split(",")[1]))
        a.append(float(line.split(",")[0]))
    A = [a[0], t[0]]
    D = [a[1], t[1]]
    S = [a[2], t[2]]
    R = [a[3], t[3]]

    f = open(partials_filename, "r")
    data = f.readlines()
    f.close()
    freqs = []
    amps = []
    for line in data:
        amps.append(float(line.split(",")[0]))
        freqs.append(float(line.split(",")[1]))

    return [A, D, S, R], [amps, freqs]


def get_partial(D, S, filename, sampling_rate):
    # Read file to get buffer
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
    N = len(audio_normalised)
    t1 = round(D * N)
    t2 = round(S * N)

    #tn = np.linspace(1.37, 1.6, t2-t1)

    #plt.plot(tn, audio_normalised[t1:t2])
    N2 = len(audio_normalised[t1:t2])
    audio_fft = 2.0 / N2 * np.abs(fft.fft(audio_normalised[t1:t2])[1:N2 // 2])
    freqs = fft.fftfreq(N2, 1 / sampling_rate)[1:N2 // 2]
    audio_fft = audio_fft / max(audio_fft)
    f0 = freqs[np.argmax(audio_fft)]
    peaks = signal.find_peaks(audio_fft, distance=np.argmax(audio_fft)//1.1, height=1e-3)

    peaks_freq = []
    saved_f=[]
    for p in peaks[0]:
        if freqs[p] <= f0:
            if np.isclose(f0/freqs[p], round(f0/freqs[p]), rtol = 1e-2):
                saved_f.append(p)
                peaks_freq.append(1/round(f0/freqs[p]))
        elif f0 < freqs[p] < 20e3 and round(freqs[p]/f0) <= 30:
            if np.isclose(freqs[p]/f0, round(freqs[p]/f0), rtol = 1e-1):
                saved_f.append(p)
                peaks_freq.append(round(freqs[p] / f0))

    peaks_val = [audio_fft[p] for p in saved_f]

    return peaks_val, peaks_freq


def get_adsr(filename, sampling_rate):
    # Read file to get buffer
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
    An = int(np.argmax(audio_normalised))
    N = len(audio_normalised)
    t = np.linspace(0, N/sampling_rate, N)
    audio_fft = 2.0 / N * np.abs(fft.fft(audio_normalised)[1:N // 2])
    freqs = fft.fftfreq(N, 1 / sampling_rate)[1:N // 2]
    audio_fft = audio_fft / max(audio_fft)
    f0 = freqs[np.argmax(audio_fft)]
    t0 = 1/f0
    peaks = signal.find_peaks(audio_normalised, distance= 2 * round(t0*sampling_rate), height=0.04)
    peaks_val = [audio_normalised[p] for p in peaks[0]]
    peaks_t = [t[p] for p in peaks[0]]

    peak_max_n = np.argmax(peaks_val)
    max_peak = peaks_val[int(peak_max_n)]
    Dn = 0
    Dni = 0
    for i in range(int(peak_max_n), len(peaks_val)):
        max_t = peaks_t[int(peak_max_n)]
        peak_i = peaks_val[i]
        peak_ip1 = peaks_val[i+1]
        peak_ip2 = peaks_val[i + 2]
        t_i = peaks_t[i]
        if abs(peak_ip1 - peak_ip2) < 0.1 and 0.4*max_peak < peak_i < 0.95*max_peak and max_t < t_i < 4*max_t:
            Dn = peaks[0][i]
            Dni = i
            break
    Sn = 0
    Sni = 0
    count = 0
    try:
        for i in range(Dni, len(peaks_val)):
            D_peak = peaks_val[Dni]
            peak_im1 = peaks_val[i-3]
            peak_i = peaks_val[i]
            peak_ip1 = peaks_val[i+1]
            delta_m = abs(peak_im1 - peak_i)
            delta_p = abs(peak_ip1 - peak_i)

            if delta_p > 0.1*abs(D_peak - peak_i) > delta_m and 0.4*max_peak > peak_i > 0.2*max_peak:
                count = count + 1
                if count == 3:
                    Sn = peaks[0][i]
                    Sni = i
                    break
    except:
        Sni = 0
        i = 0
        while Sni < Dni:
            Sni = np.where(peaks_val <= 0.7*peaks_val[Dni])[0][i]
            i += 1
        Sn = peaks[0][Sni]

    Rn = 0
    for i in range(Sni, len(peaks_val)):
        peak_i = peaks_val[i]
        max_peak = peaks_val[int(peak_max_n)]
        if peak_i < 0.05:
            Rn = peaks[0][i]
            break

    A = [1, An / N]
    D = [audio_normalised[Dn]/max(audio_normalised), Dn / N]
    S = [audio_normalised[Sn]/max(audio_normalised), Sn / N]
    R = [0, Rn / N]

    return A, D, S, R


def adsr_envelope(A, D, S, R, duration, t):
    At = A[1] * duration
    Dt = D[1] * duration
    St = S[1] * duration
    Rt = R[1] * duration
    out = np.array([])
    ta = np.array([ti for ti in t if ti <= At])
    td = np.array([ti for ti in t if At < ti <= Dt])
    ts = np.array([ti for ti in t if Dt < ti <= St])
    tr = np.array([ti for ti in t if St < ti])
    out = np.append(out, ta / At)
    out = np.append(out, ((D[0] - 1)/(Dt - At)) * (td - At) + 1)
    out = np.append(out, ((S[0] - D[0])/(St - Dt)) * (ts - Dt) + D[0])
    out = np.append(out, S[0]*np.exp(-(tr-St)/(abs(Rt-St))))
    return out