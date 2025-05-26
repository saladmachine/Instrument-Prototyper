# SPDX-FileCopyrightText: 2025 Joe Pardue
#
# SPDX-License-Identifier: MIT

"""
Pico W 2 SD Card File I/O Example

This example demonstrates fundamental file operations (write, read, append)
on an SD card connected via the Adafruit PiCowbell Adalogger for Pico W 2.
It creates a test file, writes initial data, reads it back, appends more data,
and then reads the file again to show the appended content.

Hardware Setup:
- Raspberry Pi Pico W 2
- Adafruit PiCowbell Adalogger for Pico
- MicroSD card (formatted as FAT32)

Connections (handled by PiCowbell; for reference, uses SPI0 pins):
- SCK (SPI Clock):   board.GP18
- MOSI (SPI Data Out): board.GP19
- MISO (SPI Data In):  board.GP16
- CS (Chip Select):    board.GP17
"""

import board
import busio
import sdcardio
import storage
import time
import os  # Required for os.remove() (if uncommented)

# --- Configuration ---
# Define the name and path for the test file on the SD card.
# The '/sd/' prefix refers to the mounted SD card.
TEST_FILE_NAME = "/sd/test_data.txt"
# --- End Configuration ---

print("--- Starting SD Card File I/O Example ---")

try:
    # Initialize the SPI bus using the specific pins for the PiCowbell Adalogger.
    spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=board.GP16)

    # Initialize the SD card module with the configured SPI bus and Chip Select pin.
    sd_card = sdcardio.SDCard(spi, board.GP17)

    # Create a VfsFat (Virtual File System) object for the SD card.
    vfs = storage.VfsFat(sd_card)

    # Mount the SD card into the CircuitPython file system at the '/sd' path.
    # After this, the SD card is accessible like a regular directory.
    storage.mount(vfs, "/sd")

    print("SD Card successfully initialized and mounted for file I/O.")

    # --- Test 1: Create a new file and write initial data ---
    print(f"\n--- Creating and writing new data to '{TEST_FILE_NAME}' ---")
    # 'w' mode: Opens the file for writing. If the file exists, it overwrites it.
    # If the file does not exist, it creates a new one.
    with open(TEST_FILE_NAME, "w") as f:
        f.write("Hello from CircuitPython!\n")
        f.write(f"Initial write timestamp: {time.monotonic()}\n")
        f.write("This is the first line of content.\n")
    print(f"Initial data written successfully to '{TEST_FILE_NAME}'.")

    # --- Test 2: Read data from the file ---
    print(f"\n--- Reading data from '{TEST_FILE_NAME}' ---")
    # 'r' mode: Opens the file for reading. The file must exist.
    with open(TEST_FILE_NAME, "r") as f:
        content = f.read() # Reads the entire content of the file.
        print("Content read from file:")
        print(content.strip()) # .strip() removes any leading/trailing whitespace (like extra newlines)

    # --- Test 3: Append data to the file ---
    print(f"\n--- Appending new data to '{TEST_FILE_NAME}' ---")
    # 'a' mode: Opens the file for appending. If the file exists, data is added to the end.
    # If the file does not exist, it creates a new one.
    with open(TEST_FILE_NAME, "a") as f:
        f.write(f"Appended at timestamp: {time.monotonic()}\n")
        f.write("This line was appended later.\n")
        f.write("And this is the final line of content.\n")
    print("New data appended successfully.")

    # --- Test 4: Read data after appending ---
    print(f"\n--- Reading data after appending from '{TEST_FILE_NAME}' ---")
    with open(TEST_FILE_NAME, "r") as f:
