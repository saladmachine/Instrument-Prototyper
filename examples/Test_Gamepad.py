# SPDX-FileCopyrightText: 2025 Joe Pardue
#
# SPDX-License-Identifier: MIT

"""
STEMMA QT Gamepad LED Blink Test

Simple test program for the Adafruit STEMMA QT Gamepad that blinks the
Pico W's built-in LED when any button is pressed or joystick is moved.
Demonstrates basic gamepad input detection and LED control.

Features:
- Gamepad initialization and communication
- Button press detection (6 buttons: X, Y, A, B, Start, Select)
- Joystick movement detection (2-axis analog input)
- LED blinking response to any input
- Continuous monitoring loop

Hardware Requirements:
- Raspberry Pi Pico 2 W
- Adafruit Mini I2C STEMMA QT Gamepad with seesaw (Product ID: 5743)
- STEMMA QT cable connection

Library Dependencies:
Install in /lib folder:
- adafruit_seesaw (folder)

Usage:
1. Connect gamepad via STEMMA QT cable
2. Install required libraries from Adafruit CircuitPython bundle
3. Run this program
4. Press buttons or move joystick to see LED blink
5. Press Ctrl+C to stop

Integration Notes:
This test demonstrates basic gamepad input handling suitable for
instrument control interfaces, menu navigation, and user input systems.
"""

import board
import digitalio
import time
from micropython import const
from adafruit_seesaw.seesaw import Seesaw

# =============================================================================
# GLOBAL CONFIGURATION
# =============================================================================

# Gamepad button pin definitions (seesaw firmware pins)
BUTTON_X = const(6)
BUTTON_Y = const(2)
BUTTON_A = const(5)
BUTTON_B = const(1)
BUTTON_SELECT = const(0)
BUTTON_START = const(16)

# Joystick analog pin definitions
JOYSTICK_X = const(14)  # X-axis analog input
JOYSTICK_Y = const(15)  # Y-axis analog input

# Button mask for bulk operations
BUTTON_MASK = const(
    (1 << BUTTON_X)
    | (1 << BUTTON_Y)
    | (1 << BUTTON_A)
    | (1 << BUTTON_B)
    | (1 << BUTTON_SELECT)
    | (1 << BUTTON_START)
)

# Gamepad I2C address (default)
GAMEPAD_I2C_ADDR = 0x50

# Joystick center values and deadzone
JOYSTICK_CENTER = 512  # Approximate center value for 10-bit ADC
JOYSTICK_DEADZONE = 50  # Movement threshold to ignore small variations

# LED blink timing
LED_BLINK_DURATION = 0.2  # Seconds to keep LED on

# Global hardware instances
gamepad = None
led = None
last_joystick_x = JOYSTICK_CENTER
last_joystick_y = JOYSTICK_CENTER

# =============================================================================
# HARDWARE SETUP FUNCTIONS
# =============================================================================


def setup_led():
    """
    Initialize the Pico W built-in LED.

    Configures the built-in LED as a digital output for visual feedback
    when gamepad inputs are detected.

    Args:
        None

    Returns:
        digitalio.DigitalInOut: LED control object or None if failed

    Raises:
        Exception: If LED initialization fails
    """
    global led

    try:
        print("Setting up Pico W LED...")
        led = digitalio.DigitalInOut(board.LED)
        led.direction = digitalio.Direction.OUTPUT
        led.value = False  # Start with LED off

        print("✓ LED initialized successfully")
        return led

    except Exception as e:
        print(f"✗ LED setup failed: {e}")
        return None


def setup_gamepad():
    """
    Initialize the STEMMA QT Gamepad.

    Sets up I2C communication with the gamepad and configures button
    inputs with pull-up resistors.

    Args:
        None

    Returns:
        Seesaw: Gamepad control object or None if failed

    Raises:
        Exception: If gamepad initialization fails
    """
    global gamepad

    try:
        print("Setting up STEMMA QT Gamepad...")

        # Initialize I2C using STEMMA connector
        i2c = board.STEMMA_I2C()

        # Create seesaw instance for gamepad
        gamepad = Seesaw(i2c, GAMEPAD_I2C_ADDR)

        print("Checking gamepad firmware...")

        # Verify correct firmware version (should be 5743 for gamepad)
        version = (gamepad.get_version() >> 16) & 0xFFFF
        if version != 5743:
            print(f"⚠ Warning: Unexpected firmware version {version}, expected 5743")
        else:
            print(f"✓ Gamepad firmware version {version} confirmed")

        # Configure button pins as inputs with pull-ups
        gamepad.pin_mode_bulk(BUTTON_MASK, gamepad.INPUT_PULLUP)

        print("✓ Gamepad initialized successfully")
        return gamepad

    except Exception as e:
        print(f"✗ Gamepad setup failed: {e}")
        return None


# =============================================================================
# INPUT DETECTION FUNCTIONS
# =============================================================================


def read_buttons():
    """
    Read all button states from the gamepad.

    Checks the state of all 6 buttons and returns which ones are currently
    pressed. Uses bulk reading for efficiency.

    Args:
        None

    Returns:
        dict: Dictionary with button names as keys and pressed state as values

    Raises:
        Exception: If button reading fails
    """
    try:
        # Read all button states at once
        buttons = gamepad.digital_read_bulk(BUTTON_MASK)

        # Convert to individual button states (buttons are active low)
        button_states = {
            "X": not bool(buttons & (1 << BUTTON_X)),
            "Y": not bool(buttons & (1 << BUTTON_Y)),
            "A": not bool(buttons & (1 << BUTTON_A)),
            "B": not bool(buttons & (1 << BUTTON_B)),
            "SELECT": not bool(buttons & (1 << BUTTON_SELECT)),
            "START": not bool(buttons & (1 << BUTTON_START)),
        }

        return button_states

    except Exception as e:
        print(f"Button read error: {e}")
        return {}


def read_joystick():
    """
    Read joystick position and detect movement.

    Reads the analog values from both joystick axes and determines if
    there has been significant movement from the center position.

    Args:
        None

    Returns:
        tuple: (x_value, y_value, movement_detected)

    Raises:
        Exception: If joystick reading fails
    """
    global last_joystick_x, last_joystick_y

    try:
        # Read analog values (0-1023 range)
        x_value = gamepad.analog_read(JOYSTICK_X)
        y_value = gamepad.analog_read(JOYSTICK_Y)

        # Check for significant movement from center
        x_movement = abs(x_value - JOYSTICK_CENTER) > JOYSTICK_DEADZONE
        y_movement = abs(y_value - JOYSTICK_CENTER) > JOYSTICK_DEADZONE

        # Also check for change from last reading
        x_change = abs(x_value - last_joystick_x) > (JOYSTICK_DEADZONE // 2)
        y_change = abs(y_value - last_joystick_y) > (JOYSTICK_DEADZONE // 2)

        movement_detected = x_movement or y_movement or x_change or y_change

        # Update last position
        last_joystick_x = x_value
        last_joystick_y = y_value

        return x_value, y_value, movement_detected

    except Exception as e:
        print(f"Joystick read error: {e}")
        return JOYSTICK_CENTER, JOYSTICK_CENTER, False


def check_any_input():
    """
    Check for any gamepad input (buttons or joystick).

    Combines button and joystick checking to detect any user input
    that should trigger the LED blink response.

    Args:
        None

    Returns:
        tuple: (input_detected, input_description)

    Raises:
        Exception: If input checking fails
    """
    input_detected = False
    input_description = ""

    try:
        # Check buttons
        button_states = read_buttons()
        pressed_buttons = [name for name, pressed in button_states.items() if pressed]

        if pressed_buttons:
            input_detected = True
            input_description = f"Buttons: {', '.join(pressed_buttons)}"

        # Check joystick
        x_val, y_val, joystick_moved = read_joystick()

        if joystick_moved:
            if input_detected:
                input_description += f" | Joystick: ({x_val}, {y_val})"
            else:
                input_detected = True
                input_description = f"Joystick: ({x_val}, {y_val})"

        return input_detected, input_description

    except Exception as e:
        print(f"Input check error: {e}")
        return False, "Error reading input"


# =============================================================================
# LED CONTROL FUNCTIONS
# =============================================================================


def blink_led(description="Input detected"):
    """
    Blink the LED in response to gamepad input.

    Turns on the LED briefly to provide visual feedback when any
    gamepad input is detected.

    Args:
        description (str): Description of the input that triggered the blink

    Returns:
        None

    Raises:
        Exception: If LED control fails
    """
    try:
        if led is not None:
            print(f"💡 LED BLINK: {description}")
            led.value = True
            time.sleep(LED_BLINK_DURATION)
            led.value = False
        else:
            print(f"LED not available: {description}")

    except Exception as e:
        print(f"LED blink error: {e}")


# =============================================================================
# MAIN TEST EXECUTION
# =============================================================================


def gamepad_test():
    """
    Main gamepad testing loop.

    Continuously monitors gamepad inputs and blinks LED when any
    button is pressed or joystick is moved. Runs until interrupted.

    Args:
        None

    Returns:
        None

    Raises:
        KeyboardInterrupt: When user stops the program
    """
    print("Starting gamepad input monitoring...")
    print("Press any button or move joystick to blink LED")
    print("Press Ctrl+C to stop")
    print("-" * 50)

    input_count = 0

    try:
        while True:
            # Check for any gamepad input
            input_detected, description = check_any_input()

            if input_detected:
                input_count += 1
                blink_led(f"#{input_count}: {description}")

                # Brief delay to avoid rapid repeated triggers
                time.sleep(0.1)
            else:
                # Small delay for main loop
                time.sleep(0.05)

    except KeyboardInterrupt:
        print(f"\nGamepad test stopped. Total inputs detected: {input_count}")

        # Turn off LED
        if led is not None:
            led.value = False


def main():
    """
    Main execution function.

    Sets up hardware and runs the gamepad test with proper error handling
    and cleanup.

    Args:
        None

    Returns:
        None

    Raises:
        Exception: Reports critical errors during execution
    """
    print("=" * 60)
    print("STEMMA QT GAMEPAD LED BLINK TEST")
    print("=" * 60)

    try:
        # Hardware setup
        if setup_led() is None:
            print("Failed to setup LED - continuing without LED feedback")

        if setup_gamepad() is None:
            print("Failed to setup gamepad - cannot continue")
            return

        print("\n✓ Hardware setup complete")
        print("Gamepad buttons: X, Y, A, B, Start, Select")
        print("Joystick: 2-axis analog input")
        print()

        # Run the test
        gamepad_test()

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        # Cleanup
        print("Cleaning up...")
        if led is not None:
            try:
                led.value = False
            except:
                pass
        print("Test completed")


if __name__ == "__main__":
    main()
