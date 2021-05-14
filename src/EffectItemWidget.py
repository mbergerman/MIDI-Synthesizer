
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import os


class EffectItemWidget(QtWidgets.QWidget):
    def __init__(self, tracks, parent=None):
        super(EffectItemWidget, self).__init__(parent)

        self.row = QtWidgets.QHBoxLayout()

        self.effect_type = QtWidgets.QComboBox()
        self.effect_type.setFont(QtGui.QFont("Helvetica", 12))
        self.effect_type.addItem("Reverb #1")
        self.effect_type.addItem("Reverb #2")
        self.effect_type.addItem("Flanger")
        self.effect_type.addItem("Vibratto")
        self.row.addWidget(self.effect_type)

        self.row.addSpacerItem(QtWidgets.QSpacerItem(20, 30, hPolicy=QtWidgets.QSizePolicy.Expanding))
        
        self.track_number = QtWidgets.QComboBox()
        self.track_number.setFont(QtGui.QFont("Helvetica", 12))
        for t in tracks:
            self.track_number.addItem(t)
        self.row.addWidget(self.track_number)

        self.row.addSpacerItem(QtWidgets.QSpacerItem(20, 30, hPolicy=QtWidgets.QSizePolicy.Expanding))

        self.slider = QtWidgets.QSlider(orientation=Qt.Horizontal)
        self.slider.setFixedWidth(150)
        self.slider.setMaximum(100)
        self.slider.setMinimum(0)
        self.slider.setValue(50)
        self.row.addWidget(self.slider)
        self.setLayout(self.row)