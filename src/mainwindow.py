# PyQt5 modules
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
# Project modules
from src.ui.mainwindow import Ui_MainWindow

from src.TrackItemWidget import *
from src.midi_parser import *

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.statusbar.hide()
        self.setFixedSize(1200, 600)

        self.midi_data = None

        self.processing = False         # Barra de progreso
        self.processing_progress = 0    # Porcentaje de progreso
        self.processing_msg = ""        # Mensaje de qué se está procesando
        self.updateProgress(self.processing, self.processing_progress, self.processing_msg)

        self.openbtn.clicked.connect(self.openFile)

    def hideProgress(self):
        self.processing = False         # Barra de progreso
        self.processing_progress = 0    # Porcentaje de progreso
        self.processing_msg = ""        # Mensaje de qué se está procesando
        self.updateProgress(self.processing, self.processing_progress, self.processing_msg)

    def updateProgress(self, processing = False, progress = 0, msg = ""):
        self.progressBar.setHidden(not processing)
        self.progressBar.setValue(progress)
        self.processlabel.setText(msg)

    def openFile(self):
        msgbox = QMessageBox(QMessageBox.Question, "Confirmación",
                             "¿Seguro que quiere abrir un archivo?\nSe perderá el progreso actual.")
        msgbox.addButton(QMessageBox.Yes)
        msgbox.addButton(QMessageBox.No)
        msgbox.setDefaultButton(QMessageBox.No)
        reply = msgbox.exec()
        if reply == QMessageBox.Yes:
            filename = QFileDialog.getOpenFileName(self, "Abrir Archivo", "", "Archivo MIDI (*.mid)",
                                                   "Archivo MIDI (*.mid)")[0]
            if filename:
                try:
                    self.processing = True  # Barra de progreso
                    self.processing_progress = 10  # Porcentaje de progreso
                    self.processing_msg = "Abriendo archivo MIDI..."  # Mensaje de qué se está procesando
                    self.updateProgress(self.processing, self.processing_progress, self.processing_msg)

                    self.midi_data = MidiData(filename)
                    self.midi_data.midi_parse()
                    N = self.midi_data.get_num_of_tracks()

                    item = QtWidgets.QListWidgetItem(self.track_list)
                    self.track_list.addItem(item)
                    row = TrackItemWidget(f'Canción', program = False)
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
                        self.processing_progress = 10+(100-10)*(i+1)/N
                        self.updateProgress(self.processing, self.processing_progress, self.processing_msg)

                        item = QtWidgets.QListWidgetItem(self.track_list)
                        self.track_list.addItem(item)
                        name = f'0{i}' if i < 10 else str(i)
                        row = TrackItemWidget(f'Track 0{i}')
                        item.setSizeHint(row.minimumSizeHint())
                        self.track_list.setItemWidget(item, row)
                    self.hideProgress()
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error!")
                    msg.setText("Error crítico intentando abrir el archivo!")
                    msg.exec_()
                    self.hideProgress()
                return True
        return False