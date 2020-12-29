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

    @abc.abstractmethod
    def getAllFields(self):
        pass

    @abc.abstractmethod
    def getAllSizes(self):
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

    @abc.abstractmethod
    def getAllFields(self):
        pass

    @abc.abstractmethod
    def getAllSizes(self):
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
    def __init__(self, type=0, flags=0, remLength=0):
        self.setType(type)
        self.setFlags(flags);
        self.setRemainingLength(remLength);

    def setType(self, type):
        if not type in range(0, 16):
            raise Exception("type must be between 0 and 16")
        self.type = type;

    def setFlags(self, flags):
        if not flags in range(0, 16):
            raise Exception("flags must be between 0 and 16")
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
        myStr += "\t[type -> " + str(self.type) + "]\n"
        myStr += "\t[flags -> " + format(self.flags, '04b') + "]\n"
        myStr += "\t[" + str(self.remainingLength) + "]\n"
        myStr += "}"
        return myStr


# Variable header: are la baza un dictionar cu mai multe fielduri
#   -> Acesta va fi construit de catre builder conform fiecarui tip de comanda
class VariableHeader(IVariableHeader):
    def __init__(self):
        self.fields = {}
        self.sizes = {}

    def addFieldName(self, fieldName):
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

    def getAllFields(self):
        return self.fields

    def getAllSizes(self):
        return self.sizes

    def __str__(self):
        myStr = "VariableHeader{"
        if len(self.fields) == 0:
            myStr += " }"
            return myStr
        myStr += "\n"
        for key in self.fields:
            display_text = str(self.fields[key])
            if isinstance(self.fields[key], str):
                display_text = "\"" + display_text + "\""
            myStr += "\t[" + str(key) + " -> " + display_text + "]\n"
        myStr += "}"
        return myStr


# Payload: are la baza un dictionar cu mai multe fielduri
class Payload(IPayload):
    def __init__(self):
        self.fields = {}
        self.sizes = {}

    def addFieldName(self, fieldName):
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

    def getAllFields(self):
        return self.fields

    def getAllSizes(self):
        return self.sizes

    def __str__(self):
        myStr = "Payload{"
        if len(self.fields) == 0:
            myStr += " }"
            return myStr

        myStr += "\n"
        for key in self.fields:
            display_text = str(self.fields[key])
            if isinstance(self.fields[key], str):
                display_text = "\"" + display_text + "\""
            myStr += "\t[" + str(key) + " -> " + display_text + "]\n"
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
