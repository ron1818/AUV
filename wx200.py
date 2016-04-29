import time
import serial
import pynmea2
from SC16IS750_I2C import *


class WX200_UART(object):
    """ Furono WX200 (airmar made) weather station,
    It is connected via RS442 (+- 5V) with NMEA0183 protocol,
    the adaptor can be
    1. X205 RPi shield with MAX485 connected to /dev/ttyAMA0
    2. RPi connected to SC16IS750 via I2C, then SC16IS750 connected to
    MAX 485 via TTL
    These two options are used in this class as 'UART' (default) or 'I2C'
    """

    def __init__(self, port, baud, parity='N', stopbits=1, bytesize=8, timeout=5):
        self.conn = serial.Serial(
                port=port,
                baudrate=baud,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                timeout=timeout)
    
    def __str__(self):
        return self.conn.readline()


class WX200(WX200_UART, SC16IS750):
    """ Furono WX200 (airmar made) weather station,
    It is connected via RS442 (+- 5V) with NMEA0183 protocol,
    the adaptor can be
    1. X205 RPi shield with MAX485 connected to /dev/ttyAMA0
    2. RPi connected to SC16IS750 via I2C, then SC16IS750 connected to
    MAX 485 via TTL
    These two options are used in this class as 'UART' (default) or 'I2C'
    """
    def __init__(self, address=None, busnum=-1, debug=False, baud=4800, \
            port=None, parity='N', stopbits=1, bytesize=8, timeout=5, config='UART'):
        """ both uart and I2c interface, uart has higher piority """
        self.config = config
        if port is None: # no UART connection
            self.config = 'I2C'
        elif address is None: # no I2C address
            self.config = 'UART'
        else:
            print "No valid connection"

        if self.config is 'I2C':
            SC16IS750.__init__(self, address, busnum, debug, baud)
        else: # default
            WX200_UART.__init__(self, port, baud, parity, stopbits, bytesize, timeout)
    
    def __str__(self):
        if self.config is 'I2C':
            return SC16IS750.__str__(self)
        else:
            return WX200_UART.__str__(self)

if __name__ == "__main__":
    WX200 = WX200(port="/dev/ttyAMA0", baud=4800) #, config='UART')
    # WX200 = WX200(address=0x4d, baud = 4800, config ='I2C')
    
    while True:
        print WX200
