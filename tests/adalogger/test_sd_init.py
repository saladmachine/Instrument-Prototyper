# test_sd_init.py
# Test program for initializing an SD card using the PiCowbell Adalogger pinout.

import board
import busio
import sdcardio
import storage
import time
import os

print("--- Starting SD Card Initialization Test ---")

# Define SPI pins for the PiCowbell Adalogger
# SCK (Clock)  = GP18
# MOSI (Data Out) = GP19
# MISO (Data In)  = GP16
# CS (Chip Select) = GP17

try:
    # Initialize SPI bus
    # Note: Raspberry Pi Pico's SPI interfaces are typically SPI0 (GPs 16-19)
    # and SPI1 (GPs 8-11). The PiCowbell uses pins that map to SPI0.
    spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=board.GP16)

    # Initialize SD card
    # The Chip Select (CS) pin for the SD card is GP17
    sd_card = sdcardio.SDCard(spi, board.GP17)

    # Mount the SD card as /sd/
    vfs = storage.VfsFat(sd_card)
    storage.mount(vfs, "/sd")

    print("SD Card successfully initialized and mounted!")
    print("Files on SD card (first 5):")
    # List up to 5 files/directories to confirm it's readable
    for i, entry in enumerate(os.listdir("/sd")):
        print(f"- {entry}")
        if i >= 4:  # Limit output to 5 entries
            print("...")
            break

except Exception as e:
    print(f"Error initializing SD Card: {e}")
    print("Please ensure:")
    print("1. An SD card is inserted into the PiCowbell Adalogger.")
    print("2. The PiCowbell Adalogger is correctly connected to the Pico W 2.")
    print("3. The SD card is formatted (FAT32 is recommended).")

print("--- SD Card Initialization Test Complete ---")

# The program will idle here.
while True:
    time.sleep(1)
