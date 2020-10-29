import abc

# un control package este format implicit din 3 componente membre
# Fixed Header
# Existent in acelasi format pentru toate tipurile de Control Packages
# Contine 2 campuri: -> byte1: MQTT Control type (4biti) + Specific flags (4biti)
#                    -> byte2 ...: Remainging Length of the package
class IFixedHeader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def setType(self, type):
        pass

    @abc.abstractmethod
    def setFlags(self, flags):
        pass

    @abc.abstractmethod
    def setRemainingLength(self, remLength):
        pass


    @abc.abstractmethod
    def getType(self):
        pass

    @abc.abstractmethod
    def getFlags(self):
        pass


    @abc.abstractmethod
    def getRemainingLength(self):
        pass

# Variable Header
# Continutul acestui camp depinde de tipul controlului:
#    -> Packet Identifier: 2 bytes (MSB, LSB) for:
#           ->PUBLISH(if QoS > 0),PUBACK, PUBREC, PUBREL, PUBCOMP, SUBSCRIBE, SUBACK, UNSUBSCRIBE, UNSUBACK
#    -> etc ...
# Din motivul faptului ca este variabil, pentru fiecare comanda separata, va exista un VariableHeader corespunzator
# Va fi conceput din mai multe fielduri (un hashmap de valori)
class IVariableHeader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def addFieldName(self,fieldName):
        pass

    @abc.abstractmethod
    def setField(self,fieldName, value, fieldLength):
        pass

    @abc.abstractmethod
    def getField(self, fieldName):
        pass

    @abc.abstractmethod
    def getFieldSize(self, fieldName):
        pass

    @abc.abstractmethod
    def getSize(self):
        pass

# Payload
# Camp care depinde de comanda:
#   -> Required in: CONNECT, SUBSCRIBE, SUBACK, UNSUBSCRIBE
#   -> Optional in: PUBLISH
#   -> NONE in restul comenzilor (Voi crea un empty Payload class pentru acestea)
class IPayload(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def addFieldName(self, fieldName):
        pass

    @abc.abstractmethod
    def setField(self, fieldName, value, fieldLength):
        pass

    @abc.abstractmethod
    def getField(self, fieldName):
        pass

    @abc.abstractmethod
    def getFieldSize(self, fieldName):
        pass

    @abc.abstractmethod
    def getSize(self):
        pass

# definim interfata pentru un control package
class IControlPackage(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def getType(self):
        pass
    @abc.abstractmethod
    def getFixedHeader(self):
        pass
    @abc.abstractmethod
    def getVariableHeader(self):
        pass
    @abc.abstractmethod
    def getPayload(self):
        pass

# Clasele concrete
# Fixed Header = Acelasi pentru toate tipurile de pachete
class FixedHeader(IFixedHeader):
    def __init__(self, type=0, flags=0, remLength = 0):
        self.setType(type)
        self.setFlags(flags);
        self.setRemainingLength(remLength);

    def setType(self, type):
        if not type in range(0, 16):
            raise "type must be between 0 and 16"
        self.type = type;


    def setFlags(self, flags):
        if not flags in range(0, 16):
            raise "flags must be between 0 and 16"
        self.flags = flags;

    def setRemainingLength(self, remLength):
        self.remainingLength = remLength;

    def getType(self):
        return self.type

    def getFlags(self):
        return self.flags

    def getRemainingLength(self):
        return self.remainingLength

    def __str__(self):
        myStr = "FixedHeader{\n"
        myStr += "\t[" + str(self.type) + ", " + str(self.flags) + "]\n\t[" + str(self.remainingLength) + "]\n"
        myStr += "}"
        return myStr

# Variable header: are la baza un dictionar cu mai multe fielduri
#   -> Acesta va fi construit de catre builder conform fiecarui tip de comanda
class VariableHeader(IVariableHeader):
    def __init__(self):
        self.fields = {}
        self.sizes = {}

    def addFieldName(self,fieldName):
        self.fields[fieldName] = None
        self.sizes[fieldName] = 0

    def setField(self, fieldName, value, fieldSize):
        if fieldName in self.fields:
            self.fields[fieldName] = value
            self.sizes[fieldName] = fieldSize
        else:
            raise "Unidentified field name: " + fieldName

    def getField(self, fieldName):
        if fieldName in self.fields:
            return self.fields[fieldName]
        return None

    def getFieldSize(self, fieldName):
        if fieldName in self.sizes:
            return self.sizes[fieldName]
        else:
            return 0

    def getSize(self):
        totalSize = 0
        for field in self.sizes:
            totalSize += self.sizes[field]
        return totalSize

    def __str__(self):
        myStr = "VariableHeader{"
        if len(self.fields) == 0:
            myStr += " }"
            return myStr
        myStr += "\n"
        for key in self.fields:
            myStr += "\t["  + str(key) + " -> " + str(self.fields[key]) + "]\n"
        myStr += "}"
        return myStr

# Payload: are la baza un dictionar cu mai multe fielduri
class Payload(IPayload):
    def __init__(self):
        self.fields = {}
        self.sizes = {}

    def addFieldName(self,fieldName):
        self.fields[fieldName] = None
        self.sizes[fieldName] = 0

    def setField(self, fieldName, value, fieldSize):
        if fieldName in self.fields:
            self.fields[fieldName] = value
            self.sizes[fieldName] = fieldSize
        else:
            raise "Unidentified field name: " + fieldName

    def getField(self, fieldName):
        if fieldName in self.fields:
            return self.fields[fieldName]
        return None

    def getFieldSize(self, fieldName):
        if fieldName in self.sizes:
            return self.sizes[fieldName]
        else:
            return 0

    def getSize(self):
        totalSize = 0
        for field in self.sizes:
            totalSize += self.sizes[field]
        return totalSize

    def __str__(self):
        myStr = "Payload{"
        if len(self.fields) == 0:
            myStr += " }"
            return myStr

        myStr += "\n"
        for key in self.fields:
            myStr += "\t["  + str(key) + " -> " + str(self.fields[key]) + "]\n"
        myStr += "}"
        return myStr

# Generic control package that is used to describe all packages
class ControlPackage(IControlPackage):
    def __init__(self, fixedHeader, variableHeader, payload):
        self.fixedHeader = fixedHeader
        self.variableHeader = variableHeader
        self.payload = payload

    def getType(self):
        return self.fixedHeader.getType()
    def getFixedHeader(self):
        return self.fixedHeader
    def getVariableHeader(self):
        return self.variableHeader
    def getPayload(self):
        return self.payload
    def __str__(self):
        myStr = str(self.getType()) + ":\n{\n"
        myStr += str(self.fixedHeader) + "\n"
        myStr += str(self.variableHeader) + "\n"
        myStr += str(self.payload) + "\n"
        myStr += "}\n"
        return myStr


def createConnectPackage():
    myVarHeader = VariableHeader()
    myVarHeader.addFieldName("protocol_name_length")
    myVarHeader.addFieldName("protocol_name")
    myVarHeader.addFieldName("level")
    myVarHeader.addFieldName("connect_flags")
    myVarHeader.addFieldName("keep_allive")

    myVarHeader.setField("protocol_name_length", 4, 2)
    myVarHeader.setField("protocol_name", "MQTT", len("MQTT"))
    myVarHeader.setField("level", 4, 1)
    myVarHeader.setField("connect_flags", int("11001110", 2), 1)
    myVarHeader.setField("keep_allive", 10, 2)

    myFixedHeader = FixedHeader()
    myFixedHeader.setType(1)
    myFixedHeader.setFlags(int("0000", 2))
    myFixedHeader.setRemainingLength(myVarHeader.getSize())

    # username(0) | password(1) | will retain(2) | will Qos(3 - 4) | will flag(5) | cleanSesion(6) | reserved(7)
    varFlags = str(bin(myVarHeader.getField("connect_flags")))[2:]
    print("Connect flags = " + varFlags)

    myPayload = Payload()
    myPayload.addFieldName("client_identifier_length")
    myPayload.addFieldName("client_identifier")

    # aici identificatorul de client nu admite toate caracterele
    myPayload.setField("client_identifier_length", len("First Client"), 2)
    myPayload.setField("client_identifier", "First Client", len("First Client"))

    #will flag
    if varFlags[5] == "1":
        myPayload.addFieldName("will_topic_length")
        myPayload.addFieldName("will_topic")
        myPayload.setField("will_topic_length", len("Not death"), 2)
        myPayload.setField("will_topic", "Not death", len("Not death"))

        myPayload.addFieldName("will_message_length")
        myPayload.addFieldName("will_message")
        myPayload.setField("will_message_length", len("My will is to be awake"), 2)
        myPayload.setField("will_message", "My will is to be awake", len("My will is to be awake"))

    #username
    if varFlags[0] == "1":
        myPayload.addFieldName("username_length")
        myPayload.addFieldName("username")
        myPayload.setField("username_length", len("vladbatalan"), 2)
        myPayload.setField("username", "vladbatalan", len("vladbatalan"))

        #pasword
        if varFlags[1] == "1":
            myPayload.addFieldName("password_length")
            myPayload.addFieldName("password")
            myPayload.setField("password_length", len("surprise"), 2)
            myPayload.setField("password", "surprise", len("surprise"))


    return ControlPackage(myFixedHeader, myVarHeader, myPayload)


if __name__ == "__main__":
    types = ["REZERVED", "CONNECT", "CONNACK", "PUBLISH", "..."]

    connectPkg = createConnectPackage()
    print(str(connectPkg))

    print(connectPkg.getPayload().getField("non_existing"))


