# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.track_list = QtWidgets.QListWidget(self.centralwidget)
        self.track_list.setGeometry(QtCore.QRect(10, 80, 681, 451))
        self.track_list.setObjectName("track_list")
        self.openbtn = QtWidgets.QPushButton(self.centralwidget)
        self.openbtn.setGeometry(QtCore.QRect(10, 10, 81, 31))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        self.openbtn.setFont(font)
        self.openbtn.setObjectName("openbtn")
        self.savebtn = QtWidgets.QPushButton(self.centralwidget)
        self.savebtn.setGeometry(QtCore.QRect(110, 10, 81, 31))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        self.savebtn.setFont(font)
        self.savebtn.setObjectName("savebtn")
        self.trackslabel = QtWidgets.QLabel(self.centralwidget)
        self.trackslabel.setGeometry(QtCore.QRect(10, 50, 421, 31))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        self.trackslabel.setFont(font)
        self.trackslabel.setObjectName("trackslabel")
        self.propertieslabel = QtWidgets.QLabel(self.centralwidget)
        self.propertieslabel.setGeometry(QtCore.QRect(710, 50, 161, 31))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        self.propertieslabel.setFont(font)
        self.propertieslabel.setObjectName("propertieslabel")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(210, 10, 221, 31))
        self.progressBar.setProperty("value", 100)
        self.progressBar.setObjectName("progressBar")
        self.processlabel = QtWidgets.QLabel(self.centralwidget)
        self.processlabel.setGeometry(QtCore.QRect(440, 10, 361, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.processlabel.setFont(font)
        self.processlabel.setObjectName("processlabel")
        self.songSlider = QtWidgets.QSlider(self.centralwidget)
        self.songSlider.setGeometry(QtCore.QRect(80, 555, 991, 21))
        self.songSlider.setMaximum(100)
        self.songSlider.setProperty("value", 0)
        self.songSlider.setOrientation(QtCore.Qt.Horizontal)
        self.songSlider.setObjectName("songSlider")
        self.playbtn = QtWidgets.QPushButton(self.centralwidget)
        self.playbtn.setGeometry(QtCore.QRect(10, 540, 51, 51))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.playbtn.setFont(font)
        self.playbtn.setCheckable(False)
        self.playbtn.setObjectName("playbtn")
        self.synthbtn = QtWidgets.QPushButton(self.centralwidget)
        self.synthbtn.setGeometry(QtCore.QRect(910, 10, 131, 31))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        self.synthbtn.setFont(font)
        self.synthbtn.setObjectName("synthbtn")
        self.specbtn = QtWidgets.QPushButton(self.centralwidget)
        self.specbtn.setGeometry(QtCore.QRect(1060, 10, 131, 31))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        self.specbtn.setFont(font)
        self.specbtn.setObjectName("specbtn")
        self.eplusbtn = QtWidgets.QPushButton(self.centralwidget)
        self.eplusbtn.setGeometry(QtCore.QRect(1120, 50, 25, 25))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        self.eplusbtn.setFont(font)
        self.eplusbtn.setObjectName("eplusbtn")
        self.eminusbtn = QtWidgets.QPushButton(self.centralwidget)
        self.eminusbtn.setGeometry(QtCore.QRect(1150, 50, 25, 25))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(12)
        self.eminusbtn.setFont(font)
        self.eminusbtn.setObjectName("eminusbtn")
        self.playtimelabel = QtWidgets.QLabel(self.centralwidget)
        self.playtimelabel.setGeometry(QtCore.QRect(1090, 550, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.playtimelabel.setFont(font)
        self.playtimelabel.setObjectName("playtimelabel")
        self.effect_list = QtWidgets.QListWidget(self.centralwidget)
        self.effect_list.setGeometry(QtCore.QRect(700, 80, 481, 451))
        self.effect_list.setObjectName("effect_list")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.openbtn.setText(_translate("MainWindow", "Abrir"))
        self.savebtn.setText(_translate("MainWindow", "Exportar"))
        self.trackslabel.setText(_translate("MainWindow", "Lista de Tracks"))
        self.propertieslabel.setText(_translate("MainWindow", "Efectos"))
        self.processlabel.setText(_translate("MainWindow", "Listo."))
        self.playbtn.setText(_translate("MainWindow", "▶"))
        self.synthbtn.setText(_translate("MainWindow", "Sintetizar"))
        self.specbtn.setText(_translate("MainWindow", "Espectrograma"))
        self.eplusbtn.setText(_translate("MainWindow", "+"))
        self.eminusbtn.setText(_translate("MainWindow", "-"))
        self.playtimelabel.setText(_translate("MainWindow", "00:00 / 00:00"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
