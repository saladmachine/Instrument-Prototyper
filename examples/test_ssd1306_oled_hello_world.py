# SPDX-FileCopyrightText: 2025 Joe Pardue
#
# SPDX-License-Identifier: MIT

"""
Simple Hello World Test for Adafruit 938 OLED Display

Basic test to display "Hello, World!" text on the OLED using
the detected I2C address and STEMMA QT initialization.

Features:
- STEMMA QT I2C initialization
- SSD1306 display setup at detected address 0x3D
- Simple text display test

Hardware Requirements:
- Raspberry Pi Pico 2 W
- Adafruit 938 OLED Display (128x64, SSD1306)
- STEMMA QT connection

Library Dependencies:
Install in /lib folder:
- adafruit_displayio_ssd1306.mpy
- adafruit_display_text (folder)
- i2cdisplaybus.mpy

Usage:
1. Connect OLED via STEMMA QT connector
2. Install adafruit_ssd1306 library
3. Run this script to display "Hello, World!"

Integration Notes:
Basic display functionality test using the detected I2C address 0x3D
from the previous communication test.
"""

import board
import displayio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label
from i2cdisplaybus import I2CDisplayBus
import time


def hello_world_test():
    """
    Display Hello World on the OLED with continuous program control.

    Initializes the OLED and displays messages while maintaining continuous
    program execution to prevent CircuitPython console takeover. Simulates
    the behavior needed for instrument applications.

    Args:
        None

    Returns:
        None: Runs continuously until interrupted

    Raises:
        KeyboardInterrupt: When user stops the program
    """
    try:
        print("Initializing OLED display...")

        # Release any existing displays
        displayio.release_displays()

        # Use STEMMA I2C and detected address 0x3D
        i2c = board.STEMMA_I2C()
        display_bus = I2CDisplayBus(i2c, device_address=0x3D)

        # Create the display
        display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

        print("Display initialized successfully")

        # Create a display group and claim control immediately
        splash = displayio.Group()
        display.root_group = splash

        print("Starting continuous display test...")
        print("Press Ctrl+C to stop")

        # Continuous loop - simulates instrument behavior
        counter = 0
        while True:
            # Clear previous content
            while len(splash) > 0:
                splash.pop()

            if counter % 3 == 0:
                # Show Hello World
                text = label.Label(
                    terminalio.FONT, text="Hello, World!", color=0xFFFFFF, x=10, y=30
                )
                splash.append(text)
            elif counter % 3 == 1:
                # Show a different message
                text = label.Label(
                    terminalio.FONT, text="Instrument Ready", color=0xFFFFFF, x=5, y=30
                )
                splash.append(text)
            else:
                # Show counter (simulates changing data)
                text = label.Label(
                    terminalio.FONT,
                    text=f"Count: {counter//3}",
                    color=0xFFFFFF,
                    x=25,
                    y=30,
                )
                splash.append(text)

            time.sleep(2)  # Update every 2 seconds
            counter += 1

    except KeyboardInterrupt:
        print("\nProgram stopped by user")

        # Clean shutdown - show final message
        while len(splash) > 0:
            splash.pop()
        final_text = label.Label(
            terminalio.FONT, text="Program Stopped", color=0xFFFFFF, x=10, y=30
        )
        splash.append(final_text)
        time.sleep(2)

    except Exception as e:
        print(f"✗ Display test failed: {e}")


def main():
    """
    Main execution function for continuous operation.

    Runs the Hello World test in continuous mode to demonstrate
    proper display control for instrument applications.

    Args:
        None

    Returns:
        None

    Raises:
        Exception: Reports critical errors during execution
    """
    print("=" * 40)
    print("OLED HELLO WORLD TEST - CONTINUOUS MODE")
    print("=" * 40)
    print("This simulates instrument behavior")
    print("Display will cycle through messages")
    print("Press Ctrl+C to stop")
    print("=" * 40)

    try:
        hello_world_test()

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Critical error: {e}")

    print("Test completed")


if __name__ == "__main__":
    main()
