
import sys

# 1. Import `QApplication` and all the required widgets
from PyQt5.QtCore import QObject, QSize
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QApplication, QPushButton, QComboBox, QLineEdit, QListWidget, QListWidgetItem, QCheckBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget

class UI:
    def __init__(self):

        self.app = QApplication(sys.argv)

        self.window = QWidget()

        # window
        self.window.setWindowTitle('MQTT Client')
        self.window.setGeometry(100, 100, 400, 400)
        self.window.move(100, 15)

        self.login=QWidget(parent=self.window)


        self.subscribe=QWidget(parent=self.window)
        self.subscribe.hide()

        self.publish=QWidget(parent=self.window)
        self.publish.hide()

        self.common=QWidget(parent=self.window)
        self.common.hide()



        # login UI
        self.user = QLineEdit('', parent=self.login)
        self.password = QLineEdit('', parent=self.login)

        #label-ul folosit pentru erori
        self.errorMsg = QLabel('',parent=self.login)
        self.errorMsg.hide()
        self.errorMsg.setStyleSheet('color: red')
        self.errorMsg.setGeometry(15,30,1000,100)
        self.errorMsg.setFont(QFont('Arial', 10))

        # loginButton
        self.loginButton = QPushButton('Login', parent=self.login)
        self.loginButton.move(300, 350)
        # pass and user
        self.userLabel = QLabel('Username: ', parent=self.login)
        self.userLabel.move(20, 100)
        self.userLabel.setFont(QFont('Arial', 20))
        self.passLabel = QLabel('Password: ', parent=self.login)
        self.passLabel.move(20, 200)
        self.passLabel.setFont(QFont('Arial', 20))
        self.user.move(20, 150)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.move(20, 250)

        self.loginButton.clicked.connect(lambda: self.loginPress(self.user, self.password))

#common ui elements
        #random text
        self.helloMsg = QLabel('<h1>MQTT Client</h1>', parent=self.window)
        self.helloMsg.move(10, 15)

        #tips
        self.tips=QLabel('',parent=self.common)
        self.tips.setFont(QFont('Arial', 10))
        self.tips.setGeometry(0,0,400,400)
        self.tips.move(10, 500)
        #dc button
        self.disconnectButton=QPushButton('Disconnect',parent=self.common)
        self.disconnectButton.move(900,0)
        self.disconnectButton.clicked.connect(lambda: self.disconnectPress())

        #subscribe and publish buttons
        self.subscribeButton = QPushButton('Subscribe', parent=self.common)
        self.subscribeButton.move(10, 50)
        self.subscribeButton.resize(100,50)
        self.subscribeButton.clicked.connect(lambda: self.subscribePress())

        self.publishButton = QPushButton('Publish', parent=self.common)
        self.publishButton.resize(100, 50)
        self.publishButton.move(100, 50)
        self.publishButton.clicked.connect(lambda: self.publishPress())

        #subscribe only stuff
        self.pcList=QListWidget(parent=self.subscribe)
        self.pcList.move(10,150)
        self.pcList.resize(200,400)
        self.pcList.clicked.connect(lambda: self.listClick())
        self.pcList.setFont(QFont('Arial', 15))

        #datele de la pc-ul X
        #cpu% cpu Freq %total memory %used memory $disk usage
        self.cpuUsage=QLabel('CPU %=',parent=self.common)
        self.cpuFreq = QLabel('CPU freq=', parent=self.common)
        self.totalMem = QLabel('Total Memory=', parent=self.common)
        self.memUsage = QLabel('Memory Usage=', parent=self.common)
        self.diskUsage = QLabel('Disk Usage=', parent=self.common)

        self.cpuUsage.move(400,150)
        self.cpuFreq.move(400,200)
        self.totalMem.move(400,250)
        self.memUsage.move(400,300)
        self.diskUsage.move(400,350)

        self.checkCpuUsage = QCheckBox('CPU Usage',parent=self.common)
        self.checkCpuUsage.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px;}")
        self.checkCpuUsage.move(750,150)

        self.checkCpuFreq = QCheckBox('CPU Frequence',parent=self.common)
        self.checkCpuFreq.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px;}")
        self.checkCpuFreq.move(750, 200)

        self.checktotalmem = QCheckBox('Total Memory', parent=self.common)
        self.checktotalmem.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px;}")
        self.checktotalmem.move(750, 250)

        self.checkmemUsage = QCheckBox('Memory Usage', parent=self.common)
        self.checkmemUsage.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px;}")
        self.checkmemUsage.move(750, 300)

        self.checkdiskUsage = QCheckBox('Disk Usage', parent=self.common)
        self.checkdiskUsage.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px;}")
        self.checkdiskUsage.move(750, 350)





        # self.delButton=QPushButton('DELETE',parent=self.window)
        # self.delButton.move(300,100)
        # self.addButton = QPushButton('ADD PC', parent=self.window)
        # self.addButton.move(400, 100)
        # self.string = QLineEdit('', parent=self.window)
        # self.delButton.clicked.connect(lambda: self.delPc(self.string.text()))
        # self.addButton.clicked.connect(lambda: self.addPc(self.string.text()))

        self.login.show()
        self.window.show()





    def listClick(self):
        print(self.pcList.currentItem().text())

    def addPc(self,str):
        self.pcList.addItem(QListWidgetItem(str))
        self.pcList.item(self.pcList.count()-1).setBackground(QColor('#80ff80'))  ##ff0000=red  ##80ff80=green
    def delPc(self,str):
       index=-1
       for i in range(self.pcList.count()):
            if(self.pcList.item(i).text() == str):
                index=i
       if(index!=-1):
        self.pcList.takeItem(index)

    def publishPress(self):
        self.publish.show()
        self.subscribe.hide()
        self.tips.setText('PUBLISH TEXT')
    def subscribePress(self):

        self.common.show()
        self.subscribe.show()
        self.login.hide()
        self.publish.hide()
        self.tips.setText('SUBSCRIBE TEXT')


    def disconnectPress(self):
        self.login.show()
        self.common.hide()
        self.publish.hide()
        self.subscribe.hide()
        self.window.resize(QSize(400,400))

    def loginPress(self, user, password):
        if(user.text()!='' and password.text()!=''):
            self.tips.setText('SUBSCRIBE') #tips pt subscribe
            self.login.hide()
            self.subscribe.show()
            self.common.show()
            self.errorMsg.hide()
            self.window.resize(QSize(1000,800))
        else: #more errors here i guess
            self.errorMsg.show()
            self.errorMsg.setText("Unable to login , blank username or password")





    def run(self):

        self.app.exec_()




app=UI()
app.run()

