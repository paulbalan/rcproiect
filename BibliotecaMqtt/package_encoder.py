import abc
import binascii
from package_builders import *


def displayControlPackageBinary(encodedStr, file=None):
    for index in range(0, len(encodedStr), 8):
        chunk = encodedStr[index:index + 8] + "("
        if 32 <= int(encodedStr[index:index + 8], 2) < 128:
            chunk += "'" + chr(int(encodedStr[index:index + 8], 2)) + "', "
        chunk += str(int(encodedStr[index:index + 8], 2)) + ")"
        if file is not None:
            file.write(chunk)
        else:
            print(chunk)


class GenericPackageEncoder:
    def __init__(self):
        pass

    def encode(self, controlPackage) -> str:
        encodedString = ""

        # encode the header of the control package
        fixedHeader = controlPackage.getFixedHeader()
        encodedString += format(fixedHeader.getType(), '04b')
        encodedString += format(fixedHeader.getFlags(), '04b')
        remLengthEnc = self.encodeRemainingLength(fixedHeader.getRemainingLength())
        encodedString += remLengthEnc

        # encode the variable header
        variableHeader = controlPackage.getVariableHeader()

        for field in variableHeader.getAllFields():
            value = variableHeader.getAllFields()[field]
            # is string -> encode every char
            if isinstance(value, str):
                for char in value:
                    encodedString += format(ord(char), '08b')
            else:
                # is integer
                # little endian encoding
                fieldSize = variableHeader.getFieldSize(field)

                for index in range(fieldSize - 1, -1, -1):
                    mask = 0xFF << (index * 8)
                    currentByte = (value & mask) >> (index * 8)
                    encodedString += format(currentByte, '08b')

        # encode the payload
        payload = controlPackage.getPayload()

        for field in payload.getAllFields():
            value = payload.getAllFields()[field]
            # is string -> encode every char
            if isinstance(value, str):
                for char in value:
                    encodedString += format(ord(char), '08b')
            else:
                # is integer
                # little endian encoding
                fieldSize = payload.getFieldSize(field)

                for index in range(fieldSize - 1, -1, -1):
                    mask = 0xFF << (index * 8)
                    currentByte = (value & mask) >> (index * 8)
                    encodedString += format(currentByte, '08b')

        return encodedString

    # functie care primeste un int si il decodifica pentru a genera remaining length
    def encodeRemainingLength(self, remLength) -> str:
        if remLength == 0:
            return "00000000"

        remLengthStr = ""
        while remLength > 0:
            # encodedByte = remLength % 128
            encodedByte = divmod(remLength, 128)[1]
            # remLength = [remLength / 128]
            remLength = divmod(remLength, 128)[0]

            if remLength > 0:
                encodedByte = (encodedByte | 128)

            remLengthStr += format(encodedByte, '08b')

        return remLengthStr


class IPackageDecoder(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def getType(self) -> int:
        pass

    # binaryString is the encoded string of the Variable Header and the Payload
    @abc.abstractmethod
    def decodeVariableComponents(self, binaryString, fixedHeader) -> IControlPackage:
        pass

    # functie pentru extragerea unui sir de caractere dupa formatul
    # byte0: MSB of length
    # byte1: LSB of length
    # byte2 ...: char codes
    # return a tuple containing the remaining binaryString and the result string
    def decodeField(self, binaryString) -> [int, str]:
        resultStringLength = int(binaryString[0:16], 2)
        binaryString = binaryString[16:]

        resultString = ""
        for index in range(0, resultStringLength):
            char = chr(int(binaryString[0:8], 2))
            resultString += char
            binaryString = binaryString[8:]

        return [binaryString, resultString]


# Specific decoder for the CONNECT control package
class ConnectDecoder(IPackageDecoder):
    def __init__(self):
        pass

    def getType(self) -> int:
        return 1

    # binaryString is the encoded string of the Variable Header and the Payload
    def decodeVariableComponents(self, binaryString, fixedHeader) -> IControlPackage:
        if self.getType() != fixedHeader.getType():
            raise Exception("Type does not match!")

        # initialise builder
        builder = ConnectBuilder()
        builder.reset()
        # build fixed Header
        builder.buildFixedHeader(fixedHeader)

        if not isinstance(binaryString, str):
            binaryString = str(binaryString)
            if binaryString[0:2] == '0b':
                binaryString = binaryString[2:]

        # observatie: pentru decodarea unui camp de format:
        # byte0: MSB length
        # byte1: LSB length
        # byte2 ...: caractere
        #           se va utiliza self.decodeField(binaryString)

        # variable header components
        # 1) protocol name
        binaryString, protocol_name = self.decodeField(binaryString)

        # 2) level
        level = binaryString[0:8]
        binaryString = binaryString[8:]

        # 3) flags
        flags = binaryString[0:8]
        binaryString = binaryString[8:]

        # 4) keep alive
        keep_alive = int(binaryString[0:16], 2)
        binaryString = binaryString[16:]

        # build variable header
        builder.buildVariableHeader(flags, keep_alive)

        # payload components
        # 1) Client Id
        binaryString, client_id = self.decodeField(binaryString)

        # 2) Will topic and message
        will_topic = ""
        will_message = ""

        # if there is will flag on
        if flags[5] == "1":
            binaryString, will_topic = self.decodeField(binaryString)
            binaryString, will_message = self.decodeField(binaryString)

        # 3) Username and Password
        username = ""
        password = ""

        # if username flag is on
        if flags[0] == "1":
            binaryString, username = self.decodeField(binaryString)

            # if password flag is on
            if flags[1] == "1":
                binaryString, password = self.decodeField(binaryString)
        else:
            # if there is a password flag but no user flag -> error
            if flags[1] == "1":
                raise Exception("Password flag was set but username flag wasn't!")

        # build Payload
        builder.buildPayload(client_id, willTopic=will_topic,
                             willMessage=will_message, username=username, password=password)

        return builder.getPackage()


# Pentru decodarea unui string, este necesara mai intai decodarea headerului pentru a afla
#         cati biti mai trebuie cititi din buffer
class GenericPackageDecoder:
    def __init__(self):
        pass

    def decodeFixedHeader(self, binaryFixedHeader) -> IFixedHeader:
        fixedHeaderResult = FixedHeader()

        # we are working with a string
        fixedHeaderString = binaryFixedHeader
        if not isinstance(binaryFixedHeader, str):
            # translate to string
            fixedHeaderString = str(binaryFixedHeader)
            if fixedHeaderString[0:2] == "0b":
                fixedHeaderString = fixedHeaderString[2:]

        if len(fixedHeaderString) < 16:
            raise Exception("The header string has not enough length!")

        fixedHeaderResult.setType(int(fixedHeaderString[0:4], 2))
        fixedHeaderResult.setFlags(int(fixedHeaderString[4:8], 2))
        fixedHeaderResult.setRemainingLength(self.decodeRemainingLength(fixedHeaderString[8:]))
        return fixedHeaderResult

    # gets a string as an input
    def decodeRemainingLength(self, remLengthBinaryStr) -> int:
        multiplier = 1
        value = 0

        while True:
            # extract encoded byte
            encodedByte = int(remLengthBinaryStr[0:8], 2)
            remLengthBinaryStr = remLengthBinaryStr[8:]

            value += (encodedByte & 127) * multiplier
            if multiplier > 128 * 128 * 128:
                raise Exception("Malformed Remaining Length!")

            multiplier *= 128

            if encodedByte & 128 == 0:
                break

        return value

    def decodeVariableComponents(self, binaryString, fixedHeader) -> IControlPackage:
        # to be added one decoder foreach package type
        decoders = [ConnectDecoder()]

        packageType = fixedHeader.getType()

        decoder = None
        for currentDecoder in decoders:
            if currentDecoder.getType() == packageType:
                decoder = currentDecoder

        if decoder is None:
            raise Exception("Type of package unknown!")

        return decoder.decodeVariableComponents(binaryString, fixedHeader)

