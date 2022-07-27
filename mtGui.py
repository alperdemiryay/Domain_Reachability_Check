from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QObject, pyqtSignal

import time, socket, datetime, pythonping, sqlite3

class Worker(QObject):

    finished = pyqtSignal()  # give worker class a finished signal

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.infiniteLoop = True  # provide a bool run condition for the class

    def connectDbAndWriteData(self, domainListDict, date):
        db = sqlite3.connect('domainCheckDB.sqlite')
        cursor = db.cursor()
        createTableSql = '''CREATE TABLE IF NOT EXISTS domain_check_results (domain_name CHAR, latency_ms INT, date INT);'''
        cursor.execute(createTableSql)
        reformatedText = str(date.strftime('%H:%M:%S %m-%d-%Y')) +'\n'
        for domain in domainListDict.keys():
            reformatedText += (domain + (' '*(20-len(domain)))) + '  >>>  {} ms\n'.format(str(int(domainListDict[domain])))
            insertDataSql = '''INSERT INTO domain_check_results VALUES('{}', '{}', '{}')'''.format(domain, str(
                int(domainListDict[domain])), date.strftime('%Y%m%d%H%M%S'))
            cursor.execute(insertDataSql)
            db.commit()
        print(reformatedText)
        #
        #window.sonuclarWidget.setPlainText('alperdeneme ')
        window.sonuclarWidget.append(reformatedText)


    def basla(self):
        try:
            while self.infiniteLoop:
                domainList = window.domainlerWidget.toPlainText().split('\n')
                intervalTime = window.widgetKontrolAraligi.text()
                timeoutTime = window.widgetTimeoutSure.text()
                socket.setdefaulttimeout(int(timeoutTime))
                domainListDict = {}
                date = datetime.datetime.now()
                for domain in domainList:
                    connectionRequired = True
                    while connectionRequired:
                        retryCounter = 0
                        start = time.time()
                        domainIp = socket.gethostbyname(domain)
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        httpConnectionResult = s.connect_ex((domainIp, 80))
                        if (httpConnectionResult == 0) or (retryCounter >= 100):
                            end = time.time()
                            s.close()
                            print('{} domain connection time is: '.format(domain) + str(end - start))
                            connectionRequired = False
                            domainListDict[domain] = round(float(end - start), 3) * 1000
                        else:
                            retryCounter += 1
                            s.close()
                pingResult = str(pythonping.ping('8.8.8.8', timeout=1))
                if len(pingResult) >= 50:
                    pingResult = pingResult.split('/')[3].split('.')[0]
                elif 'Request timed out' in pingResult:
                    pingResult = '100000'
                else:
                    pingResult = '99999'
                print('Google DNS ping result is: ' + pingResult)
                domainListDict['GoogleDNS'] = pingResult
                self.connectDbAndWriteData(domainListDict, date)
                time.sleep(int(intervalTime))
        except Exception as e:
            print(e)
    def dur(self):
        self.infiniteLoop = False  # set the run condition to false on stop


class MainWindow(QMainWindow):
    stop_signal = pyqtSignal()  # make a stop signal to communicate with the worker in another thread

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        #Layouts
        v_layout = QVBoxLayout()
        h_layout11 = QHBoxLayout()
        h_layout12 = QHBoxLayout()
        h_layout1 = QHBoxLayout()
        h_layout2 = QHBoxLayout()
        h_layout3 = QHBoxLayout()
        h_layout4 = QHBoxLayout()

        # Labels
        self.labelKontrolAraligi = QLabel("Kontrol Araligini Saniye Olarak Giriniz!")
        h_layout11.addWidget(self.labelKontrolAraligi)
        self.labelTimeoutSure= QLabel("HTTP Timeout Suresini Saniye Olarak Giriniz!")
        h_layout11.addWidget(self.labelTimeoutSure)
        v_layout.addLayout(h_layout11)

        self.widgetKontrolAraligi = QLineEdit('5')
        h_layout12.addWidget(self.widgetKontrolAraligi)
        self.widgetTimeoutSure = QLineEdit('2')
        h_layout12.addWidget(self.widgetTimeoutSure)
        v_layout.addLayout(h_layout12)

        #Labels
        self.labelDomainGir = QLabel("Kontrol Edilecek Domain'leri Giriniz!")
        h_layout1.addWidget(self.labelDomainGir)
        self.labelSonuc = QLabel("SONUC:")
        h_layout1.addWidget(self.labelSonuc)
        v_layout.addLayout(h_layout1)

        #Texts
        self.domainlerWidget = QTextEdit()
        h_layout2.addWidget(self.domainlerWidget)
        self.sonuclarWidget = QTextEdit()
        fixed_font = QFont("Consolas")
        fixed_font.setStyleHint(QFont.TypeWriter)
        self.sonuclarWidget.setFont(fixed_font)
        self.sonuclarWidget.verticalScrollBar().setValue(self.sonuclarWidget.verticalScrollBar().maximum())
        h_layout2.addWidget(self.sonuclarWidget)
        v_layout.addLayout(h_layout2)

        #Buttons
        self.buttonDomainTaramaBaslat = QPushButton("BASLAT")
        h_layout3.addWidget(self.buttonDomainTaramaBaslat)
        self.buttonDomainTaramaTemizle = QPushButton("Temizle")
        h_layout3.addWidget(self.buttonDomainTaramaTemizle)
        self.buttonDomainTaramaDurdur = QPushButton("DURDUR")
        h_layout4.addWidget(self.buttonDomainTaramaDurdur)
        self.buttonDomainTaramaKaydet = QPushButton("Kaydet")
        h_layout4.addWidget(self.buttonDomainTaramaKaydet)
        v_layout.addLayout(h_layout3)
        v_layout.addLayout(h_layout4)

        # Thread:
        self.thread = QThread()
        self.worker = Worker()
        self.stop_signal.connect(self.worker.dur)  # connect stop signal to worker stop method
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread

        self.thread.started.connect(self.worker.basla)
        self.thread.finished.connect(self.worker.dur)

        # Button Actions
        self.buttonDomainTaramaBaslat.clicked.connect(self.thread.start)
        self.buttonDomainTaramaDurdur.clicked.connect(self.durdur)
        self.buttonDomainTaramaTemizle.clicked.connect(self.durdur)
        self.buttonDomainTaramaKaydet.clicked.connect(self.durdur)

        w = QWidget()
        w.setLayout(v_layout)

        self.setCentralWidget(w)
        self.setWindowTitle("DOMAIN ERISIM KONTROL")
        self.resize(600, 500)
        self.show()

    # When stop_btn is clicked this runs. Terminates the worker and the thread.
    def durdur(self):
        self.stop_signal.emit()  # emit the finished signal on stop


app = QApplication([])
window = MainWindow()
app.exec_()