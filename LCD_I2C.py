#!/usr/bin/python
#--------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#  lcd_i2c.py
#  LCD test script using I2C backpack.
#  Supports 16x2 and 20x4 screens.
#
# Author : Matt Hawkins
# Date   : 20/09/2015
#
# http://www.raspberrypi-spy.co.uk/
#
# Copyright 2015 Matt Hawkins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#--------------------------------------

''' modified by Ren Ye, 20160331 to class file '''

import smbus
import time

# enable I2C bus
bus = smbus.SMBus(1)

class LCD_I2C(object):

    # commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    # flags for backlight control
    LCD_BACKLIGHT = 0x08
    LCD_NOBACKLIGHT = 0x00

    En = 0b00000100  # Enable bit
    Rw = 0b00000010  # Read/Write bit
    Rs = 0b00000001  # Register select bit

    # Define some device constants
    LCD_CHR = 1 # Mode - Sending data
    LCD_CMD = 0 # Mode - Sending command

    # line_addr = 0x80+0x40*y+x
    LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
    LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
    LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

    ENABLE = 0b00000100 # Enable bit

    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005

    def __init__(self, address, height = 4, width = 20):
        self.address = address
        self.height = height
        self.width = width

    def initialize(self, backlight = True):
        # Initialise display
        self.send_byte(0x33, self.LCD_CMD) # 110011 Initialise to 8-line mode first
        self.send_byte(0x32, self.LCD_CMD) # 110010 Initialise then to 4-line mode
        self.send_byte(0x06, self.LCD_CMD) # 000110 Cursor move direction
        self.send_byte(0x0C, self.LCD_CMD) # 001100 Display On ,Cursor Off, Blink Off 
        self.send_byte(0x28, self.LCD_CMD) # 101000 Data length, number of lines, font size, 2 Lines and 5*7 dots
        # if backlight:
        #     self.send_byte(self.LCD_BACKLIGHT,self.LCD_CMD)
        # else:
        #     self.send_byte(self.LCD_NOBACKLIGHT,self.LCD_CMD)
        self.send_byte(0x01, self.LCD_CMD) # 000001 Clear display
        time.sleep(self.E_DELAY)

    def clear_screen(self):
        self.send_byte(0x01, self.LCD_CMD) # 000001 Clear display

    def send_byte(self, bits, mode):
        # Send byte to data pins
        # bits = the data
        # mode = 1 for data
        #        0 for command

        bits_high = mode | (bits & 0xF0) | self.LCD_BACKLIGHT
        bits_low = mode | ((bits<<4) & 0xF0) | self.LCD_BACKLIGHT

        # High bits
        bus.write_byte(self.address, bits_high)
        self.toggle_enable(bits_high)

        # Low bits
        bus.write_byte(self.address, bits_low)
        self.toggle_enable(bits_low)

    def toggle_enable(self, bits):
        # Toggle enable
        time.sleep(self.E_DELAY)
        bus.write_byte(self.address, (bits | self.ENABLE))
        time.sleep(self.E_PULSE)
        bus.write_byte(self.address,(bits & ~self.ENABLE))
        time.sleep(self.E_DELAY)

    def send_string(self, message, line):
        # Send string to display
        if line > self.height:
            raise ValueError, "not enought lines"
        elif line == 1:
            LCD_LINE = self.LCD_LINE_1
        elif line == 2:
            LCD_LINE = self.LCD_LINE_2
        elif line == 3:
            LCD_LINE = self.LCD_LINE_3
        elif line == 4:
            LCD_LINE = self.LCD_LINE_4
        else:
            raise ValueError, "not supported line number"

        message = message.ljust(self.width," ")

        self.send_byte(LCD_LINE, self.LCD_CMD)

        for i in range(self.width):
            self.send_byte(ord(message[i]),self.LCD_CHR)

if __name__ == '__main__':
    try:
        LCD = LCD_I2C(0x3f)
        LCD.initialize()
        counter = 1
        while True:
            # Send some test
            LCD.send_string("Hello world", 1)
            LCD.send_string("lat: %d " % counter, 2)
            LCD.send_string("LINE 3             <", 3)
            LCD.send_string("line 4             <", 4)
            counter += 1
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        LCD.clear_screen();
