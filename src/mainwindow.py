# PyQt5 modules
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QInputDialog, QApplication, QWidget, QPushButton, QAction, QLineEdit, \
    QMessageBox
from PyQt5.QtCore import QCoreApplication, QObject, QRunnable, QThread, QThreadPool, pyqtSignal, pyqtSlot
from PyQt5 import uic, QtGui
from PyQt5.QtGui import QFont

# Project modules
from src.ui.mainwindow import Ui_MainWindow

# Python modules
import pyaudio
import time
import sys
import wave, struct
import matplotlib.pyplot as plt

from src.TrackItemWidget import *
from src.EffectItemWidget import *
from src.MidiData import *
from src.synthesizers import *
from src.SampleBasedSynthesis.synthesis import *
from src.DataStream import *
from src.reverbs import *


class Worker(QObject):
    stream_is_active = pyqtSignal()
    stream_update = pyqtSignal()
    stream_stop_close = pyqtSignal()

    def run(self):
        self.stream_is_active.emit()

    def stream_sleep_update(self):
        time.sleep(0.1)
        self.stream_update.emit()
        self.stream_is_active.emit()


class MainWindow(QMainWindow, Ui_MainWindow):
    stream_needs_update = pyqtSignal()

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.statusbar.hide()
        self.setFixedSize(1200, 600)

        self.p = pyaudio.PyAudio()
        self.audio_device_index = None
        self.worker = None
        self.thread = None

        self.midi_data = None
        self.playing = False
        self.audio_stream = DataStream()
        self.stream = None

        self.processing_visible = False  # Barra de progreso
        self.processing_progress = 0  # Porcentaje de progreso
        self.processing_message = ""  # Mensaje de qué se está procesando
        self.updateProgress()

        self.openbtn.clicked.connect(self.openFile)
        self.synthbtn.clicked.connect(self.synthesizeTracks)
        self.playbtn.clicked.connect(self.playAudio)
        self.eplusbtn.clicked.connect(self.addEffect)
        self.eminusbtn.clicked.connect(self.removeEffect)
        self.specbtn.clicked.connect(self.spectrogram)
        self.track_list.itemSelectionChanged.connect(self.track_item_changed)
        self.savebtn.clicked.connect(self.generateWAV)

    def __del__(self):
        self.p.terminate()

    def hideProgress(self):
        self.processing_visible = False  # Barra de progreso
        self.processing_progress = 0  # Porcentaje de progreso
        self.processing_message = ""  # Mensaje de qué se está procesando
        self.updateProgress()

    def readyProgress(self):
        self.processing_visible = True  # Barra de progreso
        self.processing_progress = 100  # Porcentaje de progreso
        self.processing_message = "Listo."  # Mensaje de qué se está procesando
        self.updateProgress()

    def updateProgress(self):
        self.progressBar.setHidden(not self.processing_visible)
        self.progressBar.setValue(self.processing_progress)
        self.processlabel.setText(self.processing_message)
        self.progressBar.repaint()
        self.processlabel.repaint()

    def track_item_changed(self):
        self.playbtn.setText("▶️")
        self.playing = False
        if self.stream:
            self.stream_stop_close()

    def audioCallback(self, in_data, frame_count, time_info, status):
        data = None
        if self.audio_stream.isEmpty():
            data = np.zeros(frame_count)
        else:
            data = self.audio_stream.readData(frame_count)
        return data.astype(np.float32).tobytes(), pyaudio.paContinue

    def playAudio(self):
        if self.playing:
            self.playbtn.setText("▶️")
            self.playing = False
            try:
                if self.stream.is_active():
                    if not self.stream.is_stopped():
                        self.stream.stop_stream()
            except:
                pass #stream.is_active lanza OS Error
        else:
            resume_stream = False
            if self.stream:
                try:
                    if self.stream.is_active():
                        if self.stream.is_closed():
                            self.stream.start_stream()
                            resume_stream = True
                            self.stream_is_active()
                            self.playbtn.setText("▮▮")
                            self.playing = True
                except:
                    pass #stream.is_active lanza OS Error

            if not resume_stream:
                selected_indexes = self.track_list.selectedIndexes()
                if len(selected_indexes) > 0:
                    self.playbtn.setText("▮▮")
                    self.playing = True

                    selected_index = selected_indexes[0]

                    if selected_index.row() == 0:
                        if self.midi_data.wave_tracks:
                            for i in range(self.midi_data.get_num_of_tracks()):
                                if not self.track_list.itemWidget(self.track_list.item(i+2)).isSynthesized():
                                    msg = QMessageBox()
                                    msg.setIcon(QMessageBox.Warning)
                                    msg.setWindowTitle("Advertencia!")
                                    msg.setText(f"No se realizó una sintetización para el track {i}!")
                                    msg.exec_()
                            self.playSong()
                    else:
                        i = selected_index.row() - 2
                        if self.midi_data.wave_tracks:
                            if not self.track_list.itemWidget(self.track_list.selectedItems()[0]).isSynthesized():
                                msg = QMessageBox()
                                msg.setIcon(QMessageBox.Warning)
                                msg.setWindowTitle("Advertencia!")
                                msg.setText("No se realizó una sintetización!")
                                msg.exec_()
                            self.playTrack(i)

    def playTrack(self, track):
        if self.playing:
            # Open stream with correct settings
            if not self.audio_device_index:
                device_list = []
                for i in range(self.p.get_device_count()):
                    dev = self.p.get_device_info_by_index(i)
                    device_list.append(f"{i}. {dev['name']}, {dev['maxOutputChannels']}")

                device_name, _ = QInputDialog.getItem(self, "Seleccionar un dispositivo", "Dispositivo:", device_list)
                self.audio_device_index = device_list.index(device_name)

            open_success = False
            try:
                self.stream = self.p.open(format=pyaudio.paFloat32,
                                        channels=1,
                                        rate=self.midi_data.get_sampleRate(),
                                        output=True,
                                        output_device_index=self.audio_device_index,
                                        stream_callback=self.audioCallback)
                open_success = True
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error!")
                e = sys.exc_info()[0]
                msg.setText("Error crítico intentando abrir el canal de audio!" + f"\nError: {e}")
                msg.exec_()
                self.hideProgress()

            if open_success:
                audio_data = self.get_audio_data(track=track)

                '''try:
                    for i in range(self.effect_list.count()):
                        name = f'Track 0{i}' if i < 10 else f'Track {i}'
                        if self.effect_list.itemWidget(self.effect_list.item(i)).track_number.currentText() == name:
                            if self.effect_list.itemWidget(self.effect_list.item(i)).effect_type.currentText() == "Reverb #1":
                                value = self.effect_list.itemWidget(self.effect_list.item(i)).slider.value()
                                g = np.array([value / 167 + 0.2]*6)
                                d = []
                                for i in range(6):
                                    d.append(100e-3 / (3 ** i))
                                d = np.array(d)

                                audio_data = REV_Schroeder(g, d, audio_data, self.midi_data.get_sampleRate())
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error!")
                    e = sys.exc_info()[0]
                    msg.setText("Error crítico intentando generar los efectos!" + f"\nError: {e}")
                    msg.exec_()'''

                audio_data /= max(audio_data)
                self.audio_stream.setData(audio_data)

                self.stream.start_stream()

                if self.thread:
                    if self.thread.isRunning():
                        self.thread.terminate()
                    while self.thread.isRunning(): pass

                # Step 1: Create a QThread object
                self.thread = QThread()
                # Step 2: Create a worker object
                self.worker = Worker()
                # Step 3: Move worker to the thread
                self.worker.moveToThread(self.thread)
                # Step 4: Connect signals and slots
                self.thread.started.connect(self.worker.run)
                self.stream_needs_update.connect(self.worker.stream_sleep_update)
                self.worker.stream_is_active.connect(self.stream_is_active)
                self.worker.stream_update.connect(self.stream_update)
                self.worker.stream_stop_close.connect(self.stream_stop_close)
                # Step 5: Start the thread
                self.thread.start()

    def playSong(self):
        if self.playing:
            # Open stream with correct settings
            if not self.audio_device_index:
                device_list = []
                for i in range(self.p.get_device_count()):
                    dev = self.p.get_device_info_by_index(i)
                    device_list.append(f"{i}. {dev['name']}, {dev['maxOutputChannels']}")

                device_name, _ = QInputDialog.getItem(self, "Seleccionar un dispositivo", "Dispositivo:", device_list)
                self.audio_device_index = device_list.index(device_name)

            open_success = False
            try:
                self.stream = self.p.open(format=pyaudio.paFloat32,
                                          channels=1,
                                          rate=self.midi_data.get_sampleRate(),
                                          output=True,
                                          output_device_index=self.audio_device_index,
                                          stream_callback=self.audioCallback)
                open_success = True
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error!")
                e = sys.exc_info()[0]
                msg.setText("Error crítico intentando abrir el canal de audio!" + f"\nError: {e}")
                msg.exec_()
                self.hideProgress()

            if open_success:
                audio_data = self.get_audio_data(song=True)
                self.audio_stream.setData(audio_data)

                self.stream.start_stream()

                if self.thread:
                    if self.thread.isRunning():
                        self.thread.terminate()
                    while self.thread.isRunning(): pass

                # Step 1: Create a QThread object
                self.thread = QThread()
                # Step 2: Create a worker object
                self.worker = Worker()
                # Step 3: Move worker to the thread
                self.worker.moveToThread(self.thread)
                # Step 4: Connect signals and slots
                self.thread.started.connect(self.worker.run)
                self.stream_needs_update.connect(self.worker.stream_sleep_update)
                self.worker.stream_is_active.connect(self.stream_is_active)
                self.worker.stream_update.connect(self.stream_update)
                self.worker.stream_stop_close.connect(self.stream_stop_close)
                # Step 5: Start the thread
                self.thread.start()

    def stream_is_active(self):
        try:
            if self.stream.is_active():
                self.stream_needs_update.emit()
        except:
            self.playtimelabel.setText(f'00:00 / 00:00')
            self.songSlider.setValue(0)

    def stream_update(self):
        totaltime = len(self.audio_stream.data)
        currenttime = self.audio_stream.index
        tmin = np.floor((totaltime / 44100) / 60)
        tsec = (totaltime // 44100) % 60
        min = np.floor((currenttime / 44100) / 60)
        sec = (currenttime // 44100) % 60
        tmin, tsec, min, sec = int(tmin), int(tsec), int(min), int(sec)
        tmin = f'0{tmin}' if tmin < 10 else tmin
        tsec = f'0{tsec}' if tsec < 10 else tsec
        min = f'0{min}' if min < 10 else min
        sec = f'0{sec}' if sec < 10 else sec
        self.playtimelabel.setText(f'{min}:{sec} / {tmin}:{tsec}')
        self.songSlider.setValue( int(currenttime / totaltime * 100) )

    def stream_stop_close(self):
        self.stream.stop_stream()
        self.stream.close()

        self.playtimelabel.setText(f'00:00 / 00:00')
        self.songSlider.setValue(0)

    def synthesizeTracks(self):
        try:
            selected_indexes = self.track_list.selectedIndexes()
            if len(selected_indexes) > 0:
                selected_index = selected_indexes[0]

                self.processing_visible = True  # Barra de progreso
                self.processing_progress = 0  # Porcentaje de progreso
                self.processing_message = "Sintetizando Canción..." if selected_index.row() == 0 else "Sintetizando Track..."
                self.updateProgress()

                if selected_index.row() == 0:
                    N = self.midi_data.get_num_of_tracks()
                    for i in range(N):
                        instrument = self.track_list.itemWidget(self.track_list.item(i + 2)).getProgram()
                        if instrument == "Guitar":
                            self.midi_data.synthesize_track(i, KS_string)
                        elif instrument == "Drums":
                            self.midi_data.synthesize_track(i, KS_drum)
                        elif instrument == "E-Piano":
                            self.midi_data.synthesize_track(i, add_synth_epiano)
                        elif instrument == "Bass":
                            self.midi_data.synthesize_track(i, add_synth_bass)
                        elif instrument == "Violin":
                            self.midi_data.synthesize_track(i, add_synth_violin)
                        elif instrument == "French Horn":
                            self.midi_data.synthesize_track(i, add_synth_horn)
                        elif instrument == "Trumpet":
                            self.midi_data.synthesize_track(i, sample_syn)
                        self.processing_progress = 100 * (i + 1) / N  # Porcentaje de progreso
                        self.updateProgress()
                        self.track_list.itemWidget(self.track_list.item(i + 2)).setSynthesized(True)
                    self.readyProgress()
                    self.track_list.itemWidget(self.track_list.item(0)).setSynthesized(True)
                else:
                    i = selected_index.row() - 2
                    instrument = self.track_list.itemWidget(self.track_list.item(i + 2)).getProgram()
                    if instrument == "Guitar":
                        self.midi_data.synthesize_track(i, KS_string)
                    elif instrument == "Drums":
                        self.midi_data.synthesize_track(i, KS_drum)
                    elif instrument == "E-Piano":
                        self.midi_data.synthesize_track(i, add_synth_epiano)
                    elif instrument == "Bass":
                        self.midi_data.synthesize_track(i, add_synth_bass)
                    elif instrument == "Violin":
                        self.midi_data.synthesize_track(i, add_synth_violin)
                    elif instrument == "French Horn":
                        self.midi_data.synthesize_track(i, add_synth_horn)
                    elif instrument == "Trumpet":
                        self.midi_data.synthesize_track(i, sample_syn)
                    self.processing_progress = 100  # Porcentaje de progreso
                    self.updateProgress()
                    self.readyProgress()
                    self.track_list.itemWidget(self.track_list.selectedItems()[0]).setSynthesized(True)
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Advertencia!")
                msg.setText(f"Debe seleccionar un Track, o la Canción entera para sintetizar.")
                msg.exec_()
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error!")
            e = sys.exc_info()[0]
            msg.setText("Error crítico intentando hacer la sintesis!" + f"\nError: {e}")
            msg.exec_()
            self.hideProgress()

    def addEffect(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Advertencia!")
        msg.setText(f"Los efectos no han sido integrados a la GUI... todavía ;)")
        msg.exec_()
        '''if self.midi_data:
            if self.midi_data.get_num_of_tracks() > 0:
                item = QtWidgets.QListWidgetItem(self.effect_list)
                self.effect_list.addItem(item)
                tracks = ['Canción']
                for i in range(self.midi_data.get_num_of_tracks()):
                    name = f'Track 0{i}' if i < 10 else f'Track {i}'
                    tracks.append(name)
                row = EffectItemWidget(tracks)
                item.setSizeHint(row.minimumSizeHint())
                self.effect_list.setItemWidget(item, row)'''

    def removeEffect(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Advertencia!")
        msg.setText(f"Los efectos no han sido integrados a la GUI... todavía ;)")
        msg.exec_()
        '''selected = self.effect_list.selectedIndexes()
        if len(selected) > 0:
            selected = selected[0]
            self.effect_list.takeItem(selected.row())'''

    def programChanged(self, track):
        pass

    def clearData(self):
        self.midi_data = None
        self.track_list.clear()
        self.effect_list.clear()
        self.playtimelabel.setText('00:00')
        self.readyProgress()

    def openFile(self):
        open = True
        if self.midi_data:
            open = False
            msgbox = QMessageBox(QMessageBox.Question, "Confirmación",
                                 "¿Seguro que quiere abrir un archivo?\nSe perderá el progreso actual.")
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            reply = msgbox.exec()
            if reply == QMessageBox.Yes:
                open = True
        if open:
            filename = QFileDialog.getOpenFileName(self, "Abrir Archivo", "", "Archivo MIDI (*.mid)",
                                                   "Archivo MIDI (*.mid)")[0]
            if filename:
                try:
                    self.clearData()
                    self.processing_visible = True  # Barra de progreso
                    self.processing_progress = 0  # Porcentaje de progreso
                    self.processing_message = "Abriendo archivo MIDI..."  # Mensaje de qué se está procesando
                    self.updateProgress()

                    self.midi_data = MidiData(filename)
                    self.midi_data.midi_parse()
                    N = self.midi_data.get_num_of_tracks()

                    self.processing_progress = 10  # Porcentaje de progreso
                    self.updateProgress()

                    item = QtWidgets.QListWidgetItem(self.track_list)
                    self.track_list.addItem(item)
                    row = TrackItemWidget(f'Canción', program=False)
                    item.setSizeHint(row.minimumSizeHint())
                    self.track_list.setItemWidget(item, row)

                    item = QtWidgets.QListWidgetItem(self.track_list)
                    item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                    self.track_list.addItem(item)
                    hline = QtWidgets.QFrame()
                    hline.setFrameShape(QtWidgets.QFrame.HLine)
                    hline.setFrameShadow(QtWidgets.QFrame.Sunken)
                    item.setSizeHint(hline.minimumSizeHint())
                    self.track_list.setItemWidget(item, hline)

                    for i in range(N):
                        self.processing_progress = 10 + (100 - 10) * (i + 1) / N
                        self.updateProgress()

                        item = QtWidgets.QListWidgetItem(self.track_list)
                        self.track_list.addItem(item)
                        name = f'Track 0{i}' if i < 10 else f'Track {i}'
                        row = TrackItemWidget(name, index=i)
                        #row.program.currentTextChanged.connect(lambda: self.programChanged(row.index)) #No funciona porque row cambia
                        item.setSizeHint(row.minimumSizeHint())
                        self.track_list.setItemWidget(item, row)
                    self.readyProgress()
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error!")
                    e = sys.exc_info()[0]
                    msg.setText("Error crítico intentando abrir el archivo!" + f"\nError: {e}")
                    msg.exec_()
                    self.clearData()
                return True
        return False

    def get_audio_data(self, song = False, track = 0):
        if song:
            volume = self.track_list.itemWidget(self.track_list.item(0+2)).slider.value() / 100
            audio_data = self.midi_data.wave_tracks[0] * volume

            for i in range(1, self.midi_data.get_num_of_tracks()):
                volume = self.track_list.itemWidget(self.track_list.item(i+2)).slider.value() / 100
                audio_data += self.midi_data.wave_tracks[i] * volume

            audio_data /= max(audio_data)
            audio_data *= self.track_list.itemWidget(self.track_list.item(0)).slider.value() / 100
        else:
            volume = self.track_list.itemWidget(self.track_list.item(track+2)).slider.value() / 100
            audio_data = self.midi_data.wave_tracks[track] * volume

        return audio_data

    def generateWAV(self):
        if self.midi_data.wave_tracks:
            selected = self.track_list.selectedIndexes()
            if len(selected) > 0:
                selected = selected[0].row()
                data = []
                if selected == 0:
                    data = self.get_audio_data(song=True)
                else:
                    track = selected-2
                    data = self.get_audio_data(track=track)

                filename, ok = QInputDialog.getText(self, "Elegir el nombre del archivo de salida", "Nombre del archivo")
                if ok:
                    if not filename.endswith('.wav'):
                        filename += '.wav'

                    obj = wave.open(filename, 'w')
                    obj.setnchannels(2)  # stereo/mono
                    obj.setsampwidth(2)  # cada muestra tiene 2 bytes
                    obj.setframerate(self.midi_data.get_sampleRate())
                    for L, R in zip(data, data):
                        ldata = int((2 ** 15 - 1) * L)
                        ldata = struct.pack('<h', ldata)
                        obj.writeframesraw(ldata)
                        rdata = int((2 ** 15 - 1) * R)
                        rdata = struct.pack('<h', rdata)
                        obj.writeframesraw(rdata)
                    obj.close()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Advertencia!")
                msg.setText(f"Debe seleccionar la canción o uno de los tracks.")
                msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Advertencia!")
            msg.setText(f"No se encontraron tracks.")
            msg.exec_()

    def spectrogram(self):
        if self.midi_data.wave_tracks:
            selected = self.track_list.selectedIndexes()
            if len(selected) > 0:
                selected = selected[0].row()
                data = []
                if selected == 0:
                    data = self.get_audio_data(song=True)
                else:
                    track = selected-2
                    data = self.get_audio_data(track=track)

                fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 6))
                fig.patch.set_facecolor((0.75, 0.75, 0.75))
                ax.patch.set_facecolor((0.0, 0.0, 0.0))
                Pxx, freqs, bins, im = ax.specgram(data, NFFT=1024, Fs=self.midi_data.get_sampleRate(), noverlap=900)
                ax.set_ylabel('Frecuencia [Hz]')
                ax.set_xlabel('Tiempo [s]')
                plt.show()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Advertencia!")
                msg.setText(f"Debe seleccionar la canción o uno de los tracks.")
                msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Advertencia!")
            msg.setText(f"No se encontraron tracks.")
            msg.exec_()