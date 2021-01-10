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
        self.lock = threading.RLock()
        pass

    def sendPackage(self, package):
        # encode package to binary and send to conenction
        text = self.encoder.encode(package)
        self.lock.acquire()
        sent_bytes = self.conn.send(str_to_binary(text))
        self.lock.release()
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
    def __init__(self, addr, logs=False):
        self.logs_flag = logs
        self.isConnected = False
        self.loop_flag = False
        self.keep_alive = 0
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.settimeout(1)
        self.transmitter = SenderReceiver(self.conn)

        self.packedId = 0

        # generate unique client id
        length = random.randint(4, 10)
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))

        self.clientId = result_str

        # all callbacks are with the following arguments: topic, message
        self.topic_callbacks = {}
        # used only for subscribe
        self.unconfirmed_subscribe = {}
        # used for other kind of packages
        self.unconfirmed = {}
        # used for storing the topics for each publish with qos = 2
        self.stored_topics = {}

        if self.logs_flag is True:
            print("Client trying to get the Broker socket ...")
        self.conn.connect(addr)
        if self.logs_flag is True:
            print("Broker socket aquired.")

        self.loop_flag = True
        self.keep_alive_flag = False
        self.recv_thread = threading.Thread(target=self.receive_constantly)
        self.ping_thread = threading.Thread(target=self.keep_alive_clock)
        self.recv_thread.start()

    def keep_alive_clock(self):
        while self.keep_alive_flag is True:
            wait_time = self.keep_alive / 2
            while wait_time > 0 and self.keep_alive_flag is True:
                time.sleep(1)
                wait_time -= 1

            if self.keep_alive_flag is True:
                # print("Ping sent!")
                # send ping
                builder = PingreqBuilder()
                builder.reset()
                builder.buildFixedHeader()
                builder.buildVariableHeader()
                builder.buildPayload()
                ping = builder.getPackage()
                self.transmitter.sendPackage(ping)

    # this method is used for qos purpose
    # it gets a packet_id, and checks every some seconds the
    # unconfirmed dictionary
    # if after the timeout, packet_id key still exists, resend the package
    def resend_on_timeout(self, unconfirmed_package):
        packet_id = unconfirmed_package.getVariableHeader().getField("packet_id")
        packet_type = unconfirmed_package.getType()

        # in case of publish, we change the package: dup = 1
        if packet_type == 3:
            current_flags = unconfirmed_package.getFixedHeader().getFlags()
            unconfirmed_package.getFixedHeader().setFlags(current_flags | 8)

        # set the timeout
        done_flag = False
        timeout = 3
        step = 0.5

        while done_flag is False:
            index = timeout
            exist_flag = True

            while index > 0:
                time.sleep(step)

                # check if package is not in unconfirmed
                if packet_id not in self.unconfirmed.keys():
                    exist_flag = False
                    break
                else:
                    # packed_id exists, but has another type
                    existing_packet_type = self.unconfirmed[packet_id].getType()

                    if packet_type != existing_packet_type:
                        # special for qos2
                        exist_flag = False

                index -= step

            # check the exist_flag
            if exist_flag is True:
                # we need to resend the package
                if self.logs_flag is True:
                    print("Due to timeout, resend: " + str(unconfirmed_package.getType()) + " package type")
                self.transmitter.sendPackage(unconfirmed_package)
            else:
                done_flag = True

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
                            if self.logs_flag is True:
                                print("Conected successfully!")
                            # set keep alive thread
                            if self.keep_alive != 0:
                                # self.conn.settimeout(self.keep_alive)
                                self.keep_alive_flag = True
                                self.ping_thread.start()

                        else:
                            if self.logs_flag is True:
                                print("Connection failed! Return code = " + str(return_code))

                    # PUBLISH PACKAGE
                    if package_type == 3:

                        # get the topic and run callback
                        packet_topic = package_recv.getVariableHeader().getField("topic_name")
                        packet_message = package_recv.getPayload().getField("application_message")
                        packet_qos = ((package_recv.getFixedHeader().getFlags() & 6) >> 1)

                        # get the packet id
                        # if qos == 0, it has no packet_id
                        packet_id = package_recv.getVariableHeader().getField('packet_id')
                        packet_id_string = str(packet_id)

                        packet_DUP = ((package_recv.getFixedHeader().getFlags() & 8) > 0)

                        if packet_topic in self.topic_callbacks.keys():
                            # get required information
                            callback, broker_qos = self.topic_callbacks[packet_topic]

                            # depending on the qos, manage the feedback
                            if packet_qos == 0:
                                # send nothing back, just call the function to handle publish
                                # start the thread
                                threading.Thread(target=callback,
                                                 args=[package_recv.getVariableHeader().getField("topic_name"),
                                                       package_recv.getPayload().getField(
                                                           "application_message")]).start()

                            if packet_qos == 1:
                                # send puback to broker
                                puback_builder = PubackBuilder()
                                puback_builder.reset()
                                puback_builder.buildFixedHeader()
                                puback_builder.buildVariableHeader(packet_id)
                                puback_builder.buildPayload()

                                pubackPackage = puback_builder.getPackage()
                                self.transmitter.sendPackage(pubackPackage)

                                # start the thread
                                threading.Thread(target=callback,
                                                 args=[package_recv.getVariableHeader().getField("topic_name"),
                                                       package_recv.getPayload().getField(
                                                           "application_message")]).start()

                            if packet_qos == 2:
                                # extract DUP from package
                                # send Pubrec package and wait for Pubrel sequance
                                pubrec_builder = PubrecBuilder()
                                pubrec_builder.reset()
                                pubrec_builder.buildFixedHeader()
                                pubrec_builder.buildVariableHeader(packet_id)
                                pubrec_builder.buildPayload()

                                pubrecPackage = pubrec_builder.getPackage()

                                # put the package into the unconfirmed
                                self.unconfirmed[packet_id] = pubrecPackage
                                # save the topic to stored_topics
                                self.stored_topics[packet_id] = (packet_topic, packet_message)

                                # start the receving thread
                                threading.Thread(target=self.resend_on_timeout, args=[pubrecPackage]).start()

                                self.transmitter.sendPackage(pubrecPackage)

                    # PUBACK PACKAGE
                    if package_type == 4:
                        packet_id = package_recv.getVariableHeader().getField('packet_id')
                        if self.logs_flag is True:
                            print("Received PUBACK[" + str(packet_id) + "]")

                        if packet_id in self.unconfirmed.keys():
                            # daca este un publish in lista
                            if self.unconfirmed[packet_id].getType() == 3:
                                # stergem din lista, in acest moment s a terminat operatia de publish
                                self.unconfirmed.pop(packet_id, None)

                    # PUBREC PACKAGE
                    if package_type == 5:
                        packet_id = package_recv.getVariableHeader().getField('packet_id')

                        if self.logs_flag is True:
                            print("Received PUBREC[" + str(packet_id) + "]")

                        if packet_id in self.unconfirmed.keys():
                            # daca este un publish
                            if self.unconfirmed[packet_id].getType() == 3:
                                # stergem din lista si trimitem un pubrel
                                self.unconfirmed.pop(packet_id, None)

                                pubrel_builder = PubrelBuilder()
                                pubrel_builder.buildFixedHeader()
                                pubrel_builder.buildVariableHeader(packet_id)
                                pubrel_builder.buildPayload()
                                pubrel_package = pubrel_builder.getPackage()

                                # adaugam noul pachet in unconfirmed
                                self.unconfirmed[packet_id] = pubrel_package

                                # activez threadul de timeout care retrimite pubrel daca exista in lista
                                threading.Thread(target=self.resend_on_timeout, args=[pubrel_package]).start()
                                # trimit pubrel
                                self.transmitter.sendPackage(pubrel_package)

                    # PUBREL
                    if package_type == 6:
                        packet_id = package_recv.getVariableHeader().getField('packet_id')
                        if self.logs_flag is True:
                            print("Received PUBREL[" + str(packet_id) + "]")

                        if packet_id in self.unconfirmed.keys():
                            # daca este un pubrel
                            if self.unconfirmed[packet_id].getType() == 5:
                                # stergem din lista si trimitem un pubcomp
                                self.unconfirmed.pop(packet_id, None)

                                pubcomp_builder = PubcompBuilder()
                                pubcomp_builder.buildFixedHeader()
                                pubcomp_builder.buildVariableHeader(packet_id)
                                pubcomp_builder.buildPayload()
                                pubcomp_package = pubcomp_builder.getPackage()

                                self.transmitter.sendPackage(pubcomp_package)

                                # i take the topic assigned to packet_id
                                packet_topic, packet_message = self.stored_topics[packet_id]
                                # delete topic from stored_topics_list
                                self.stored_topics.pop(packet_id, None)

                                # get required information
                                callback, broker_qos = self.topic_callbacks[packet_topic]

                                # start the thread
                                threading.Thread(target=callback,
                                                 args=[packet_topic, packet_message]).start()

                    # PUBCOMP
                    if package_type == 7:
                        packet_id = package_recv.getVariableHeader().getField('packet_id')
                        if self.logs_flag is True:
                            print("Received PUBCOMP[" + str(packet_id) + "]")

                        if packet_id in self.unconfirmed.keys():
                            # daca este un pubrel
                            if self.unconfirmed[packet_id].getType() == 6:
                                # stergem din lista
                                self.unconfirmed.pop(packet_id, None)

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
                            # print("\t\tTopics = " + str(topics))

                            for index in range(0, len(topics)):
                                return_code = package_recv.getPayload().getField("return_code_" + str(index))

                                if self.logs_flag is True:
                                    print("Trying to subscribe to " + str(topics[index]) + "...")
                                if return_code == 0x80:
                                    if self.logs_flag is True:
                                        print("\tResult = FAILURE")
                                else:
                                    if self.logs_flag is True:
                                        print("\tResult = SUCCESS")
                                        print("\tQos admitted = " + str(return_code))
                                    self.topic_callbacks[topics[index]] = (callback, return_code)
                                    # print("Current callbacks: " + str(self.topic_callbacks))
                            # I treated the package, now there is no need for it so i can delete it
                            self.unconfirmed_subscribe.pop(packet_id, None)

                    # UNSUBACK PACKAGE
                    if package_type == 11:
                        packet_id = package_recv.getVariableHeader().getField("packet_id")
                        # check if packet_id exists in unconfirmed
                        if packet_id in self.unconfirmed.keys():
                            topics = []

                            for index in range(0, int(
                                    len(self.unconfirmed.get(packet_id).getPayload().getAllFields()) / 2)):
                                topics.append(self.unconfirmed.get(packet_id).getPayload().getField(
                                    "topic_content_" + str(index)))

                            if self.logs_flag is True:
                                print("\nUnsubcribe sucessful to ", topics)

                            for topic in topics:
                                del self.topic_callbacks[topic]

                        self.unconfirmed.pop(packet_id, None)

                    # PINGRESP PACKAGE
                    if package_type == 13:
                        # print("Ping response get!")
                        pass

                except Exception as ex:
                    if "An established connection was aborted by the software in your host machine" in str(ex):
                        print("\tException: " + str(ex))
                        exit(-1)
                    if "string index out of range" in str(ex):
                        print("\tException: " + str(ex))
                        exit(-1)
                    if "timed out" not in str(ex):
                        print("\tException: " + str(ex))

    def connect(self, flags, keep_alive, username='', password='', willTopic='', willMessage=''):

        # create connect package
        builder = ConnectBuilder()
        builder.buildFixedHeader()
        builder.buildVariableHeader(flags, keep_alive)
        # a problem occurs with the will message, the first 2 chars are not considered so, i just patch it
        builder.buildPayload(self.clientId, username=username, password=password, willMessage=willMessage,
                             willTopic=willTopic)
        connectPackage = builder.getPackage()

        if self.logs_flag is True:
            print("Connecting as " + username + " ...")
        # print(str(connectPackage))
        # displayControlPackageBinary(self.transmitter.encoder.encode(connectPackage))
        self.keep_alive = keep_alive

        # send a connect package
        self.transmitter.sendPackage(connectPackage)

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

    def unsubscribe(self, topics):
        self.packedId += 1
        builder = UnsubscribeBuilder()
        builder.buildFixedHeader()
        builder.buildVariableHeader(self.packedId)
        builder.buildPayload(topics)
        unsubscribePackage = builder.getPackage()

        if self.logs_flag is True:
            print("Trying to unsubscribe to ", topics)

        self.unconfirmed.update({self.packedId: unsubscribePackage})

        # trimiterea pachetului de unsubscribe
        self.transmitter.sendPackage(unsubscribePackage)

    def publish(self, topic, message, QoS):
        self.packedId += 1

        # create connect package
        builder = PublishBuilder()
        builder.reset()
        builder.buildFixedHeader(DUP=0, QoS=QoS, RETAIN=0)
        builder.buildVariableHeader(topic=topic, packetId=self.packedId)
        builder.buildPayload(message)

        publishPackage = builder.getPackage()

        if self.logs_flag is True:
            print("Publish[" + str(self.packedId) + "] sent:")
            print("\t[" + topic + "]: \"" + message + "\"")
        self.transmitter.sendPackage(publishPackage)

        # prepearing the thread that assures the resending of the message if there was a problem
        if QoS > 0:
            self.unconfirmed[self.packedId] = publishPackage
            threading.Thread(target=self.resend_on_timeout, args=[publishPackage]).start()

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

        if self.logs_flag is True:
            print("Client disconnected!")


def people_entered(topic_name, publish_message):
    print("Posted on " + topic_name + ":")
    print("\t" + publish_message)


def publish_get(topic_name, publish_message):
    print("(Received)" + topic_name + ": " + publish_message)


def custom_publish_get(topic_name, publish_message):
    print("[" + topic_name + "]: \"" + publish_message + "\"")


if __name__ == "__main__":
    # configure the adress of the broker
    ip = socket.gethostbyname(socket.gethostname())
    port = 1883
    address = (ip, port)

    username = input("Username = ")

    client = ClientMQTT(address)
    client.connect(flags="10000100", keep_alive=90, username=username, willTopic="/register",
                   willMessage="[" + username + "]:disconnected")

    while True:
        try:
            command = input("$: ")
            if command == "subscribe" or command == "s":
                nr_topics = input("\t$nr of topics: ")
                topics = []
                qos = []
                for i in range(int(nr_topics)):
                    topics.append(input("\t$topic: "))
                    qos.append(int(input("\t$qos: ")))
                client.subscribe(topics, qos, custom_publish_get)
            if command == "unsubscribe" or command == "u":
                nr_topics = input("\t$nr of topics: ")
                topics = []
                for i in range(int(nr_topics)):
                    topics.append(input("\t$topic: "))
                client.unsubscribe(topics)

            if command == "publish" or command == "p":
                topic = input("\t$topic: ")
                qos = int(input("\t$qos: "))
                message = input("\t$message: ")
                client.publish(topic, message, qos)

            if command == "topics" or command == "t":
                print("Topics: " + str(client.topic_callbacks.keys()))

            if command == "disconnect" or command == "d":
                client.disconnect()
                break
        except Exception as e:
            print(e)
