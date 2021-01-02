from mqtt_lib import *
import socket
import random
import string
import threading
import time


# Acest module foloseste socketuri pentru a facilita
#   trimiterea si primirea de pachete client -> server
class SenderReceiver:
    def __init__(self, conn):
        self.encoder = GenericPackageEncoder()
        self.decoder = GenericPackageDecoder()
        self.conn = conn
        pass

    def sendPackage(self, package):
        # encode package to binary and send to conenction
        text = self.encoder.encode(package)
        sent_bytes = self.conn.send(str_to_binary(text))
        return sent_bytes

    def receivePackage(self) -> IControlPackage:
        # receive Fixed Header and then the variable part
        # create fixedHeader
        header_content = ""

        # read flags
        flags = self.conn.recv(1)
        header_content += binary_to_str(flags)

        # read remaining length
        remLength = binary_to_str(self.conn.recv(1))
        header_content += remLength
        while remLength[0] == '1':
            remLength = binary_to_str(self.conn.recv(1))
            header_content += remLength

        # decode header
        header_component = self.decoder.decodeFixedHeader(header_content)

        # based on the rem length, read variable header
        remLength = header_component.getRemainingLength()

        variable_content = binary_to_str(self.conn.recv(remLength))
        package = self.decoder.decodeVariableComponents(variable_content, header_component)

        return package


class ClientMQTT:
    def __init__(self, addr):
        self.isConnected = False
        self.loop_flag = False
        self.keep_alive = 0
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.settimeout(5)
        self.transmitter = SenderReceiver(self.conn)

        self.packedId = 0

        # generate unique client id
        length = random.randint(4, 10)
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))

        self.clientId = result_str

        self.topic_callbacks = {}
        # used only for subscribe
        self.unconfirmed_subscribe = {}
        # used for other kind of packages
        self.unconfirmed = {}

        print("Client trying to get the Broker socket ...")
        self.conn.connect(addr)
        print("Broker socket aquired.")

        self.loop_flag = True
        self.keep_alive_flag = False
        self.recv_thread = threading.Thread(target=self.receive_constantly)
        self.ping_thread = threading.Thread(target=self.keep_alive_clock)
        self.recv_thread.start()

    def keep_alive_clock(self):
        while self.keep_alive_flag is True:
            time.sleep(self.keep_alive / 2)

            if self.keep_alive_flag is True:
                print("Ping sent!")
                # send ping
                builder = PingreqBuilder()
                builder.reset()
                builder.buildFixedHeader()
                builder.buildVariableHeader()
                builder.buildPayload()
                ping = builder.getPackage()
                self.transmitter.sendPackage(ping)

    def receive_constantly(self):
        while self.loop_flag is True:
            if self.loop_flag is True:
                # print("Prepare to receive ...")
                try:
                    package_recv = self.transmitter.receivePackage()
                    # print("Received Package Type = " + package.getType())
                    # displayControlPackageBinary(package)

                    package_type = package_recv.getType()

                    # CONNACK PACKAGE
                    if package_type == 2:
                        return_code = package_recv.getVariableHeader().getField("connect_return_code")

                        if return_code == 0:
                            print("Conected successfully!")
                            # set keep alive thread
                            if self.keep_alive != 0:
                                self.conn.settimeout(self.keep_alive)
                                self.keep_alive_flag = True
                                self.ping_thread.start()

                        else:
                            print("Connection failed! Return code = " + str(return_code))

                    # PUBLISH PACKAGE
                    if package_type == 3:
                        # get the topic and run callback
                        topic = package_recv.getVariableHeader().getField("topic_name")
                        if topic in self.topic_callbacks.keys():
                            threading.Thread(target=self.topic_callbacks[topic], args=[package_recv]).start()

                    # SUBACK PACKAGE
                    if package_type == 9:
                        packet_id = package_recv.getVariableHeader().getField("packet_id")

                        # check if packet_id exists in unconfirmed subscribe
                        if packet_id in self.unconfirmed_subscribe.keys():
                            subscribe, callback = self.unconfirmed_subscribe[packet_id]

                            # we extract the topic list and the number of topics

                            topics = []
                            for index in range(0, int(len(subscribe.getPayload().getAllFields()) / 3)):
                                topics.append(subscribe.getPayload().getField("topic_content_" + str(index)))
                            print("\t\tTopics = " + str(topics))

                            for index in range(0, len(topics)):
                                return_code = package_recv.getPayload().getField("return_code_" + str(index))
                                print("Trying to subscribe to " + str(topics[index]) + "...")
                                if return_code == 0x80:
                                    print("\tResult = FAILURE")
                                else:
                                    print("\tResult = SUCCESS")
                                    print("\tQos admitted = " + str(return_code))
                                    self.topic_callbacks[topics[index]] = callback
                                    # print("Current callbacks: " + str(self.topic_callbacks))
                            # I treated the package, now there is no need for it so i can delete it
                            self.unconfirmed_subscribe.pop(packet_id, None)

                    # PINGRESP PACKAGE
                    if package_type == 13:
                        print("Ping response get!")

                    # UNSUBACK PACKAGE
                    if package_type == 11:
                        print("Unsubcribe sucessful")

                except Exception as e:
                    print("\tException: " + str(e))
                    pass

    def connect(self, flags, keep_alive, username='', password='', willTopic='', willMessage=''):

        # create connect package
        builder = ConnectBuilder()
        builder.buildFixedHeader()
        builder.buildVariableHeader(flags, keep_alive)
        builder.buildPayload(self.clientId, username=username, password=password, willMessage=willMessage,
                             willTopic=willTopic)
        connectPackage = builder.getPackage()

        print("Connecting as " + username + " ...")
        self.keep_alive = keep_alive

        # send a connect package
        self.transmitter.sendPackage(connectPackage)

        # receive connack
        # connackPackage = self.transmitter.receivePackage()

    # callback must have a parameter for the packet received!
    def subscribe(self, topics, QoS, callback):
        if isinstance(topics, str):
            topics = [topics]
        if isinstance(QoS, str):
            QoS = int(QoS)
        if isinstance(QoS, int):
            QoS = [QoS]

        self.packedId += 1

        builder = SubscribeBuilder()
        builder.buildFixedHeader()
        builder.buildVariableHeader(self.packedId)
        builder.buildPayload(topics, QoS)
        subscribePackage = builder.getPackage()

        # acest pachet inca nu a fost confirmat
        self.unconfirmed_subscribe[self.packedId] = (subscribePackage, callback)

        # trimiterea pachetului de subscribe
        self.transmitter.sendPackage(subscribePackage)

        # astept raspuns de subscribe
        # subackPackage = self.transmitter.receivePackage()

        # if subackPackage.getVariableHeader().getField("packet_id") != self.packedId:
        #     print("Id Packets for suback does not match!")
        #
        # for index in range(0, len(topics)):
        #     return_code = subackPackage.getPayload().getField("return_code_" + str(index))
        #     print("Trying to subscribe to " + topics[index] + "...")
        #     if return_code == 0x80:
        #         print("\tResult = FAILURE")
        #     else:
        #         print("\tResult = SUCCESS")
        #         print("\tQos admitted = " + str(return_code))
        #         self.topic_callbacks[topics[index]] = callback
        #         print("Current callbacks: " + str(self.topic_callbacks))

    def unsubscribe(self, topics):
        builder = UnsubscribeBuilder()
        builder.buildFixedHeader()
        builder.buildVariableHeader(self.packedId)
        builder.buildPayload(topics)
        unsubscribePackage = builder.getPackage()

        print("Trying to unsubscribe to ", topics)

        #trimiterea pachetului de unsubscribe
        self.transmitter.sendPackage(unsubscribePackage)

        for topic in topics:
            del self.topic_callbacks[topic]
        print(self.topic_callbacks)


    def publish(self, topic, message, QoS):
        self.packedId += 1

        # create connect package
        builder = PublishBuilder()
        builder.reset()
        builder.buildFixedHeader(DUP=0, QoS=QoS, RETAIN=0)
        builder.buildVariableHeader(topic=topic, packetId=self.packedId)
        builder.buildPayload(message)

        publishPackage = builder.getPackage()
        self.transmitter.sendPackage(publishPackage)

        # if QoS != 0:
        #     # astept sa primesc confirmare
        #     while True:
        #         try:
        #             pubAck = self.transmitter.receivePackage()
        #             if pubAck.getType() in [4, 5]:
        #                 print("Message( " + message + " ) was susscessfully sent to \"" + topic + "\"!")
        #             break
        #         except:
        #             pass

    def disconnect(self):
        # create disconnect
        builder = DisconnectBuilder()
        builder.reset()
        builder.buildFixedHeader()
        builder.buildVariableHeader()
        builder.buildPayload()
        disconnectPackage = builder.getPackage()

        if self.loop_flag is True:
            self.loop_flag = False
            self.recv_thread.join()

        if self.keep_alive_flag is True:
            self.keep_alive_flag = False
            self.ping_thread.join()

        self.transmitter.sendPackage(disconnectPackage)
        print("Client disconnected!")


def people_entered(publish_package):
    message = publish_package.getPayload().getField("application_message")
    print("Posted on /register:")
    print("\t" + message)


def publish_get(publish_package):
    topic_name = publish_package.getVariableHeader().getField("topic_name")
    message = publish_package.getPayload().getField("application_message")
    print("(Received)" + topic_name + ": " + message)


if __name__ == "__main__":
    # configure the adress of the broker
    ip = socket.gethostbyname(socket.gethostname())
    port = 1883
    address = (ip, port)

    username = input("Username = ")

    client = ClientMQTT(address)
    client.connect(flags="10000000", keep_alive=10, username=username, willTopic="/register",
                   willMessage="Disconnected " + username)
    client.subscribe(["/register"], [2], people_entered)
    client.subscribe(["/client1/cpu", "/client1/ram"], [2, 2], publish_get)

    time.sleep(4)

    client.publish("/register", "Hello, my name is " + username, 0)

    client.unsubscribe(["/register", "/client1/cpu"])

    client.publish("/client1/cpu", "Hello, my name is " + username, 0)


    time.sleep(30)
    client.disconnect()
