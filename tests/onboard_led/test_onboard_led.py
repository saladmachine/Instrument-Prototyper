# test_onboard_led.py
# Test program for the Pico W's onboard LED.

import board
import digitalio
import time

# Set up the onboard LED as an output
# The onboard LED is usually connected to board.LED
# On Pico W, it's connected to GPIO25, which CircuitPython maps to board.LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

print("--- Starting Onboard LED Test ---")
print("The onboard LED should blink on and off.")
print("Press Ctrl+C in the REPL to stop.")

try:
    while True:
        led.value = True  # Turn LED on
        print("LED ON")
        time.sleep(0.5)  # Wait for 0.5 seconds

        led.value = False  # Turn LED off
        print("LED OFF")
        time.sleep(0.5)  # Wait for 0.5 seconds

except KeyboardInterrupt:
    print("\n--- Onboard LED Test Stopped ---")
    led.value = False  # Ensure LED is off when program exits
