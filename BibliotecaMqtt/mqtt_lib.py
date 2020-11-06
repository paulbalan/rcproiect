# from base_components import *
# from package_builders import *
from package_encoder import *


if __name__ == "__main__":

    connectPackageBuilder = ConnectBuilder()
    connectPackageBuilder.reset()
    connectPackageBuilder.buildFixedHeader()
    connectPackageBuilder.buildVariableHeader("11000100", 20)
    connectPackageBuilder.buildPayload("Client - 1", username="vladbatalan", password="betivaneala",
                                       willTopic="register", willMessage="display credentials")
    connectControlPackage = connectPackageBuilder.getPackage()

    print("Original package:")
    print(str(connectControlPackage))

    myEncoder = GenericPackageEncoder()
    myDecoder = GenericPackageDecoder()
    text = myEncoder.encode(connectControlPackage)
    print("Encoded package:")
    displayControlPackageBinary(text)

    decodedPackage = myDecoder.decodeVariableComponents(text[16:], myDecoder.decodeFixedHeader(text[0:16]))
    print("Decoded Package:")
    print(str(decodedPackage))

    if str(connectControlPackage) == str(decodedPackage):
        print("There is a match!")