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
        self.setFixedSize(1000, 500)

        self.midi_data = None

        imagepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "speaker.png")
        speakerimg = QtGui.QImage(imagepath)
        self.speakerlabel.setPixmap(QtGui.QPixmap.fromImage(speakerimg).scaled(35, 35, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation))
        self.speakerlabel.adjustSize()

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