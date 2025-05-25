# test_sd_file_io.py
# Test program for writing to and reading from a file on the SD card.

import board
import busio
import sdcardio
import storage
import time
import os  # Needed for os.listdir and os.remove

# --- Configuration ---
FILE_NAME = "/sd/test_data.txt"  # Path to the test file on the SD card
# -------------------

print("--- Starting SD Card File I/O Test ---")

try:
    # Define SPI pins for the PiCowbell Adalogger (same as test_sd_init.py)
    spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=board.GP16)
    sd_card = sdcardio.SDCard(spi, board.GP17)
    vfs = storage.VfsFat(sd_card)
    storage.mount(vfs, "/sd")

    print("SD Card successfully initialized and mounted for file I/O.")

    # --- Test 1: Create a new file and write data ---
    print(f"\n--- Writing new data to '{FILE_NAME}' ---")
    # Use 'w' mode for writing (creates file if it doesn't exist, overwrites if it does)
    with open(FILE_NAME, "w") as f:
        f.write("Hello from CircuitPython!\n")
        f.write(f"Timestamp: {time.monotonic()}\n")
    print("Data written successfully.")

    # --- Test 2: Read data from the file ---
    print(f"\n--- Reading data from '{FILE_NAME}' ---")
    # Use 'r' mode for reading
    with open(FILE_NAME, "r") as f:
        content = f.read()
        print("File Content:")
        print(content.strip())  # .strip() removes extra newlines

    # --- Test 3: Append data to the file ---
    print(f"\n--- Appending new data to '{FILE_NAME}' ---")
    # Use 'a' mode for appending
    with open(FILE_NAME, "a") as f:
        f.write(f"Appended at: {time.monotonic()}\n")
        f.write("More data here!\n")
    print("Data appended successfully.")

    # --- Test 4: Read data after appending ---
    print(f"\n--- Reading data after appending from '{FILE_NAME}' ---")
    with open(FILE_NAME, "r") as f:
        content_appended = f.read()
        print("File Content (after append):")
        print(content_appended.strip())

    # --- Optional: Clean up (uncomment to enable) ---
    # print(f"\n--- Deleting '{FILE_NAME}' ---")
    # os.remove(FILE_NAME)
    # print("File deleted.")

except Exception as e:
    print(f"Error during SD Card File I/O Test: {e}")
    print("Please ensure:")
    print(
        "1. An SD card is inserted into the PiCowbell Adalogger and properly formatted."
    )
    print("2. The PiCowbell Adalogger is correctly connected to the Pico W 2.")

print("--- SD Card File I/O Test Complete ---")

while True:
    time.sleep(1)
