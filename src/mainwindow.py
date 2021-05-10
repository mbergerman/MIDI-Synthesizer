# PyQt5 modules
from PyQt5.QtWidgets import QMainWindow
# Project modules
from src.ui.mainwindow import Ui_MainWindow

from src.TrackItemWidget import *

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        item = QtWidgets.QListWidgetItem(self.track_list)
        self.track_list.addItem(item)
        row = TrackItemWidget('Track 01')
        item.setSizeHint(row.minimumSizeHint())
        self.track_list.setItemWidget(item, row)

        item = QtWidgets.QListWidgetItem(self.track_list)
        self.track_list.addItem(item)
        row = TrackItemWidget('Track 02')
        item.setSizeHint(row.minimumSizeHint())
        self.track_list.setItemWidget(item, row)


        item = QtWidgets.QListWidgetItem(self.track_list)
        self.track_list.addItem(item)
        row = TrackItemWidget('Track 03')
        item.setSizeHint(row.minimumSizeHint())
        self.track_list.setItemWidget(item, row)
