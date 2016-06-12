class SerialString(object):
    """ A namespace for static method that generate serial data.
    """
    @staticmethod
    def _chksum(msg):
        """ Returns the Sphero checksum for a tuple of message bytes.
        """
        return ~(sum(msg) % 256) & 0xFF

    @staticmethod
    def _formatsend(SOP1=0xFF, SOP2=0xFE, DID=0x02, CID=None, SEQ=0x00,
                    DLEN=None, DATA=None):
        """ Formats a send based on CID and DATA hex strings.
        """
        # We have to format the data first into 8-bit values (msB,lsB) etc.
        data = '{:0{}X}'.format(DATA, (DLEN - 1) * 2)
        data = tuple(bytearray(data.decode("hex")))

        # We can then assemble the basic message components
        summablemsg = (DID, CID, SEQ, DLEN) + data

        # Perform the checksum
        chksum = SerialString._chksum(summablemsg)

        # And return the complete message as a string of hex characters
        return ''.join(map(lambda byte: '{:02X}'.format(byte),
                           (SOP1, SOP2) + summablemsg + (chksum,)))

    @staticmethod
    def _pack(*args):
        """ Given 1 or more hex args put them in order then return the overall
            value.
        """
        total = 0
        # Reverse and iterage the args, multiplying them by 256 to the power
        # of i to make a large number
        for i, num in enumerate(args[::-1]):
            total += num * (256 ** i)
        return total

    @staticmethod
    def move(angle, speed):
        """ Generates serial data for movement at an angle
        """
        angle = min(angle, 359)
        angle = max(angle, 0)
        angle1 = 0
        angle2 = angle
        if angle2 > 255:
            angle1 = 1
            angle2 = angle2 - 256
        packed = SerialString._pack(speed, angle1, angle2, 1)
        hexstr = SerialString._formatsend(CID=0x30, DLEN=0x05, DATA=packed)
        return hexstr

    @staticmethod
    def stop():
        """ Generates serial data for movement.
        """
        packed = SerialString._pack(0, 0, 0, 1)
        hexstr = SerialString._formatsend(CID=0x30, DLEN=0x05, DATA=packed)
        return hexstr
