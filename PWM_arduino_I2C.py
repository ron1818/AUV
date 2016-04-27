#! /usr/bin/python

# ren ye 2016-04-26
# user Arduino to generate motor and servo PWM signal
# assume PWM signal is 50Hz
# Arduino I2C slave 0x40
# it requires 4 bytes of data in: [MSB_degree, LSB_degree, MSB_rpm, LSB_rpm] format
# 2's complement

import smbus
import time
from bitstring import BitArray

bus = smbus.SMBus(1)

class PWM_Driver(object):
    """ send PWM signals to arduino via I2C """
    def __init__(self, addr, bits=16):
        self.addr = addr
        self.bits = bits

    def send_data(self,  *args):
        """ send integer data via I2C """
        payload=list()
        for arg in args:
            payload += self.extract_msb_lsb(arg, self.bits)
        print payload
        bus.write_i2c_block_data(self.addr, 0, payload)

    def extract_msb_lsb(self, val, bits):
        """ use bitstring.BitArray to convert and extract,
        auto two's complement"""

        # change value to binary string
        val_bitarray = BitArray(int=val, length=bits)
        # length of msb and lsb
        half_length = int(bits/2)
        # separate to msb and lsb, string
        msb, lsb = val_bitarray.bin[:half_length], val_bitarray.bin[half_length:]
        # convert back to integer so that i2c bus can send
        return [int(msb, 2), int(lsb, 2)]

if __name__ == "__main__":
    pwm_gen = PWM_Driver(0x04)
    pwm_gen.send_data(100, -15)
    time.sleep(10)
    pwm_gen.send_data(-100, 15)
    time.sleep(10)
    pwm_gen.send_data(10, 150)
    time.sleep(10)
    pwm_gen.send_data(-10, -150)
