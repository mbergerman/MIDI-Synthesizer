# PyQt5 modules
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QWidget, QPushButton, QAction, QLineEdit, \
    QMessageBox
# Project modules
from src.ui.mainwindow import Ui_MainWindow

import pyaudio

from src.TrackItemWidget import *
from src.MidiData import *
from src.synthesizers import *
from src.SampleBasedSynthesis.synthesis import *

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.statusbar.hide()
        self.setFixedSize(1200, 600)

        self.p = pyaudio.PyAudio()

        self.midi_data = None
        self.playing = False

        self.processing_visible = False  # Barra de progreso
        self.processing_progress = 0  # Porcentaje de progreso
        self.processing_message = ""  # Mensaje de qué se está procesando
        self.updateProgress()

        self.openbtn.clicked.connect(self.openFile)
        self.synthbtn.clicked.connect(self.synthesizeTracks)
        self.playbtn.clicked.connect(self.playAudio)

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

    def stopAudio(self):
        if not self.playing:
            self.playbtn.setText("▮▮")
            self.playing = True

    def playAudio(self):
        if not self.playing:
            self.playbtn.setText("▮▮")
            self.playing = True
        else:
            self.playbtn.setText("▶️")
            self.playing = False

        if self.playing:
            selected_indexes = self.track_list.selectedIndexes()
            if len(selected_indexes) > 0:
                selected_index = selected_indexes[0]

            if selected_index.row() == 0:
                '''if self.midi_data.wave_tracks:
                    if not self.track_list.itemWidget(self.track_list.selectedItems()[0]).isSynthesized():
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setWindowTitle("Advertencia!")
                        msg.setText("No se realizó una sintetización!")
                        msg.exec_()'''
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

            device_list = []
            for i in range(self.p.get_device_count()):
                dev = self.p.get_device_info_by_index(i)
                device_list.append(f"{i}. {dev['name']}, {dev['maxOutputChannels']}")

            device_index, _ = QtWidgets.QInputDialog.getItem(self, "Seleccionar un dispositivo", "Dispositivo:",
                                                             device_list)
            device_index = device_list.index(device_index)

            stream = self.p.open(format=pyaudio.paFloat32,
                                 channels=1,
                                 rate=self.midi_data.get_sampleRate(),
                                 output=True,
                                 output_device_index=device_index
                                 )

            data = self.midi_data.wave_tracks[track].astype(np.float32).tostring()
            stream.write(data)
            stream.stop_stream()
            stream.close()

    def playSong(self):
        if self.playing:
            # Open stream with correct settings

            device_list = []
            for i in range(self.p.get_device_count()):
                dev = self.p.get_device_info_by_index(i)
                device_list.append(f"{i}. {dev['name']}, {dev['maxOutputChannels']}")

            device_index, _ = QtWidgets.QInputDialog.getItem(self, "Seleccionar un dispositivo", "Dispositivo:",
                                                             device_list)
            device_index = device_list.index(device_index)

            stream = self.p.open(format=pyaudio.paFloat32,
                                 channels=1,
                                 rate=self.midi_data.get_sampleRate(),
                                 output=True,
                                 output_device_index=device_index
                                 )

            data = np.zeros(len(self.midi_data.wave_tracks[0]))
            N = self.midi_data.get_num_of_tracks()
            for i in range(N):
                data = np.add(data, self.midi_data.wave_tracks[i])

            maxVal = np.max(np.abs(data))
            data /= max(1, maxVal)
            data = data.astype(np.float32).tostring()
            stream.write(data)
            stream.stop_stream()
            stream.close()

    def synthesizeTracks(self):
        # try:
        selected_indexes = self.track_list.selectedIndexes()
        if len(selected_indexes) > 0:
            selected_index = selected_indexes[0]

            self.processing_visible = True  # Barra de progreso
            self.processing_progress = 0  # Porcentaje de progreso
            self.processing_message = "Sintetizando Canción..." if selected_index == 0 else "Sintetizando Track..."
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
        '''except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error!")
            msg.setText("Error crítico intentando hacer la sintesis!")
            msg.exec_()
            self.hideProgress()'''

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
                        row = TrackItemWidget(name)
                        item.setSizeHint(row.minimumSizeHint())
                        self.track_list.setItemWidget(item, row)
                    self.readyProgress()
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error!")
                    msg.setText("Error crítico intentando abrir el archivo!")
                    msg.exec_()
                    self.clearData()
                return True
        return False
