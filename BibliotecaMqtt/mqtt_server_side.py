from mqtt_lib import *
import socket
import random
import string
import threading


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
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transmitter = SenderReceiver(self.conn)

        self.packedId = 0

        # generate unique client id
        length = random.randint(4, 10)
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))

        self.clientId = result_str

        print("Client trying to get the Broker socket ...")
        self.conn.connect(addr)
        print("Broker socket aquired.")

    def connect(self, flags, keep_alive, username='', password='', willTopic='', willMessage=''):

        # create connect package
        builder = ConnectBuilder()
        builder.buildFixedHeader()
        builder.buildVariableHeader(flags, keep_alive)
        builder.buildPayload(self.clientId, username=username, password=password, willMessage=willMessage,
                             willTopic=willTopic)
        connectPackage = builder.getPackage()

        print("Connecting as " + username + " ...")
        # send a connect package
        self.transmitter.sendPackage(connectPackage)

        # receive connack
        connackPackage = self.transmitter.receivePackage()

        return_code = connackPackage.getVariableHeader().getField("connect_return_code")

        if return_code == 0:
            print("Conected successfully!")
        else:
            print("Connection failed! Return code = " + str(return_code))

    def subscribe(self, topics, QoS):
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

        # trimiterea pachetului de subscribe
        self.transmitter.sendPackage(subscribePackage)

        # astept raspuns de subscribe
        subackPackage = self.transmitter.receivePackage()

        if subackPackage.getVariableHeader().getField("packet_id") != self.packedId:
            print("Id Packets for suback does not match!")

        for index in range(0, len(topics)):
            return_code = subackPackage.getPayload().getField("return_code_" + str(index))
            print("Trying to subscribe to " + topics[index] + "...")
            if return_code == 0x80:
                print("\tResult = FAILURE")
            else:
                print("\tResult = SUCCESS")
                print("\tQos admitted = " + str(return_code))

    def disconnect(self):
        # create disconnect
        builder = DisconnectBuilder()
        builder.reset()
        builder.buildFixedHeader()
        builder.buildVariableHeader()
        builder.buildPayload()
        disconnectPackage = builder.getPackage()

        self.transmitter.sendPackage(disconnectPackage)
        print("Client disconnected!")


if __name__ == "__main__":
    # configure the adress of the broker
    ip = socket.gethostbyname(socket.gethostname())
    port = 1883
    address = (ip, port)

    username = input("Username = ")

    client = ClientMQTT(address)
    client.connect("10000110", 0, username=username, willTopic="/register",
                   willMessage="Hello everyone! I am " + username)
    client.subscribe(["/result", "/buldozer"], [2, 1])

    start_key = input("Start? PressKet = Any ...\n")
    #client.receive_thread.start()
    exit_key = input("Exit? PressKey = Any ...\n")

    client.disconnect()
