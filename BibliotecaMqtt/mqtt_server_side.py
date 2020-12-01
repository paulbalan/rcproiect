from mqtt_lib import *
import socket

# Acest module foloseste socketuri pentru a facilita
#   trimiterea si primirea de pachete client -> server


if __name__ == "__main__":
    # configure the adress of the broker
    ip = socket.gethostbyname(socket.gethostname())
    port = 1883
    address = (ip, port)
    print(address)

    # connect to broker using tcp/ip
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #my_socket.bind(address)

    print("Before accepting")
    my_socket.connect(address)
    print("Accepted")

    # create connect package
    builder = ConnectBuilder()
    builder.buildFixedHeader()
    builder.buildVariableHeader("10000110", 0)
    builder.buildPayload("firstClient", username="vladbatalan", willMessage="hello world!", willTopic="/register")
    connectPk = builder.getPackage()

    # create encoders and decoders
    encoder = GenericPackageEncoder()
    decoder = GenericPackageDecoder()

    print("Before sending")
    # send a connect package
    content = encoder.encode(connectPk) # is a string containing 1 s and zeros
    displayControlPackageBinary(content)

    # print("encoded content = " + str(content.encode('UTF-8')))
    sent = my_socket.send(str_to_binary(content))
    print(str(sent) + " bytes were sent")



    # receive a connack
    print("starting recv ...")
    raw = my_socket.recv(4)
    print("raw received = " + str(raw))
    buffer = binary_to_str(raw)
    print("ended recv")
    print("buffer = " + buffer)
    fixedHeader = decoder.decodeFixedHeader(buffer[0:16])

    if fixedHeader.getType() == 2:
        connackPk = decoder.decodeVariableComponents(buffer[16:], fixedHeader)
        print(str(connackPk))
    else:
        print(str(fixedHeader.getType()) + "received")

    # ping request
    builder = PingreqBuilder()
    builder.reset()
    builder.buildFixedHeader()
    builder.buildVariableHeader()
    builder.buildPayload()
    pingReq = builder.getPackage()

    print(str(pingReq))
    my_socket.send(str_to_binary(encoder.encode(pingReq)))


    # receive a pingResp
    print("starting recv ...")
    raw = my_socket.recv(2)
    print("raw received = " + str(raw))
    buffer = binary_to_str(raw)
    print("ended recv")
    print("buffer = " + buffer)
    fixedHeader = decoder.decodeFixedHeader(buffer[0:16])

    if fixedHeader.getType() == 2:
        pingResp = decoder.decodeVariableComponents(buffer[16:], fixedHeader)
        print(str(pingResp))
    else:
        print(str(fixedHeader.getType()) + " received")



    # create disconnect
    builder = DisconnectBuilder()
    builder.reset()
    builder.buildFixedHeader()
    builder.buildVariableHeader()
    builder.buildPayload()
    disconnect = builder.getPackage()

    disconnect_text = encoder.encode(disconnect)
    my_socket.send(str_to_binary(disconnect_text))




