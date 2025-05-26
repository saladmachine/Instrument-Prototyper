# SPDX-FileCopyrightText: 2025 Joe Pardue
#
# SPDX-License-Identifier: MIT

"""
Pico W 2 SD Card Initialization Example

This example demonstrates how to initialize and mount an SD card using the
Adafruit PiCowbell Adalogger for Pico W 2. It verifies that the SD card
is correctly detected and accessible, and lists the first few files found.

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
import os  # Required for os.listdir() to list files on the SD card

print("--- Starting SD Card Initialization Example ---")

try:
    # Initialize the SPI bus using the specific pins for the PiCowbell Adalogger.
    # The Pico W 2's GP pins (General Purpose) are used for SPI communication.
    spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=board.GP16)

    # Initialize the SD card using the SPI bus and the Chip Select (CS) pin.
    sd_card = sdcardio.SDCard(spi, board.GP17)

    # Create a VfsFat (Virtual File System) object for the SD card.
    vfs = storage.VfsFat(sd_card)

    # Mount the SD card into the CircuitPython file system at the '/sd' path.
    # This makes the SD card accessible like a regular directory.
    storage.mount(vfs, "/sd")

    print("SD Card successfully initialized and mounted at '/sd'!")

    # List up to the first 5 files/directories found on the SD card to confirm readability.
    print("\nFiles found on SD card (first 5 entries):")
    # os.listdir("/sd") returns a list of names of entries in the /sd directory.
    for i, entry in enumerate(os.listdir("/sd")):
        print(f"- {entry}")
        if i >= 4:  # Stop after listing 5 entries to keep output concise
            print("  ...")
            break
    if not os.listdir("/sd"):  # Check if the directory is empty
        print("  (No files found on SD card)")


except OSError as e:
    # Catch specific OS-related errors during SD card operation (e.g., card not found, bad format).
    print(f"\nError during SD Card Initialization: {e}")
    print("Troubleshooting Tips:")
    print("  - Ensure an SD card is correctly inserted into the PiCowbell Adalogger.")
    print(
        "  - Verify the SD card is formatted as FAT32 (most common for CircuitPython)."
    )
    print("  - Check all connections between the Pico W 2 and the PiCowbell Adalogger.")
except Exception as e:
    # Catch any other unexpected errors during the process.
    print(f"\nAn unexpected error occurred: {e}")
    print("Please review the traceback above for more details.")

print("\n--- SD Card Initialization Example Complete ---")

# Keep the program running indefinitely. In a real application,
# the code would continue to perform logging or other tasks.
while True:
    time.sleep(1)
