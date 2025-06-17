# This file is part of the Universal Maker Sensor Kit by SunFounder, Inc.
# Original author: Mike Huang (CEO, SunFounder, Inc.)
# Original license: GNU General Public License v2 or later (GPL-2.0-or-later)
# 
# This code was originally published under the GPL and is reused here
# in accordance with its terms. It may have been modified for use in
# an open source course project.
#
# Source: https://docs.sunfounder.com/projects/umsk/en/latest/04_pi_pico/pico_lesson26_lcd.html
# License details: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
#
# Copyright (C) 2015 SunFounder, Inc.

# Modifications made by Josef Anhede on 2025-06-17

import time

class LCD:
    def __init__(self, i2c, addr=None, blen=1):
        self.bus = i2c
        self.addr = self.scanAddress(addr)
        self.blen = blen
        self.send_command(0x33)  # Must initialize to 8-line mode at first
        time.sleep(0.005)
        self.send_command(0x32)  # Then initialize to 4-line mode
        time.sleep(0.005)
        self.send_command(0x28)  # 2 Lines & 5*7 dots
        time.sleep(0.005)
        self.send_command(0x0C)  # Enable display without cursor
        time.sleep(0.005)
        self.send_command(0x01)  # Clear Screen
        self.bus.writeto(self.addr, bytearray([0x08]))

    def scanAddress(self, addr):
        devices = self.bus.scan()
        if len(devices) == 0:
            raise Exception("No LCD found")
        if addr is not None:
            if addr in devices:
                return addr
            else:
                raise Exception(f"LCD at 0x{addr:2X} not found")
        elif 0x27 in devices:
            return 0x27
        elif 0x3F in devices:
            return 0x3F
        else:
            raise Exception("No LCD found")

    def write_word(self, data):
        temp = data
        if self.blen == 1:
            temp |= 0x08
        else:
            temp &= 0xF7
        self.bus.writeto(self.addr, bytearray([temp]))

    def send_command(self, cmd):
        # Send bit7-4 firstly
        buf = cmd & 0xF0
        buf |= 0x04  # RS = 0, RW = 0, EN = 1
        self.write_word(buf)
        time.sleep(0.002)
        buf &= 0xFB  # Make EN = 0
        self.write_word(buf)

        # Send bit3-0 secondly
        buf = (cmd & 0x0F) << 4
        buf |= 0x04  # RS = 0, RW = 0, EN = 1
        self.write_word(buf)
        time.sleep(0.002)
        buf &= 0xFB  # Make EN = 0
        self.write_word(buf)

    def send_data(self, data):
        # Send bit7-4 firstly
        buf = data & 0xF0
        buf |= 0x05  # RS = 1, RW = 0, EN = 1
        self.write_word(buf)
        time.sleep(0.002)
        buf &= 0xFB  # Make EN = 0
        self.write_word(buf)

        # Send bit3-0 secondly
        buf = (data & 0x0F) << 4
        buf |= 0x05  # RS = 1, RW = 0, EN = 1
        self.write_word(buf)
        time.sleep(0.002)
        buf &= 0xFB  # Make EN = 0
        self.write_word(buf)

    def clear(self):
        self.send_command(0x01)  # Clear Screen

    def openlight(self):  # Enable the backlight
        self.bus.writeto(self.addr, bytearray([0x08]))
        # self.bus.close()

    def write(self, x, y, str):
        if x < 0:
            x = 0
        if x > 15:
            x = 15
        if y < 0:
            y = 0
        if y > 1:
            y = 1

        # Move cursor
        addr = 0x80 + 0x40 * y + x
        self.send_command(addr)

        for chr in str:
            self.send_data(ord(chr))

    def message(self, text):
        # print("message: %s"%text)
        for char in text:
            if char == "\n":
                self.send_command(0xC0)  # next line
            else:
                self.send_data(ord(char))

if __name__ == "__main__":
    from machine import I2C, Pin

    # Initialize I2C communication;
    # Set SDA to pin 20, SCL to pin 21, and frequency to 400kHz
    i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=400000)

    # Create an LCD object for interfacing with the LCD1602 display
    lcd = LCD(i2c)

    # Display the first message on the LCD
    # Use '\n' to create a new line.
    string = "SunFounder\n    LCD Tutorial"
    lcd.message(string)
    # Wait for 2 seconds
    time.sleep(2)
    # Clear the display
    lcd.clear()

    # Display the second message on the LCD
    string = "Hello\n  World!"
    lcd.message(string)
    # Wait for 5 seconds
    time.sleep(5)
    # Clear the display before exiting
    lcd.clear()