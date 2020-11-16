# from base_components import *
# from package_builders import *
from package_encoder import *


if __name__ == "__main__":
    builder = UnsubscribeBuilder()
    builder.reset()
    builder.buildFixedHeader()
    builder.buildVariableHeader(25)
    builder.buildPayload(["Electrocasnice", "Masini", "Gaming"])

    unsubscribe = builder.getPackage()

    print(str(unsubscribe))

    encoder = GenericPackageEncoder()
    encodedText = encoder.encode(unsubscribe)

    displayControlPackageBinary(encodedText)

    decoder = GenericPackageDecoder()
    header = decoder.decodeFixedHeader(encodedText[0:16])
    unsubscribe_decoded = decoder.decodeVariableComponents(encodedText[16:], header)

    print(str(unsubscribe_decoded))

    if str(unsubscribe) == str(unsubscribe_decoded):
        print("We got a match!")



