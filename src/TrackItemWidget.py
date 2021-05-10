
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

class TrackItemWidget(QtWidgets.QWidget):
    def __init__(self, name, parent=None):
        super(TrackItemWidget, self).__init__(parent)

        self.row = QtWidgets.QHBoxLayout()

        self.row.addWidget(QtWidgets.QComboBox())
        self.row.addWidget(QtWidgets.QLabel(name))
        self.row.addWidget(QtWidgets.QCheckBox("Check"))
        self.row.addWidget(QtWidgets.QSlider(orientation=Qt.Horizontal))

        self.setLayout(self.row)