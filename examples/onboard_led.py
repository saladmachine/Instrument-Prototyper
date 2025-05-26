# SPDX-FileCopyrightText: 2025 Joe Pardue
#
# SPDX-License-Identifier: MIT
# Adding a changed comment for test purposes
"""
Pico W 2 Onboard LED Blinky Example

This example demonstrates how to control and blink the onboard LED of the
Raspberry Pi Pico W 2. It's a fundamental 'Hello World' for microcontrollers,
verifying basic digital output functionality.

The onboard LED on the Pico W 2 is connected to GPIO25, which CircuitPython
maps to `board.LED`.
"""

import board
import digitalio
import time

# --- Configuration ---
# Define the blink interval in seconds
BLINK_INTERVAL_SECONDS = 0.5
# --- End Configuration ---

print("--- Starting Onboard LED Blinky Example ---")
print("The onboard LED should blink on and off.")
print(f"Blink interval: {BLINK_INTERVAL_SECONDS} seconds.")
print("Press Ctrl+C in the REPL to stop the program.")

try:
    # Set up the onboard LED as a digital output.
    # On the Pico W 2, board.LED is an alias for board.GP25.
    onboard_led = digitalio.DigitalInOut(board.LED)
    onboard_led.direction = digitalio.Direction.OUTPUT

    while True:
        # Turn the LED on
        onboard_led.value = True
        print("LED ON")
        time.sleep(BLINK_INTERVAL_SECONDS)

        # Turn the LED off
        onboard_led.value = False
        print("LED OFF")
        time.sleep(BLINK_INTERVAL_SECONDS)

except KeyboardInterrupt:
    # This block executes if Ctrl+C is pressed in the REPL.
    print("\n--- Onboard LED Blinky Example Stopped ---")
    onboard_led.value = False  # Ensure the LED is off when exiting the program
except Exception as e:
    # Catch any other unexpected errors.
    print(f"\nAn unexpected error occurred: {e}")

# The program will idle here after completion or error.
while True:
    time.sleep(1)
