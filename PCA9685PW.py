#!/usr/bin/python

# from Adafruit_PWM_Servo_Driver import PWM
import time

import math
from Adafruit_I2C import Adafruit_I2C

# ============================================================================
# Adafruit PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685PW(object):
    # Registers/etc.
    __MODE1              = 0x00
    __MODE2              = 0x01
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALL_LED_ON_L       = 0xFA
    __ALL_LED_ON_H       = 0xFB
    __ALL_LED_OFF_L      = 0xFC
    __ALL_LED_OFF_H      = 0xFD

    # Bits
    __RESTART            = 0x80
    __SLEEP              = 0x10
    __ALLCALL            = 0x01
    __INVRT              = 0x10
    __OUTDRV             = 0x04

    general_call_i2c = Adafruit_I2C(0x00)

    @classmethod
    def softwareReset(cls):
        "Sends a software reset (SWRST) command to all the servo drivers on the bus"
        cls.general_call_i2c.writeRaw8(0x06)        # SWRST

    def __init__(self, address=0x40, quiet=False):
        self.i2c = Adafruit_I2C(address)
        self.address = address
        self.quiet = quiet
        if not self.quiet:
            print "Reseting PCA9685 MODE1 (without SLEEP) and MODE2"
        self.setAllPWM(0, 0)
        self.i2c.write8(self.__MODE2, self.__OUTDRV)
        self.i2c.write8(self.__MODE1, self.__ALLCALL)
        time.sleep(0.005)                                       # wait for oscillator

        mode1 = self.i2c.readU8(self.__MODE1)
        mode1 = mode1 & ~self.__SLEEP                 # wake up (reset sleep)
        self.i2c.write8(self.__MODE1, mode1)
        time.sleep(0.005)                             # wait for oscillator

    def setPWMFreq(self, freq):
        """ Sets the PWM frequency """
        self.freq = freq
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if not self.quiet:
            print "Setting PWM frequency to %d Hz" % freq
            print "Estimated pre-scale: %d" % prescaleval
        prescale = math.floor(prescaleval + 0.5)
        if not self.quiet:
            print "Final pre-scale: %d" % prescale

        oldmode = self.i2c.readU8(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10             # sleep
        self.i2c.write8(self.__MODE1, newmode)        # go to sleep
        self.i2c.write8(self.__PRESCALE, int(math.floor(prescale)))
        self.i2c.write8(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.i2c.write8(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.i2c.write8(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.i2c.write8(self.__LED0_ON_H+4*channel, on >> 8)
        self.i2c.write8(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.i2c.write8(self.__LED0_OFF_H+4*channel, off >> 8)

    def setAllPWM(self, on, off):
        "Sets a all PWM channels"
        self.i2c.write8(self.__ALL_LED_ON_L, on & 0xFF)
        self.i2c.write8(self.__ALL_LED_ON_H, on >> 8)
        self.i2c.write8(self.__ALL_LED_OFF_L, off & 0xFF)
        self.i2c.write8(self.__ALL_LED_OFF_H, off >> 8)

    def setServoPulse(self, channel, pulse):
        pulseLength = 1000000                   # 1,000,000 us per second
        pulseLength /= float(self.freq)         # e.g. 50 Hz
        if not self.quiet:
            print "%d us per period" % pulseLength
        pulseLength /= 4096.0                     # 12 bits of resolution
        if not self.quiet:
            print "%d us per bit" % pulseLength
        pulse *= 1000
        pulse /= pulseLength
        if not self.quiet:
            print pulse
        self.setPWM(channel, 0, int(pulse))

    def setServoAngle(self, channel, angle=0):
        """ frequency force to 50Hz (20ms),
        1.5ms => 0 degree, 0.5ms => -90 degree, 2.5ms => 90 degree """

        # define three key points
        pulse_0 = 1.5
        pulse_90 = 2.5
        pulse_270 = 0.5

        if 0<=angle<=90:
            pulse = 1.5 + angle * (pulse_90-pulse_0) / 90
        elif -90<=angle<0:
            pulse = 1.5 - angle * (pulse_270-pulse_0) / 90
        else:
            raise ValueError("angle Out of range")
        self.setServoPulse(channel, pulse)

    def setServoThrottle(self, channel, throttle=0):
        """ frequency force to 50Hz (20ms),
        1.5ms => halt, 0.5ms => reverse, 2.5ms => forward"""

        # define three key points
        thrust_0 = 1.5
        thrust_forward = 2.5
        thrust_reverse = 0.5

        if 0<=throttle<=100:
            thrust = thrust_0 + throttle * (thrust_forward-thrust_0) / 100
        elif -100<=throttle<0:
            thrust = thrust_0 - throttle * (thrust_reverse-thrust_0) / 90
        else:
            raise ValueError("thrust Out of range")
        self.setServoPulse(channel, thrust)

if __name__ == "__main__":
    # ===========================================================================
    # Example Code
    # ===========================================================================

    # Initialise the PWM device using the default address
    # pwm = PWM(0x40)
    # Note if you'd like more debug output you can instead run:
    pwm = PCA9685PW(0x40, quiet=False)

    pwm.setPWMFreq(50)                        # Set frequency to 60 Hz
    try:
        while (True):
            # Change speed of continuous servo on channel O
            # pwm.setPWM(7, 0, servooneeighty)
            # pwm.setPWM(1, 0, servoMin)
            # time.sleep(5)
            # pwm.setPWM(0, 0, servoninty)
            # time.sleep(5)
            # pwm.setPWM(0, 0, servooneeighty)
            # pwm.setPWM(1, 0, servoMax)
            # time.sleep(5)
            # pwm.setServoPulse(7, 2.5)
            # time.sleep(5)
            for i in range(-60, 61, 5):
                pwm.setServoAngle(7, i)
                time.sleep(1)
                pwm.setServoAngle(6, i)
                time.sleep(1)
            for i in range(60, -61, -5):
                pwm.setServoAngle(7, i)
                time.sleep(1)
                pwm.setServoAngle(6, i)
                time.sleep(1)
            time.sleep(5)

    except KeyboardInterrupt:
        pwm.softwareReset()


