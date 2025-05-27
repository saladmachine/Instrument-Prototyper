# SPDX-FileCopyrightText: 2025 Joe Pardue
#
# SPDX-License-Identifier: MIT

"""
STEMMA QT Gamepad OLED Display Test

Test program that displays gamepad input on the OLED screen. Shows the most
recent button press or joystick movement on the display and updates when new
input is detected. Demonstrates continuous operation without timeouts.

Features:
- Gamepad input detection (6 buttons + 2-axis joystick)
- OLED display output with real-time updates
- Persistent display of last input until new input detected
- No timeout - waits indefinitely for input
- Continuous program operation to maintain display control

Hardware Requirements:
- Raspberry Pi Pico 2 W
- Adafruit Mini I2C STEMMA QT Gamepad with seesaw (Product ID: 5743)
- Adafruit 938 OLED Display (128x64, SSD1306)
- STEMMA QT cable connections

Library Dependencies:
Install in /lib folder:
- adafruit_seesaw (folder)
- adafruit_displayio_ssd1306.mpy
- adafruit_display_text (folder)
- i2cdisplaybus.mpy

Usage:
1. Connect gamepad and OLED via STEMMA QT cables
2. Install required libraries from Adafruit CircuitPython bundle
3. Run this program
4. Press buttons or move joystick to see updates on OLED
5. Press Ctrl+C to stop

Integration Notes:
This demonstrates the display update pattern suitable for instrument
menu systems where the display shows current state and updates only
when user input is detected.
"""

import board
import displayio
import terminalio
import time
from micropython import const
from adafruit_seesaw.seesaw import Seesaw
import adafruit_displayio_ssd1306
from adafruit_display_text import label
from i2cdisplaybus import I2CDisplayBus

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

# Hardware I2C addresses
GAMEPAD_I2C_ADDR = 0x50
OLED_I2C_ADDR = 0x3D  # From previous test

# Display configuration
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64

# Joystick center values and deadzone
JOYSTICK_CENTER = 512  # Approximate center value for 10-bit ADC
JOYSTICK_DEADZONE = 100  # Movement threshold for detection

# Global hardware instances
gamepad = None
display = None
display_group = None
title_label = None
input_label = None
status_label = None
last_joystick_x = JOYSTICK_CENTER
last_joystick_y = JOYSTICK_CENTER

# =============================================================================
# HARDWARE SETUP FUNCTIONS
# =============================================================================


def setup_oled():
    """
    Initialize the OLED display.

    Sets up the OLED display using DisplayIO and creates the basic
    display layout with title, input, and status areas.

    Args:
        None

    Returns:
        bool: True if setup successful, False otherwise

    Raises:
        Exception: If OLED initialization fails
    """
    global display, display_group, title_label, input_label, status_label

    try:
        print("Setting up OLED display...")

        # Release any existing displays
        displayio.release_displays()

        # Use STEMMA I2C and detected address
        i2c = board.STEMMA_I2C()
        display_bus = I2CDisplayBus(i2c, device_address=OLED_I2C_ADDR)

        # Create the display
        display = adafruit_displayio_ssd1306.SSD1306(
            display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT
        )

        # Create display group and take control immediately
        display_group = displayio.Group()
        display.root_group = display_group

        # Create text labels for different areas of the screen
        title_label = label.Label(
            terminalio.FONT, text="Gamepad Test", color=0xFFFFFF, x=20, y=8
        )
        input_label = label.Label(
            terminalio.FONT, text="Press any button", color=0xFFFFFF, x=5, y=30
        )
        status_label = label.Label(
            terminalio.FONT, text="Ready", color=0xFFFFFF, x=5, y=50
        )

        # Add labels to display group
        display_group.append(title_label)
        display_group.append(input_label)
        display_group.append(status_label)

        print("✓ OLED display initialized successfully")
        return True

    except Exception as e:
        print(f"✗ OLED setup failed: {e}")
        return False


def setup_gamepad():
    """
    Initialize the STEMMA QT Gamepad.

    Sets up I2C communication with the gamepad and configures button
    inputs with pull-up resistors.

    Args:
        None

    Returns:
        bool: True if setup successful, False otherwise

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
        return True

    except Exception as e:
        print(f"✗ Gamepad setup failed: {e}")
        return False


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
        list: List of button names that are currently pressed

    Raises:
        Exception: If button reading fails
    """
    try:
        # Read all button states at once
        buttons = gamepad.digital_read_bulk(BUTTON_MASK)

        # Convert to list of pressed button names (buttons are active low)
        pressed_buttons = []

        if not (buttons & (1 << BUTTON_X)):
            pressed_buttons.append("X")
        if not (buttons & (1 << BUTTON_Y)):
            pressed_buttons.append("Y")
        if not (buttons & (1 << BUTTON_A)):
            pressed_buttons.append("A")
        if not (buttons & (1 << BUTTON_B)):
            pressed_buttons.append("B")
        if not (buttons & (1 << BUTTON_SELECT)):
            pressed_buttons.append("SELECT")
        if not (buttons & (1 << BUTTON_START)):
            pressed_buttons.append("START")

        return pressed_buttons

    except Exception as e:
        print(f"Button read error: {e}")
        return []


def read_joystick():
    """
    Read joystick position and detect movement.

    Reads the analog values from both joystick axes and determines if
    there has been significant movement from the center position.

    Args:
        None

    Returns:
        tuple: (x_value, y_value, movement_detected, direction)

    Raises:
        Exception: If joystick reading fails
    """
    global last_joystick_x, last_joystick_y

    try:
        # Read analog values (0-1023 range)
        x_value = gamepad.analog_read(JOYSTICK_X)
        y_value = gamepad.analog_read(JOYSTICK_Y)

        # Determine direction of movement
        direction = ""
        movement_detected = False

        # Check for significant movement from center
        if x_value < (JOYSTICK_CENTER - JOYSTICK_DEADZONE):
            direction += "LEFT "
            movement_detected = True
        elif x_value > (JOYSTICK_CENTER + JOYSTICK_DEADZONE):
            direction += "RIGHT "
            movement_detected = True

        if y_value < (JOYSTICK_CENTER - JOYSTICK_DEADZONE):
            direction += "UP"
            movement_detected = True
        elif y_value > (JOYSTICK_CENTER + JOYSTICK_DEADZONE):
            direction += "DOWN"
            movement_detected = True

        # Clean up direction string
        direction = direction.strip()
        if not direction and movement_detected:
            direction = "CENTER"

        # Update last position
        last_joystick_x = x_value
        last_joystick_y = y_value

        return x_value, y_value, movement_detected, direction

    except Exception as e:
        print(f"Joystick read error: {e}")
        return JOYSTICK_CENTER, JOYSTICK_CENTER, False, ""


# =============================================================================
# DISPLAY UPDATE FUNCTIONS
# =============================================================================


def update_display(input_text, status_text=""):
    """
    Update the OLED display with new input information.

    Updates the display labels to show the most recent input and
    optional status information.

    Args:
        input_text (str): Text describing the current input
        status_text (str): Optional status information

    Returns:
        None

    Raises:
        Exception: If display update fails
    """
    try:
        # Update input label
        input_label.text = input_text

        # Update status label if provided
        if status_text:
            status_label.text = status_text

        # Display updates automatically with DisplayIO

    except Exception as e:
        print(f"Display update error: {e}")


def display_startup_message():
    """
    Show startup message on display.

    Displays initial startup information and instructions for the user.

    Args:
        None

    Returns:
        None

    Raises:
        Exception: If display update fails
    """
    update_display("Waiting for input...", "Ready")


# =============================================================================
# MAIN TEST EXECUTION
# =============================================================================


def gamepad_display_test():
    """
    Main gamepad and display test loop.

    Continuously monitors gamepad inputs and updates the OLED display
    when any button is pressed or joystick is moved. Runs indefinitely
    without timeout until manually interrupted.

    Args:
        None

    Returns:
        None

    Raises:
        KeyboardInterrupt: When user stops the program
    """
    print("Starting gamepad display monitoring...")
    print("Press any button or move joystick to see updates on OLED")
    print("Display will show most recent input until new input detected")
    print("Press Ctrl+C to stop")
    print("-" * 60)

    input_count = 0
    last_input_description = ""

    # Show startup message on display
    display_startup_message()

    try:
        while True:
            input_detected = False
            input_description = ""

            # Check buttons
            pressed_buttons = read_buttons()
            if pressed_buttons:
                input_detected = True
                if len(pressed_buttons) == 1:
                    input_description = f"Button: {pressed_buttons[0]}"
                else:
                    input_description = f"Buttons: {'+'.join(pressed_buttons)}"

            # Check joystick
            x_val, y_val, joystick_moved, direction = read_joystick()
            if joystick_moved:
                if input_detected:
                    input_description += f" + Joy: {direction}"
                else:
                    input_detected = True
                    input_description = f"Joystick: {direction}"

            # Update display if new input detected
            if input_detected and input_description != last_input_description:
                input_count += 1
                status_text = f"Count: {input_count}"

                # Update display
                update_display(input_description, status_text)

                # Print to console as well
                print(f"#{input_count}: {input_description}")

                # Remember this input
                last_input_description = input_description

                # Brief delay to debounce inputs
                time.sleep(0.1)
            else:
                # Small delay for main loop - no timeout, just efficient polling
                time.sleep(0.05)

    except KeyboardInterrupt:
        print(f"\nGamepad display test stopped. Total inputs detected: {input_count}")

        # Show final message on display
        update_display("Test stopped", f"Total: {input_count}")
        time.sleep(2)


def main():
    """
    Main execution function.

    Sets up hardware and runs the gamepad display test with proper error
    handling and cleanup. Maintains continuous operation for instrument-style
    behavior.

    Args:
        None

    Returns:
        None

    Raises:
        Exception: Reports critical errors during execution
    """
    print("=" * 60)
    print("STEMMA QT GAMEPAD OLED DISPLAY TEST")
    print("=" * 60)

    try:
        # Hardware setup
        if not setup_oled():
            print("Failed to setup OLED - cannot continue")
            return

        if not setup_gamepad():
            print("Failed to setup gamepad - cannot continue")
            return

        print("\n✓ Hardware setup complete")
        print("Gamepad buttons: X, Y, A, B, Start, Select")
        print("Joystick: 2-axis analog input with direction detection")
        print("Display: Real-time input updates on OLED")
        print()

        # Run the test
        gamepad_display_test()

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        # Cleanup - show final message
        print("Cleaning up...")
        try:
            if display_group is not None:
                update_display("Program ended", "Goodbye!")
                time.sleep(1)
        except:
            pass
        print("Test completed")


if __name__ == "__main__":
    main()
