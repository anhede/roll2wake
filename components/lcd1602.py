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

    def disableBacklight(self):
        """
        Disable the backlight of the LCD.
        This is done by writing 0000001000 to the LCD address.
                                       D
        """
        self.bus.writeto(self.addr, bytearray([0b0000000000]))
        time.sleep(0.005)  # Wait for the backlight to turn off


    def enableBacklight(self):
        """
        Enable the backlight of the LCD.
        This is done by writing 0000001100 to the LCD address.
                                       D
        """
        self.bus.writeto(self.addr, bytearray([0b0000001100]))
        time.sleep(0.005)  # Wait for the backlight to turn on

    def enableCursor(self):
        """
        Enable the blinking cursor on the LCD.
        This is done by sending the command to show the cursor.
        """
        self.send_command(0x0F)  # Display ON, Cursor ON, Blink ON

    def disableCursor(self):
        """
        Disable the blinking cursor on the LCD.
        This is done by sending the command to hide the cursor.
        """
        self.send_command(0x0C)

    def setCursor(self, row, col):
        """
        Set the cursor position on a 20x4 LCD.
        :param row: Row number (0-3).
        :param col: Column number (0-19).
        """
        # DDRAM start offsets for each line on a 20×4 display
        row_offsets = [0x00, 0x40, 0x14, 0x54]

        # Optionally clamp or raise if out of bounds:
        if not (0 <= row < len(row_offsets)) or not (0 <= col < 20):
            raise ValueError("Row must be 0-3 and col must be 0-19")

        # 0x80 is the "set DDRAM address" command
        addr = 0x80 + row_offsets[row] + col
        self.send_command(addr)

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
        # DDRAM start addresses for a 20×4 display
        line_addresses = [0x00, 0x40, 0x14, 0x54]

        # Break up the text into lines
        lines = text.split("\n")

        # For each line, move the cursor to its start and write characters
        for row, line in enumerate(lines):
            if row >= len(line_addresses):
                break  # ignore anything past 4 lines—or wrap, if you prefer

            # send_command = 0x80 OR’d with the DDRAM address
            self.send_command(0x80 | line_addresses[row])

            for ch in line:
                self.send_data(ord(ch))

if __name__ == "__main__":
    from machine import I2C, Pin
    from components.pins import PIN_SCREEN_SDA, PIN_SCREEN_SCL

    # Initialize I2C communication;
    # Set SDA to pin 20, SCL to pin 21, and frequency to 400kHz
    i2c = I2C(0, sda=Pin(PIN_SCREEN_SDA), scl=Pin(PIN_SCREEN_SCL), freq=400000)

    # Create an LCD object for interfacing with the LCD1602 display
    lcd = LCD(i2c)

    #
    rows = 4
    msg = '\n'.join([f"Line {i+1}:" for i in range(rows)])
    lcd.message(msg)
    time.sleep(2)  # Wait for 2 seconds
    lcd.clear()  # Clear the display


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
    time.sleep(2)

    # Test cursor visibility
    lcd.enableCursor()  # Show the cursor
    for y in range(2):
        for x in range(16):
            lcd.setCursor(y, x)
            time.sleep(1)
    lcd.disableCursor()  # Hide the cursor
    
    # Toggle the backlight on and off
    while True:
        # Clear the display before exiting
        lcd.disableBacklight()  # Turn off the backlight
        time.sleep(2)  # Wait for a second before re-enabling backlight
        lcd.enableBacklight()  # Turn on the backlight again
        time.sleep(2)