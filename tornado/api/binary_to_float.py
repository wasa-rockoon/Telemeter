import struct

def binary_to_float(binary):
    """
    Converts a binary string to a double.
    """
    # Check if the binary contains the correct number of bytes
    if len(binary) != 4:
        raise ValueError("Binary string must be 4 bytes long " + str(len(binary)) + " bytes long")
    
    return struct.unpack('f', binary)[0]