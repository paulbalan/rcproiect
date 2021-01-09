#UI

import sys

from PyQt5.QtCore import QObject, QSize
from PyQt5.QtGui import QFont, QColor, QPixmap
from PyQt5.QtWidgets import QApplication, QPushButton, QComboBox, QLineEdit, QListWidget, QListWidgetItem, QCheckBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget

from mqtt_client import *
from SOResources import *



#lista de topicuri pe care o folosim
OurTopicsAre = ['CPUUsage','CPUFreq','TotalMemory','MemoryUsage','DiskUsage']

#clasa User va fi folosita pentru a stoca niste date si flag-uri
#utile aferente altor useri
class User:

    def __init__(self, username:str):
        #username of said subscriber
        self.username = username

        #flags for the subtopics
        self.cpuUsageTopic = False
        self.cpuFreqTopic = False
        self.totalMemTopic = False
        self.memUsageTopic = False
        self.diskUsageTopic = False
        #data of said subscriber
        self.cpuUsage='UNKNOWN'
        self.cpuFreq='UNKNOWN'
        self.totalMem='UNKNOWN'
        self.memUsage='UNKNOWN'
        self.diskUsage='UNKNOWN'
        #flag that indicates sub
        self.subbed=False
        #if we are subbed to any topics , that topic should be here
        self.topicsList = []

    #genereaza lista de topicuri la care vrem sa dam sub (lista de string)
    def generateTopicList(self):
        self.topicsList.clear()
        if self.cpuUsageTopic != False:
            self.topicsList.append('CPUUsage')
        if self.cpuFreqTopic != False:
            self.topicsList.append('CPUFreq')
        if self.totalMemTopic != False:
            self.topicsList.append('TotalMemory')
        if self.memUsageTopic != False:
            self.topicsList.append('MemoryUsage')
        if self.diskUsageTopic != False:
            self.topicsList.append('DiskUsage')
        if(len(self.topicsList) == 0):
            return False
        else:
            return True

    #unsub all topics (pune flag-urile de topic pe false)
    def unsubAll(self):
        self.cpuUsageTopic = False
        self.cpuFreqTopic = False
        self.totalMemTopic = False
        self.memUsageTopic = False
        self.diskUsageTopic = False

        self.cpuUsage = 'UNKNOWN'
        self.cpuFreq = 'UNKNOWN'
        self.totalMem = 'UNKNOWN'
        self.memUsage = 'UNKNOWN'
        self.diskUsage = 'UNKNOWN'

    #sub flag
    def setFlag(self,mode):
        self.subbed=mode
    def isSubbed(self):
        return self.subbed
    #username
    def setUsername(self,user):
        self.username=user
    def getUsername(self):
        return self.username
    #data
    def setCpuUsage(self,cpuu):
        self.cpuUsage=cpuu
    def setMemUsage(self,memu):
        self.memUsage=memu
    def setCpuFreq(self, cpuf):
        self.cpuFreq = cpuf
    def setTotalMemory(self, totm):
        self.totalMem = totm
    def setDiskUsage(self,disk):
        self.diskUsage=disk

    def getCpuUsage(self):
        return self.cpuUsage
    def getCpuFreq(self):
        return self.cpuFreq
    def getTotalMemory(self):
        return self.totalMem
    def getMemUsage(self):
        return self.memUsage
    def getDiskUsage(self):
        return self.diskUsage

    def __str__(self):
        print('['+self.username+']')
        #print('SUB FLAG: '+str(self.subbed))
        #print('DATA FLAGS: \n'
        #      +' CPU USAGE:'+str(self.cpuUsageTopic)+' CPU FREQ:'+str(self.cpuFreqTopic)
        #      +' MEM USAGE:'+str(self.memUsageTopic)+' TOTAL MEM:'+str(self.totalMemTopic)+' DISK USAGE:'+str(self.diskUsageTopic)
        #     )
        print('USER DATA:\n')
        print('CPU USAGE '+self.cpuUsage+' '
        'CPU FREQ '+self.cpuFreq+' '
        'TOTAL MEM '+self.totalMem+' '
        'MEM USAGE'+self.memUsage+' '
        'DISK USAGE '+self.diskUsage)

        return ''


#clasa UI contine tot ce tine de interfata
class UI:
    def __init__(self):
        self.app = QApplication(sys.argv)

        #main window
        self.window = QWidget()
        self.window.setWindowTitle('MQTT Client')
        self.window.resize(500, 400)
        self.window.move(100, 15)


#login widget
        self.login = QWidget(parent=self.window)
        self.login.setGeometry(0, 0, 500, 400)
        #writable boxes
        self.user = QLineEdit('', parent=self.login)
        self.user.move(20, 200)
        self.password = QLineEdit('', parent=self.login)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.move(260, 200)
        # pass and user labels(efectiv scrie pass si user)
        self.userLabel = QLabel('Username: ', parent=self.login)
        self.userLabel.move(20, 150)
        self.userLabel.setFont(QFont('Arial', 20))

        self.passLabel = QLabel('Password: ', parent=self.login)
        self.passLabel.move(260, 150)
        self.passLabel.setFont(QFont('Arial', 20))



        # loginButton
        self.loginButton = QPushButton('Login', parent=self.login)
        self.loginButton.move(350, 350)
        self.loginButton.clicked.connect(lambda: self.loginPress(self.user, self.password))

#sub widget
        self.subscribe = QWidget(parent=self.window)
        self.subscribe.hide()
        self.subscribe.setGeometry(0, 0, 400, 800)
        # lista din stanga ( va scrie user-urile altor clienti)
        self.widgetList = QListWidget(parent=self.subscribe)
        self.widgetList.move(10, 150)
        self.widgetList.resize(200, 400)
        self.widgetList.setFont(QFont('Arial', 15))
        #legam listClick de click-ul pe lista
        self.widgetList.clicked.connect(lambda: self.listClick())


        #datele de la pc-ul clientului la care dam Subscribe
        self.datasub = QWidget(parent=self.window)
        self.datasub.hide()



        self.datasub.setGeometry(500, 100, 400, 500)

        # cpu% cpu Freq %total memory %used memory $disk usage
        self.cpuUsageSub = QLabel('CPU percent    =>', parent=self.datasub)
        self.cpuFreqSub = QLabel('CPU freq       =>', parent=self.datasub)
        self.totalMemSub = QLabel('Total Memory   =>', parent=self.datasub)
        self.memUsageSub = QLabel('Memory Usage   =>', parent=self.datasub)
        self.diskUsageSub = QLabel('Disk Usage     =>', parent=self.datasub)

        #placement of these labels
        self.cpuUsageSub.move(50, 100)
        self.cpuUsageSub.setFont(QFont('Arial', 10))
        self.cpuUsageSub.resize(300, 15)

        self.cpuFreqSub.move(0, 150)
        self.cpuFreqSub.setFont(QFont('Arial', 10))
        self.cpuFreqSub.resize(300, 15)

        self.totalMemSub.move(50, 200)
        self.totalMemSub.setFont(QFont('Arial', 10))
        self.totalMemSub.resize(300, 15)

        self.memUsageSub.move(0, 250)
        self.memUsageSub.setFont(QFont('Arial', 10))
        self.memUsageSub.resize(300, 15)

        self.diskUsageSub.move(50, 300)
        self.diskUsageSub.setFont(QFont('Arial', 10))
        self.diskUsageSub.resize(300, 15)

        #lista de checkbox-uri folosita in subscribe
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

        #butoane pentru subscribe si unsubscribe
        self.subPcButton = QPushButton('Subscribe', parent=self.subscribe)
        self.subPcButton.move(100, 670)
        self.subPcButton.clicked.connect(lambda: self.subscribeButtonPress()) #self.string.text()
        self.subPcButton.hide()


        self.unsubPcButton = QPushButton('Unsubscribe', parent=self.subscribe)
        self.unsubPcButton.move(200, 670)
        self.unsubPcButton.clicked.connect(lambda: self.unsubscribeButtonPress())
        self.unsubPcButton.hide()


        #list of other clients that run the app
        self.Clients = []


#pub widget
        self.publish = QWidget(parent=self.window)
        self.publish.hide()
        self.publish.setGeometry(0, 0, 400, 800)

        # datele de la pc-ul clientului
        self.data = QWidget(parent=self.window)
        self.data.hide()
        self.data.setGeometry(500, 50, 400, 600)
        # cpu% cpu Freq %total memory %used memory $disk usage
        self.cpuUsage = QLabel('CPU percent    =>', parent=self.data)
        self.cpuFreq = QLabel('CPU freq       =>', parent=self.data)
        self.totalMem = QLabel('Total Memory   =>', parent=self.data)
        self.memUsage = QLabel('Memory Usage   =>', parent=self.data)
        self.diskUsage = QLabel('Disk Usage     =>', parent=self.data)
        # placement of these labels
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

        # publish-tab ( buttons for publishing)
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

#common for sub and pub widget
        self.common = QWidget(parent=self.window)
        self.common.hide()
        self.common.setGeometry(300, 0, 1000, 750)


        # label-ul folosit pentru erori
        self.errorMsg = QLabel('', parent=self.window)
        self.errorMsg.hide()
        self.errorMsg.setStyleSheet('color: red')
        self.errorMsg.setGeometry(15, 50, 400, 50)
        self.errorMsg.setFont(QFont('Arial', 10))

        # common ui elements (folosim label-ul asta pentru a scrie 'Hello *username*'
        self.helloMsg = QLabel('<h1>MQTT Client</h1>', parent=self.window)
        self.helloMsg.move(10, 15)
        self.helloMsg.setFont(QFont('Arial', 20))
        self.helloMsg.setGeometry(10, 0, 200, 100)
        # tips (vom scrie tips in acest label)
        self.tips = QLabel('', parent=self.common)
        self.tips.setFont(QFont('Arial', 10))
        self.tips.setGeometry(0, 0, 300, 300)
        self.tips.move(100, 500)

        # dc button (disconnects the user)
        self.disconnectButton = QPushButton('Disconnect', parent=self.common)
        self.disconnectButton.move(600, 0)
        self.disconnectButton.clicked.connect(lambda: self.disconnectPress())

        # subscribe and publish tab buttons (common to both tabs)
        self.subscribeButton = QPushButton('Subscribe', parent=self.common)
        self.subscribeButton.move(100, 50)
        self.subscribeButton.resize(100, 50)
        self.subscribeButton.clicked.connect(lambda: self.subscribePress())

        self.publishButton = QPushButton('Publish', parent=self.common)
        self.publishButton.resize(100, 50)
        self.publishButton.move(200, 50)
        self.publishButton.clicked.connect(lambda: self.publishPress())



        # misc
        self.PCimage = QLabel(parent=self.common)
        self.PCimage.setPixmap(QPixmap(""))
        self.PCimage.setPixmap(QPixmap("PC.png"))
        self.PCimage.setGeometry(175, 125, 400, 400)

        #flags
        self.autoFlag=False
        self.specFlag=False
        self.clientConnected = False
        self.subworkerFlag = False

        # useful cheats
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






    #check if a user is subscribed
    def Subbed(self):

        for user in self.Clients:
            if (user.username == self.widgetList.currentItem().text()):
                #printeaza niste date despre utilizator la click pe lista
                #print(user) #useful thing to see your user's status

                self.subPcButton.show()
                self.unsubPcButton.show()

                if(user.subbed):
                    self.PCimage.hide()
                    self.datasub.show()


                    self.setLabelsSub(user)


                else:
                    self.PCimage.show()
                    self.datasub.hide()
                    # stop thread here?






    #sets the client's labels
    def setLabels(self,params): #params e o lista formata din apeluri de functie ->datele returnate de ele

        self.cpuUsage.setText(self.cpuUsage.text()[:self.cpuUsage.text().index('>') + 1] + params[0])
        self.cpuFreq.setText(self.cpuFreq.text()[:self.cpuFreq.text().index('>') + 1] + params[1])
        self.totalMem.setText(self.totalMem.text()[:self.totalMem.text().index('>') + 1] + params[2])
        self.memUsage.setText(self.memUsage.text()[:self.memUsage.text().index('>') + 1] + params[3])
        self.diskUsage.setText(self.diskUsage.text()[:self.diskUsage.text().index('>') + 1] +params[4])

    #sets the current's clicked User from the clients list
    def setLabelsSub(self, user):


        if user is None:
            self.cpuUsageSub.setText(self.cpuUsageSub.text()[:self.cpuUsageSub.text().index('>') + 1] + 'UNKNOWN')
            self.cpuFreqSub.setText(self.cpuFreqSub.text()[:self.cpuFreqSub.text().index('>') + 1] + 'UNKNOWN')
            self.totalMemSub.setText(self.totalMemSub.text()[:self.totalMemSub.text().index('>') + 1] + 'UNKNOWN')
            self.memUsageSub.setText(self.memUsageSub.text()[:self.memUsageSub.text().index('>') + 1] + 'UNKNOWN')
            self.diskUsageSub.setText(self.diskUsageSub.text()[:self.diskUsageSub.text().index('>') + 1] + 'UNKNOWN')
        else:
            self.cpuUsageSub.setText(self.cpuUsageSub.text()[:self.cpuUsageSub.text().index('>') + 1] + user.cpuUsage)
            self.cpuFreqSub.setText(self.cpuFreqSub.text()[:self.cpuFreqSub.text().index('>') + 1] + user.cpuFreq)
            self.totalMemSub.setText(self.totalMemSub.text()[:self.totalMemSub.text().index('>') + 1] + user.totalMem)
            self.memUsageSub.setText(self.memUsageSub.text()[:self.memUsageSub.text().index('>') + 1] + user.memUsage)
            self.diskUsageSub.setText(self.diskUsageSub.text()[:self.diskUsageSub.text().index('>') + 1] + user.diskUsage)

    def subUserLabels(self):
        timer = 5  # timer original 30
        print(str(self.subworkerFlag))
        while self.subworkerFlag:
            index = timer
            while index > 0 and self.subworkerFlag:
                time.sleep(1)
                index -= 1
            if self.subworkerFlag:
                person = None
                for user in self.Clients:
                    if self.string.text() == user.username :
                        person=user


                self.setLabelsSub(person)


    #function for subbed topics
    def subbedTopic(self,topic,message):
        #formatul este: [/username/subtopic]: "useful text" , useful text este ce trebuie pus in label
        #topic contine si utilizatorul respectiv si subtopicul unde trebuie pus
        print('['+topic+']: "'+message+'"')

        #despartim topic in username si subtopic

        topic = topic[1: (len(topic))]
        usertag = topic[:topic.find('/')]
        topictag = topic[topic.find('/') + 1:]
        #OurTopicsAre = ['CPUUsage','CPUFreq','TotalMemory','MemoryUsage','DiskUsage']
        #update the data in said person
        for person in self.Clients:
            if person.username == usertag:
                if topictag == 'CPUUsage':
                   person.cpuUsage=message
                if topictag == 'CPUFreq':
                    person.cpuFreq = message
                if topictag == 'TotalMemory':
                    person.totalMem = message
                if topictag == 'MemoryUsage':
                    person.memUsage = message
                if topictag == 'DiskUsage':
                    person.diskUsage = message

    #function for /register topic
    def mainTopicMessage(self,topic,message):
        print('['+topic+']: "'+message+'"')

        user, text =message[1:].split(']')
        text=text[1:]

        if(text == 'publishing'):
            if(user != self.user.text()):
                self.addPc(user)
        if text == 'disconnected':
            if (user != self.user.text()):

                self.delPc(user)

        #Sub register function



#sub-related


    def subscribePress(self):
        self.uncheckAll()
        self.common.show()
        self.subscribe.show()
        self.login.hide()
        self.publish.hide()
        self.data.hide()

        self.subPcButton.hide()
        self.unsubPcButton.hide()


        self.PCimage.show()
        self.tips.setText('SUBSCRIBE TEXT')
        # press X does what?
        # subscribe buttons

    def subscribeButtonPress(self):
        # change i to item or sth
        for person in self.Clients:
            if (person.username == self.string.text()):
                # seteaza flag-urile persoanei respective
                if (self.checkCpuUsage.isChecked()):
                    person.cpuUsageTopic = True

                if (self.checkCpuFreq.isChecked()):
                    person.cpuFreqTopic = True

                if (self.checktotalmem.isChecked()):
                    person.totalMemTopic = True

                if (self.checkmemUsage.isChecked()):
                    person.memUsageTopic = True

                if (self.checkdiskUsage.isChecked()):
                    person.diskUsageTopic= True

                if (person.generateTopicList()): #returns true if the list isnt empty
                    #no errors here Sir
                    self.errorMsg.hide()
                    #this person is now subscribed to
                    person.subbed=True

                    # gen the pack
                    publisher = '/' + person.username + '/'
                    topics = [publisher + x for x in person.topicsList]
                    QoS = [0 for x in person.topicsList]

                    self.client.subscribe(topics, QoS, self.subbedTopic)

                    #change the color of that person
                    index = -1
                    for number in range(self.widgetList.count()):
                        if (self.widgetList.item(number).text() == self.string.text()):
                            index = number
                    if (index != -1):
                        self.widgetList.item(index).setBackground(QColor('#80ff80'))

                    self.PCimage.hide()
                    self.datasub.show() #name to be changed


                    break


                else: #the list is empty and we cant generate a package with no topics

                    self.errorMsg.show()
                    self.errorMsg.move(400, 550)
                    self.errorMsg.setText("You need to check at least one topic to subscribe!")
                    break

    def unsubscribeButtonPress(self):
        # change i to item or sth
        for person in self.Clients:
            if (person.username == self.string.text()):
                #setam flagurile
                person.subbed=False
                person.unsubAll()

                # # gen the pack
                publisher = '/' + person.username + '/'
                # CpuUsed exception daca este unsubbed ???
                topics = [publisher + topicName for topicName in OurTopicsAre]
                self.client.unsubscribe(topics)

                #facem textul rosu pe lista
                index = -1
                for j in range(self.widgetList.count()):
                    if (self.widgetList.item(j).text() == person.username):
                        index = j
                if (index != -1):
                    self.widgetList.item(index).setBackground(QColor('#ff0000'))

                #facem niste widget-uri sa apara (modul unsubbed)
                self.PCimage.show()
                self.datasub.hide()
                break

#pub-related


    def publishPress(self):
        self.publish.show()
        self.subscribe.hide()
        self.tips.setText('PUBLISH TEXT')
        self.uncheckAll()
        self.PCimage.hide()
        self.errorMsg.hide()
        self.data.show()
        self.datasub.hide()
        self.setLabels([ProcessorPercent(), ProcessorFreq(), Memory(), UsedMemory(), DiskUsage()])
#functie care seteaza tipul de publish pe auto
    def automaticClick(self):

        self.publishTypeManualButton.hide()
        self.publishTypeManual.setStyleSheet("background-color: red")
        self.publishTypeAuto.setStyleSheet("background-color: green")

        self.autoFlag = True
        threading.Thread(target=self.autoPublish).start()


#functie care trimite datele clientului o data la X secunde
    def autoPublish(self):
        timer = 5  # timer original 30
        step=0.1
        while self.autoFlag:
            index = timer
            while index > 0 and self.autoFlag:
                time.sleep(step)
                index -= step
            if self.autoFlag:
                self.sendSpecs()
        # updates your specs from "data" widget every 30 seconds
#functie care updateaza spec-urile clientului o data la X secunde
    def updateSpecs(self):
        timer = 5  # timer original 30
        while self.specFlag:
            index = timer
            while index > 0 and self.specFlag:
                time.sleep(1)
                index -= 1
            if self.specFlag:
                self.setLabels([ProcessorPercent(), ProcessorFreq(), Memory(), UsedMemory(), DiskUsage()])

        # buttons for manual publishing
#butonul care seteaza tipul de publish pe manual
    def manualClick(self):

        self.publishTypeManualButton.show()
        #colorare butoane
        self.publishTypeManual.setStyleSheet("background-color: green")
        self.publishTypeAuto.setStyleSheet("background-color: red")
        #flag
        self.autoFlag = False
#butonul pentru manual publish
    def manualPubClick(self):

        self.sendSpecs()



#functie ce trimite datele utilizatorului
    def sendSpecs(self):
        # gen the pack
        publisher = '/' + self.user.text() + '/'
        # CpuUsed exception daca este unsubbed ???
        self.client.publish('/register', '[' + self.user.text() + ']:publishing', 0)

        topics = [publisher + x for x in OurTopicsAre]

        messages = []
        messages.append(self.cpuUsage.text()[self.cpuUsage.text().find('>') + 1:])
        messages.append(self.cpuFreq.text()[self.cpuFreq.text().find('>') + 1:])
        messages.append(self.totalMem.text()[self.totalMem.text().find('>') + 1:])
        messages.append(self.memUsage.text()[self.memUsage.text().find('>') + 1:])
        messages.append(self.diskUsage.text()[self.diskUsage.text().find('>') + 1:])

        for index in range(len(messages)):
            self.client.publish(topics[index], messages[index], 0)

    #login-related
    def loginPress(self, user, password):

        if (user.text() != ''): # and password.text() != ''):
            #makin the address
            ip = socket.gethostbyname(socket.gethostname())
            port = 1883
            address = (ip, port)
            #connect the client
            self.client = ClientMQTT(address)

            self.client.connect(flags="10000100", keep_alive=10, username=self.user.text(), willTopic="/register",
                                willMessage='[' + self.user.text() + "]:disconnected")
            time.sleep(2)
            #publish on the main topic
            self.clientConnected = True
            self.client.subscribe('/register', 0, self.mainTopicMessage)
            #starting gathering client's specs
            self.specFlag = True
            threading.Thread(target=self.updateSpecs).start()

            self.subworkerFlag = True
            threading.Thread(target=self.subUserLabels).start()

            #setting some size things and texts up
            self.tips.setText('SUBSCRIBE')  # tips pt subscribe
            self.window.resize(QSize(1000, 800))
            self.helloMsg.setText('Hello ' + self.user.text())

            self.login.hide()

            self.subscribe.show()
            self.common.show()

            self.errorMsg.hide()



        else:  # more errors here i guess
            #slight problems
            self.errorMsg.show()
            self.errorMsg.move(50, 100)
            self.errorMsg.setText("Unable to login , blank username or password")

#misc
    def listClick(self):
        self.uncheckAll()
        self.string.setText(self.widgetList.currentItem().text())
        self.errorMsg.hide()
        #checks if subbed to display appropriate things
        self.Subbed()


    # the disconnect button (top right)
    def disconnectPress(self):
        # set flags
        self.autoFlag = False
        self.specFlag = False
        self.clientConnected = False

        time.sleep(0.5)

        # spunem pe register ca plecam
        self.client.publish('/register', '[' + self.user.text() + ']:disconnected', 0)
        self.client.disconnect()


        # window stuff
        self.window.resize(500, 400)
        self.login.show()
        self.common.hide()
        self.publish.hide()
        self.subscribe.hide()
        # quality of life things (reset to nothing)
        self.uncheckAll()
        self.widgetList.clear()
        self.user.clear()
        self.password.clear()
        self.helloMsg.setText('MQTT Client')



        # Misc

    # add and del buttons (misc)
    def addPc(self, user: str):

        if ( user != ''):
            person = User(user)
            flag=True
            for client in self.Clients:
                if client.username == person.username:
                    flag=False
            if flag==True:
                #adaugam in lista si il coloram cu rosu
                self.widgetList.addItem(QListWidgetItem(person.username))
                self.widgetList.item(self.widgetList.count() - 1).setBackground(QColor('#ff0000'))  ##ff0000=red  ##80ff80=green
                self.Clients.append(person)
    def delPc(self, username):
        # #cautare in lista widget
        index = -1
        for i in range(self.widgetList.count()):
            if (self.widgetList.item(i).text() == username):
                index = i
        if (index != -1):
            self.widgetList.takeItem(index)

        person=None

        for x in self.Clients :
            if(x.username == username):
                person=x

        if(person!= None):
            self.Clients.remove(person)




    def uncheckAll(self):
        self.checkCpuUsage.setChecked(False)
        self.checkCpuFreq.setChecked(False)
        self.checktotalmem.setChecked(False)
        self.checkmemUsage.setChecked(False)
        self.checkdiskUsage.setChecked(False)

    #main function that runs the UI
    def run(self):





        self.app.exec_()
        self.autoFlag = False
        self.specFlag = False
        self.subworkerFlag=False



        #if this user dies unexpectedly it's connected flag is still up and we can send his will :(
        if self.clientConnected == True:
            self.client.publish('/register','['+self.helloMsg.text()[6:]+']:disconnected',0)
            self.client.disconnect()
        #print('might not close daca mosquitto e inchis')

#rulare interfata
app = UI()
app.run()
