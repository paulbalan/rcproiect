from base_components import *


# Fiecare commanda va avea cate un builder asignat
class IPackageBuilder(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def getPackage(self) -> IControlPackage:
        pass


class ConnectBuilder(IPackageBuilder):
    def __init__(self):
        self.fixedHeader = FixedHeader()
        self.variableHeader = VariableHeader()
        self.payload = Payload()

        self.componentsGenerated = [False, False, False]

    def reset(self):
        self.fixedHeader = FixedHeader()
        self.variableHeader = VariableHeader()
        self.payload = Payload()

        self.componentsGenerated = [False, False, False]
        pass

    def buildFixedHeader(self, fixedHeader=None):
        if fixedHeader is not None:
            if fixedHeader.getType() != 1:
                raise Exception("Type does not match with builder type!")
            if fixedHeader.getFlags() != 0:
                raise Exception("Flags do not match with builder specific flag types!")
            self.fixedHeader = fixedHeader
        else:
            # type = 0001
            self.fixedHeader.setType(1)
            # flags = 0000 (reserved)
            self.fixedHeader.setFlags(0)
            # reset remaining length
            self.fixedHeader.setRemainingLength(0)

        self.componentsGenerated[0] = True

    # connectFlags must be sent as string
    def buildVariableHeader(self, connectFlags, keepAlive):
        if not self.componentsGenerated[0]:
            raise Exception("CONNECT control package: You must first build the Fixed Header component!")
        if not isinstance(connectFlags, str):
            raise Exception("Connect Flags of CONNECT control package must be delivered as string!")

        # adding the required fields in order
        self.variableHeader.addFieldName("protocol_name_length")
        self.variableHeader.addFieldName("protocol_name")
        self.variableHeader.addFieldName("level")
        self.variableHeader.addFieldName("connect_flags")
        self.variableHeader.addFieldName("keep_alive")

        # modifying the fields
        # standard protocol name
        self.variableHeader.setField("protocol_name_length", 4, 2)
        self.variableHeader.setField("protocol_name", "MQTT", len("MQTT"))

        # standard level
        self.variableHeader.setField("level", 4, 1)

        # connect flags
        # username(0) | password(1) | will retain(2) | will Qos(3 - 4) | will flag(5) | cleanSesion(6) | reserved(7)
        self.variableHeader.setField("connect_flags", int(connectFlags, 2), 1)

        # keep alive
        self.variableHeader.setField("keep_alive", keepAlive, 2)

        # update components number
        self.componentsGenerated[1] = True

    def buildPayload(self, clientId, willTopic="", willMessage="", username="", password=""):
        if not self.componentsGenerated[1]:
            raise Exception("CONNECT control package: You must build the Variable Header component!")

        self.payload.addFieldName("client_identifier_length")
        self.payload.addFieldName("client_identifier")

        # aici identificatorul de client nu admite toate caracterele
        self.payload.setField("client_identifier_length", len(clientId), 2)
        self.payload.setField("client_identifier", clientId, len(clientId))

        # username(0) | password(1) | will retain(2) | will Qos(3 - 4) | will flag(5) | cleanSesion(6) | reserved(7)
        flags = str(format(self.variableHeader.getField("connect_flags"), '08b'))
        # will flag
        if flags[5] == "1":
            self.payload.addFieldName("will_topic_length")
            self.payload.addFieldName("will_topic")
            self.payload.setField("will_topic_length", len(willTopic), 2)
            self.payload.setField("will_topic", willTopic, len(willTopic))

            self.payload.addFieldName("will_message_length")
            self.payload.addFieldName("will_message")
            self.payload.setField("will_message_length", len(willMessage), 2)
            self.payload.setField("will_message", willMessage, len(willMessage))

        # username
        if flags[0] == "1":
            self.payload.addFieldName("username_length")
            self.payload.addFieldName("username")
            self.payload.setField("username_length", len(username), 2)
            self.payload.setField("username", username, len(username))

            # pasword
            if flags[1] == "1":
                self.payload.addFieldName("password_length")
                self.payload.addFieldName("password")
                self.payload.setField("password_length", len(password), 2)
                self.payload.setField("password", password, len(password))

        self.componentsGenerated[2] = True

    def getPackage(self):
        if not all(self.componentsGenerated):
            raise Exception("CONNECT control package: You must build all the components in this order (fixed header, "
                            "variable header, payload)!")

        # calculate the remaining size for the fixed header
        remainingSize = self.variableHeader.getSize() + self.payload.getSize()
        self.fixedHeader.setRemainingLength(remainingSize)

        # realizez package-ul aferent
        myPackage = ControlPackage(self.fixedHeader, self.variableHeader, self.payload)
        return myPackage
