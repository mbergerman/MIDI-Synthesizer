import mido
import numpy as np


def midinote2freq(n):
    A = 440  # Frecuencia de LA
    An = 69  # Valor correspondiente a LA440 en midi
    distance = abs(An - n)
    if n < An:
        return A * 2 ** (-distance / 12)
    else:
        return A * 2 ** (distance / 12)


def get_tempo(mid_):
    for msg in mid_:  # Search for tempo
        if msg.type == 'set_tempo':
            return msg.tempo


class midi_data:

    def __init__(self, filename_, sampleRate_=44100):
        self.filename = filename_
        self.num_of_tracks = 0
        self.midi_tracks = None
        self.mid = None
        self.wave_tracks = None
        self.sampleRate = sampleRate_
        self.duration = 0
        self.ticks_per_s = 0

    def midi_parse(self):
        self.mid = mido.MidiFile(self.filename, clip=True)
        num_of_tracks = len(self.mid.tracks)

        midi_tracks_dict = [[] for i in range(num_of_tracks)]
        self.midi_tracks = [[] for i in range(num_of_tracks)]

        # Put all note on/off in midinote as dictionary.
        for j, track in enumerate(self.mid.tracks):
            for i in track:
                if i.type == 'note_on' or i.type == 'note_off':
                    midi_tracks_dict[j].append(i.dict())
        # change time values from delta to relative time.
        for j, track in enumerate(midi_tracks_dict):
            time_data = 0.0
            for i in track:
                time = i['time'] + time_data
                i['time'] = time
                time_data = time
                # make every note_on with 0 velocity note_off
                if i['type'] == 'note_on' and i['velocity'] == 0:
                    i['type'] = 'note_off'
                # format is [type, note, time, velocity, channel]
                message_data = []
                if i['type'] == 'note_on' or i['type'] == 'note_off':
                    message_data.append(i['type'])
                    message_data.append(i['note'])
                    message_data.append(i['time'])
                    message_data.append(i['velocity'])
                    message_data.append(i['channel'])
                    self.midi_tracks[j].append(message_data)

        self.duration = self.mid.length  # Duration in seconds
        tempo = get_tempo(self.mid)  # Microseconds per beat
        tempo_s = tempo / 1e6  # Seconds per beat
        self.ticks_per_s = tempo_s / self.mid.ticks_per_beat
        self.wave_tracks = [np.zeros(int(self.sampleRate * self.duration)) for i in range(self.num_of_tracks)]

    def synthesize_track(self, track, function):

        for j, message_data in enumerate(self.midi_tracks[track]):
            if message_data[0] == 'note_on':
                A = message_data[3] / 100
                freq = midinote2freq(message_data[1])
                m = 1
                tick_start = message_data[2]
                while track[j + m][0] != 'note off' and track[j + m][1] != message_data[1]:
                    m += 1
                tick_end = track[j + m][2]
                delta_ticks = tick_end - tick_start
                wave = []
                for t in [n / self.sampleRate for n in range(int(self.sampleRate * delta_ticks * self.ticks_per_s))]:
                    wave.append(function(A, freq, t))
                n = int(self.sampleRate * tick_start * self.ticks_per_s)
                wave2 = np.array(
                    list(np.zeros(n)) + wave + list(np.zeros(len(self.wave_tracks[track]) - (n + len(wave)))))
                self.wave_tracks[track] = self.wave_tracks[track] + wave2