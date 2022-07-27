import sys
import urllib2
import time
from PyQt5 import QtCore, QtGui


class DownloadThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)


    def run(self):
        time.sleep(3)
        self.emit(QtCore.SIGNAL("threadDone(QString)"), 'test')


class MainWindow(QtGui.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.list_widget = QtGui.QListWidget()
        self.button = QtGui.QPushButton("Start")
        self.button.clicked.connect(self.start_download)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        self.downloader = DownloadThread()
        self.connect(self.downloader, QtCore.SIGNAL("threadDone(QString)"), self.threadDone, QtCore.Qt.DirectConnection)

    def start_download(self):
        self.downloader.start()

    def threadDone(self, info_message):
        print(info_message)
        QtGui.QMessageBox.information(self,
                    u"Information",
                    info_message
                    )
        #self.show_info_message(info_message)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())