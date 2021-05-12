
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import os

class TrackItemWidget(QtWidgets.QWidget):
    def __init__(self, name, parent=None):
        super(TrackItemWidget, self).__init__(parent)

        self.row = QtWidgets.QHBoxLayout()

        self.program = QtWidgets.QComboBox()
        self.program.setFont(QtGui.QFont("Helvetica", 12))
        self.program.addItem("Piano")
        self.program.addItem("Guitarra")
        self.program.addItem("Percusión")
        self.row.addWidget(self.program)
        self.row.addSpacerItem(QtWidgets.QSpacerItem(10, 10, hPolicy=QtWidgets.QSizePolicy.Minimum))

        self.tracklabel = QtWidgets.QLabel(name)
        self.tracklabel.setFont(QtGui.QFont("Helvetica", 12))
        self.row.addWidget(self.tracklabel)
        self.row.addSpacerItem(QtWidgets.QSpacerItem(50, 10, hPolicy=QtWidgets.QSizePolicy.Expanding))

        speakerlabel = QtWidgets.QLabel("")
        imagepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "speaker.png")
        speakerimg = QtGui.QImage(imagepath)
        speakerlabel.setPixmap(QtGui.QPixmap.fromImage(speakerimg).scaled(30, 30, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation))
        speakerlabel.adjustSize()
        self.row.addWidget(speakerlabel)

        self.slider = QtWidgets.QSlider(orientation=Qt.Horizontal)
        self.slider.setMaximum(100)
        self.slider.setMinimum(0)
        self.slider.setValue(100)
        self.row.addWidget(self.slider)
        self.setLayout(self.row)
