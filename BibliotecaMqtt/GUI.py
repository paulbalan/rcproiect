#UI

import sys

from PyQt5.QtCore import QObject, QSize
from PyQt5.QtGui import QFont, QColor, QPixmap
from PyQt5.QtWidgets import QApplication, QPushButton, QComboBox, QLineEdit, QListWidget, QListWidgetItem, QCheckBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget

from mqtt_client import *
from SOResources import *


class UI:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.window = QWidget()
        # self.window.setStyleSheet("background-image: url(BG.jpg); background-repeat: no-repeat; background-position: center")

        # self.window.setStyleSheet("background-image: url(BG.jpg)")

        # window
        self.window.setWindowTitle('MQTT Client')
        self.window.resize(500, 400)
        self.window.move(100, 15)

        self.login = QWidget(parent=self.window)

        self.login.setGeometry(0, 0, 500, 400)

        self.subscribe = QWidget(parent=self.window)
        self.subscribe.hide()
        self.subscribe.setGeometry(0, 0, 400, 800)

        self.publish = QWidget(parent=self.window)
        self.publish.hide()
        self.publish.setGeometry(0, 0, 400, 800)

        self.common = QWidget(parent=self.window)
        self.common.hide()
        self.common.setGeometry(300, 0, 1000, 750)

        # login UI
        self.user = QLineEdit('', parent=self.login)
        self.password = QLineEdit('', parent=self.login)

        # label-ul folosit pentru erori
        self.errorMsg = QLabel('', parent=self.window)
        self.errorMsg.hide()
        self.errorMsg.setStyleSheet('color: red')
        self.errorMsg.setGeometry(15, 50, 400, 50)
        self.errorMsg.setFont(QFont('Arial', 10))

        # loginButton
        self.loginButton = QPushButton('Login', parent=self.login)
        self.loginButton.move(350, 350)
        # pass and user
        self.userLabel = QLabel('Username: ', parent=self.login)
        self.userLabel.move(20, 150)
        self.userLabel.setFont(QFont('Arial', 20))
        self.passLabel = QLabel('Password: ', parent=self.login)
        self.passLabel.move(260, 150)
        self.passLabel.setFont(QFont('Arial', 20))
        self.user.move(20, 200)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.move(260, 200)

        self.loginButton.clicked.connect(lambda: self.loginPress(self.user, self.password))

        # common ui elements
        # random text
        self.helloMsg = QLabel('<h1>MQTT Client</h1>', parent=self.window)
        self.helloMsg.move(10, 15)
        self.helloMsg.setFont(QFont('Arial', 20))
        self.helloMsg.setGeometry(10, 0, 200, 100)

        # tips
        self.tips = QLabel('', parent=self.common)
        self.tips.setFont(QFont('Arial', 10))
        self.tips.setGeometry(0, 0, 300, 300)
        self.tips.move(100, 500)

        # dc button
        self.disconnectButton = QPushButton('Disconnect', parent=self.common)
        self.disconnectButton.move(600, 0)
        self.disconnectButton.clicked.connect(lambda: self.disconnectPress())

        # subscribe and publish buttons
        self.subscribeButton = QPushButton('Subscribe', parent=self.common)
        self.subscribeButton.move(100, 50)
        self.subscribeButton.resize(100, 50)
        self.subscribeButton.clicked.connect(lambda: self.subscribePress())

        self.publishButton = QPushButton('Publish', parent=self.common)
        self.publishButton.resize(100, 50)
        self.publishButton.move(200, 50)
        self.publishButton.clicked.connect(lambda: self.publishPress())

        # subscribe only stuff
        self.pcList = QListWidget(parent=self.subscribe)
        self.pcList.move(10, 150)
        self.pcList.resize(200, 400)
        self.pcList.clicked.connect(lambda: self.listClick())
        self.pcList.setFont(QFont('Arial', 15))


        # datele de la pc-ul X
        self.data = QWidget(parent=self.window)
        self.data.hide()
        self.data.setGeometry(500, 50, 400, 600)

        # cpu% cpu Freq %total memory %used memory $disk usage
        self.cpuUsage = QLabel('CPU percent    =>', parent=self.data)
        self.cpuFreq = QLabel('CPU freq       =>', parent=self.data)
        self.totalMem = QLabel('Total Memory   =>', parent=self.data)
        self.memUsage = QLabel('Memory Usage   =>', parent=self.data)
        self.diskUsage = QLabel('Disk Usage     =>', parent=self.data)

        self.cpuUsage.move(50, 150)
        self.cpuUsage.setFont(QFont('Arial', 10))
        self.cpuUsage.resize(300, 15)

        self.cpuFreq.move(0, 200)
        self.cpuFreq.setFont(QFont('Arial', 10))
        self.cpuFreq.resize(300, 15)

        self.totalMem.move(50, 250)
        self.totalMem.setFont(QFont('Arial', 10))
        self.totalMem.resize(300, 15)

        self.memUsage.move(0, 300)
        self.memUsage.setFont(QFont('Arial', 10))
        self.memUsage.resize(300, 15)

        self.diskUsage.move(50, 350)
        self.diskUsage.setFont(QFont('Arial', 10))
        self.diskUsage.resize(300, 15)

        self.checkCpuUsage = QCheckBox('CPU Usage', parent=self.subscribe)
        self.checkCpuUsage.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px;}")
        self.checkCpuUsage.move(250, 200)

        self.checkCpuFreq = QCheckBox('CPU Frequence', parent=self.subscribe)
        self.checkCpuFreq.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px;}")
        self.checkCpuFreq.move(250, 250)

        self.checktotalmem = QCheckBox('Total Memory', parent=self.subscribe)
        self.checktotalmem.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px;}")
        self.checktotalmem.move(250, 300)

        self.checkmemUsage = QCheckBox('Memory Usage', parent=self.subscribe)
        self.checkmemUsage.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px;}")
        self.checkmemUsage.move(250, 350)

        self.checkdiskUsage = QCheckBox('Disk Usage', parent=self.subscribe)
        self.checkdiskUsage.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px;}")
        self.checkdiskUsage.move(250, 400)

        # publish buttons
        self.publishTypeAuto = QPushButton('Automatic Publish', parent=self.publish)
        self.publishTypeAuto.move(50, 300)
        self.publishTypeManual = QPushButton('Manual Publish', parent=self.publish)
        self.publishTypeManual.move(50, 350)
        self.publishTypeManualButton = QPushButton('Publish your data', parent=self.publish)
        self.publishTypeManualButton.move(100, 650)
        self.publishTypeManualButton.hide()

        self.publishTypeAuto.clicked.connect(lambda: self.automaticClick())
        self.publishTypeManual.clicked.connect(lambda: self.manualClick())
        self.publishTypeManualButton.clicked.connect(lambda: self.manualPubClick())

        self.subPcButton = QPushButton('Subscribe', parent=self.subscribe)
        self.subPcButton.move(100, 670)
        self.subPcButton.clicked.connect(lambda: self.subscribeButtonPress(self.string.text()))

        #lists and subscribe
        self.pcNamesList = []
        self.clientSubscribeList = []

        # misc
        self.PCimage = QLabel(parent=self.common)
        self.PCimage.setPixmap(QPixmap("PC.png"))
        self.PCimage.setGeometry(175, 125, 400, 400)

        # useful tests
        self.delButton = QPushButton('DELETE', parent=self.subscribe)
        self.delButton.move(150, 600)
        self.addButton = QPushButton('ADD PC', parent=self.subscribe)
        self.addButton.move(50, 600)
        self.string = QLineEdit('', parent=self.subscribe)
        self.string.move(50, 630)
        self.delButton.clicked.connect(lambda: self.delPc(self.string.text()))
        self.addButton.clicked.connect(lambda: self.addPc(self.string.text()))




        self.login.show()

        self.window.show()


#publish buttons
    def automaticClick(self):
        self.publishTypeManualButton.hide()
        self.publishTypeManual.setStyleSheet("background-color: red")
        self.publishTypeAuto.setStyleSheet("background-color: green")
    def manualClick(self):
        self.publishTypeManualButton.show()
        self.publishTypeManual.setStyleSheet("background-color: green")
        self.publishTypeAuto.setStyleSheet("background-color: red")
    def manualPubClick(self):
        self.client.publish('/register', '[' + self.user.text()+']:publishing', 0)

    def Subbed(self):

        for i in self.clientSubscribeList:
            if (i[0] == self.pcList.currentItem().text()):

                if(i[2] == 'sub'):
                    self.PCimage.hide()
                    self.data.show()
                else:
                    self.PCimage.show()
                    self.data.hide()


    def setLabels(self, cpuUT, cpuFT, memTT, memUT, diskUT):
        self.cpuUsage.setText(self.cpuUsage.text()[:self.cpuUsage.text().index('>') + 1] + ' ' + cpuUT)
        self.cpuFreq.setText(self.cpuFreq.text()[:self.cpuFreq.text().index('>') + 1] + cpuFT)
        self.totalMem.setText(self.totalMem.text()[:self.totalMem.text().index('>') + 1] + memTT)
        self.memUsage.setText(self.memUsage.text()[:self.memUsage.text().index('>') + 1] + memUT)
        self.diskUsage.setText(self.diskUsage.text()[:self.diskUsage.text().index('>') + 1] + diskUT)
#subscribe buttons
    def subscribeButtonPress(self, str):
        for i in self.clientSubscribeList:
            if (i[0] == self.pcList.currentItem().text()):
                #genereaza lista dupa check-uri

                i[1].clear()
                if (self.checkCpuUsage.isChecked()):
                    i[1].append('cpuu')

                if (self.checkCpuFreq.isChecked()):
                    i[1].append('cpuf')

                if (self.checktotalmem.isChecked()):
                    i[1].append('memt')

                if (self.checkmemUsage.isChecked()):
                    i[1].append('memu')

                if (self.checkdiskUsage.isChecked()):
                    i[1].append('disk')

                if (len(i[1]) > 0):  # list is empty
                    self.errorMsg.hide()
                    if(i[2] == 'not'):
                        self.clientSubscribeList.remove((i[0],i[1],'not'))
                    else:
                        self.clientSubscribeList.remove((i[0], i[1], 'sub'))

                    self.clientSubscribeList.append((i[0],i[1],'sub'))

                    index = -1
                    for i in range(self.pcList.count()):
                        if (self.pcList.item(i).text() == str):
                            index = i
                    if (index != -1):
                        self.pcList.item(index).setBackground(QColor('#80ff80'))
                    self.PCimage.hide()
                    self.data.show()
                    #gen the pack



                    break

                else:
                    # we have a bitchass problem
                    self.errorMsg.show()
                    self.errorMsg.move(400, 550)
                    self.errorMsg.setText("You need to check at least one topic to subscribe!")
                    break



    def mainTopicMessage(self,topic,message):
        print('['+topic+']: "'+message+'"')

        user, text =message[1:].split(']')
        text=text[1:]

        if(text == 'publishing'):
            if(user != self.user.text()):
                self.addPc(user)

        #Sub register function

    def loginPress(self, user, password):
        if(user.text()!='' and password.text()!=''):
            ip = socket.gethostbyname(socket.gethostname())
            port = 1883
            address = (ip, port)

            self.client = ClientMQTT(address)

            self.client.connect(flags="10000100", keep_alive=10, username=self.user.text(), willTopic="/register",
                                willMessage='[' + self.user.text() + "]:disconnected")
            time.sleep(2)

            self.client.subscribe('/register', 0, self.mainTopicMessage)


            self.tips.setText('SUBSCRIBE') #tips pt subscribe
            self.login.hide()
            self.subscribe.show()
            self.common.show()
            self.errorMsg.hide()
            self.window.resize(QSize(1000,800))
            self.helloMsg.setText('Hello '+ self.user.text())
            self.subPcButton.hide()


        else: #more errors here i guess
            self.errorMsg.show()
            self.errorMsg.move(50,100)
            self.errorMsg.setText("Unable to login , blank username or password")

    def publishPress(self):
        self.publish.show()
        self.subscribe.hide()
        self.tips.setText('PUBLISH TEXT')
        self.uncheckAll()
        self.PCimage.hide()
        self.errorMsg.hide()
        self.data.show()
        self.setLabels(ProcessorPercent(),ProcessorFreq(),Memory(),UsedMemory(),DiskUsage())
    def subscribePress(self):
        self.uncheckAll()
        self.common.show()
        self.subscribe.show()
        self.login.hide()
        self.publish.hide()
        self.data.hide()
        self.subPcButton.hide()

        self.PCimage.show()
        self.tips.setText('SUBSCRIBE TEXT')
    def disconnectPress(self):
        self.client.disconnect()

        self.login.show()
        self.common.hide()
        self.publish.hide()
        self.subscribe.hide()
        self.uncheckAll()
        self.pcList.clear()
        self.pcNamesList.clear()
        self.window.resize(500,400)
        self.user.clear() #?
        self.password.clear()
        self.helloMsg.setText('MQTT Client')

        # Misc

    def listClick(self):
        self.uncheckAll()
        self.string.setText(self.pcList.currentItem().text())
        self.errorMsg.hide()
        self.Subbed()
        self.subPcButton.show()




    def addPc(self, str):
        if (str != '' and str not in self.pcNamesList):
            self.pcList.addItem(QListWidgetItem(str))
            self.pcList.item(self.pcList.count() - 1).setBackground(QColor('#ff0000'))  ##ff0000=red  ##80ff80=green
            self.pcNamesList.append(str)
            topicList = []
            self.clientSubscribeList.append((str, topicList , 'not'))

    def delPc(self, str):
        index = -1
        for i in range(self.pcList.count()):
            if (self.pcList.item(i).text() == str):
                index = i

        if (index != -1):
            self.pcList.takeItem(index)
            self.pcNamesList.remove(str)

    def uncheckAll(self):
        self.checkCpuUsage.setChecked(False)
        self.checkCpuFreq.setChecked(False)
        self.checktotalmem.setChecked(False)
        self.checkmemUsage.setChecked(False)
        self.checkdiskUsage.setChecked(False)

    def run(self):

        self.app.exec_()


app = UI()
app.run()
