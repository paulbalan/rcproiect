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
    def setField(self,fieldName, value):
        pass

    @abc.abstractmethod
    def getField(self, fieldName):
        pass

# Payload
# Camp care depinde de comanda:
#   -> Required in: CONNECT, SUBSCRIBE, SUBACK, UNSUBSCRIBE
#   -> Optional in: PUBLISH
#   -> NONE in restul comenzilor (Voi crea un empty Payload class pentru acestea)
class IPayload(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def setField(self, fieldName, value):
        pass

    @abc.abstractmethod
    def getField(self, fieldName):
        pass

# definim interfata pentru un control package
class IControlPackage(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def getType(self):
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

    def str(self):
        myStr = "FixedHeader{\n"
        myStr += "[" + str(self.type) + ", " + str(self.flags) + "]\n[" + str(self.remainingLength) + "]\n"
        myStr += "}\n"
        return myStr




if __name__ == "__main__":
    firstHeader = FixedHeader()
    print(firstHeader.str())
