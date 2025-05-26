# test_rtc_interactive.py

# SPDX-FileCopyrightText: 2025 Joe Pardue
#
# SPDX-License-Identifier: MIT

"""
Interactive RTC Time Manager for Adalogger

This example demonstrates how to interactively manage the Real-Time Clock (RTC)
on an Adafruit Adalogger connected to a Raspberry Pi Pico W via STEMMA QT.
The program provides a menu-driven interface allowing users to view and set
the current date and time through the REPL serial terminal.

Features:
- Automatic detection of PCF8523, DS3231, or DS1307 RTC chips
- Interactive time setting with input validation
- Real-time display of current RTC time
- Menu-driven interface for easy operation
- Comprehensive error handling and user feedback

Hardware Requirements:
- Raspberry Pi Pico W or Pico W 2
- Adafruit Adalogger FeatherWing with RTC
- STEMMA QT connection cable
- CR1220 coin cell battery (for RTC backup power)

Library Dependencies:
Install one of the following RTC libraries in your /lib folder:
- adafruit_pcf8523 (for PCF8523 RTC - most common on Adalogger)
- adafruit_ds3231 (for DS3231 RTC)
- adafruit_ds1307 (for DS1307 RTC)

Usage:
1. Connect the Adalogger to your Pico W via STEMMA QT
2. Ensure the RTC battery is installed
3. Run this program and follow the interactive prompts
4. Use option 1 to set time, option 2 to view time, option 3 to exit

The program will automatically detect which RTC chip is present and use
the appropriate library. Time settings are persistent across power cycles
thanks to the battery backup.
"""

import board
import time
import sys


def get_user_input(prompt):
    """
    Get user input from REPL with proper prompt display.

    Args:
        prompt (str): The prompt message to display to the user

    Returns:
        str: User input string with whitespace stripped
    """
    print(prompt, end="")
    return input().strip()


def get_formatted_timestamp(rtc_device):
    """
    Get current RTC time as a formatted string.

    Args:
        rtc_device: The initialized RTC device object

    Returns:
        str: Formatted timestamp in YYYY-MM-DD HH:MM:SS format
    """
    current_rtc_time = rtc_device.datetime
    return f"{current_rtc_time.tm_year}-{current_rtc_time.tm_mon:02d}-{current_rtc_time.tm_mday:02d} {current_rtc_time.tm_hour:02d}:{current_rtc_time.tm_min:02d}:{current_rtc_time.tm_sec:02d}"


def set_rtc_time_interactive(rtc_device):
    """
    Interactive time setting function with input validation.

    Prompts the user to enter year, month, day, hour, minute, and second
    values with real-time validation. Shows the current RTC time before
    each input to provide visual feedback.

    Args:
        rtc_device: The initialized RTC device object

    Returns:
        bool: True if time was successfully set, False if cancelled or error
    """
    print("\n--- Setting RTC Time ---")
    print("Enter the current date and time:")

    try:
        # Get year with validation
        while True:
            current_time = get_formatted_timestamp(rtc_device)
            print(f"Current RTC time: {current_time}")
            year_str = get_user_input("Enter year (e.g., 2025): ")
            try:
                year = int(year_str)
                if 2020 <= year <= 2099:
                    break
                else:
                    print("Year must be between 2020 and 2099")
            except ValueError:
                print("Please enter a valid year")

        # Get month with validation
        while True:
            current_time = get_formatted_timestamp(rtc_device)
            print(f"Current RTC time: {current_time}")
            month_str = get_user_input("Enter month (1-12): ")
            try:
                month = int(month_str)
                if 1 <= month <= 12:
                    break
                else:
                    print("Month must be between 1 and 12")
            except ValueError:
                print("Please enter a valid month")

        # Get day with validation
        while True:
            current_time = get_formatted_timestamp(rtc_device)
            print(f"Current RTC time: {current_time}")
            day_str = get_user_input("Enter day (1-31): ")
            try:
                day = int(day_str)
                if 1 <= day <= 31:
                    break
                else:
                    print("Day must be between 1 and 31")
            except ValueError:
                print("Please enter a valid day")

        # Get hour with validation (24-hour format)
        while True:
            current_time = get_formatted_timestamp(rtc_device)
            print(f"Current RTC time: {current_time}")
            hour_str = get_user_input("Enter hour (0-23, 24-hour format): ")
            try:
                hour = int(hour_str)
                if 0 <= hour <= 23:
                    break
                else:
                    print("Hour must be between 0 and 23")
            except ValueError:
                print("Please enter a valid hour")

        # Get minute with validation
        while True:
            current_time = get_formatted_timestamp(rtc_device)
            print(f"Current RTC time: {current_time}")
            minute_str = get_user_input("Enter minute (0-59): ")
            try:
                minute = int(minute_str)
                if 0 <= minute <= 59:
                    break
                else:
                    print("Minute must be between 0 and 59")
            except ValueError:
                print("Please enter a valid minute")

        # Get second with validation
        while True:
            current_time = get_formatted_timestamp(rtc_device)
            print(f"Current RTC time: {current_time}")
            second_str = get_user_input("Enter second (0-59): ")
            try:
                second = int(second_str)
                if 0 <= second <= 59:
                    break
                else:
                    print("Second must be between 0 and 59")
            except ValueError:
                print("Please enter a valid second")

        # Confirm before setting the RTC
        print(
            f"\nYou entered: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
        )
        confirm = get_user_input("Is this correct? (y/n): ").lower()

        if confirm == "y" or confirm == "yes":
            # Create time structure and set the RTC time
            new_time = time.struct_time(
                (year, month, day, hour, minute, second, 0, 0, 0)
            )
            rtc_device.datetime = new_time

            print("RTC time has been set!")
            time.sleep(1)  # Wait for RTC to update

            # Verify and show the new time
            verify_time = get_formatted_timestamp(rtc_device)
            print(f"New RTC time: {verify_time}")
            return True
        else:
            print("Time setting cancelled.")
            return False

    except KeyboardInterrupt:
        print("\nTime setting cancelled by user.")
        return False
    except Exception as e:
        print(f"Error setting time: {e}")
        return False


def initialize_rtc():
    """
    Initialize the RTC device by trying multiple RTC chip types.

    Attempts to initialize PCF8523, DS3231, and DS1307 RTC chips in that order.
    Uses STEMMA QT I2C connection for communication.

    Returns:
        object: Initialized RTC device object, or None if initialization fails

    Raises:
        Exception: If no compatible RTC device is found
    """
    # Initialize I2C for the RTC using STEMMA QT
    i2c = board.STEMMA_I2C()
    print("I2C initialized using board.STEMMA_I2C().")

    rtc_device = None

    # Method 1: Try adafruit_pcf8523.pcf8523 (most common on Adalogger)
    try:
        from adafruit_pcf8523.pcf8523 import PCF8523

        rtc_device = PCF8523(i2c)
        print("RTC initialized using adafruit_pcf8523.pcf8523.PCF8523")
        return rtc_device
    except:
        pass

    # Method 2: Try direct import for PCF8523
    if rtc_device is None:
        try:
            import adafruit_pcf8523

            rtc_device = adafruit_pcf8523.pcf8523.PCF8523(i2c)
            print("RTC initialized using adafruit_pcf8523.pcf8523.PCF8523")
            return rtc_device
        except:
            pass

    # Method 3: Try DS3231 RTC library
    if rtc_device is None:
        try:
            import adafruit_ds3231

            rtc_device = adafruit_ds3231.DS3231(i2c)
            print("RTC initialized using DS3231 library")
            return rtc_device
        except:
            pass

    # Method 4: Try DS1307 RTC library
    if rtc_device is None:
        try:
            import adafruit_ds1307

            rtc_device = adafruit_ds1307.DS1307(i2c)
            print("RTC initialized using DS1307 library")
            return rtc_device
        except:
            pass

    # If we get here, no RTC was found
    if rtc_device is None:
        raise Exception("No compatible RTC device found")

    return rtc_device


def main_menu_loop(rtc_device):
    """
    Main interactive menu loop for RTC management.

    Provides options to set time, show current time, or exit the program.
    Continues until user chooses to exit or interrupts with Ctrl+C.

    Args:
        rtc_device: The initialized RTC device object
    """
    # Show initial time
    print(f"\nCurrent RTC time: {get_formatted_timestamp(rtc_device)}")

    # Main interactive loop
    while True:
        print("\n--- RTC Time Manager ---")
        print("Options:")
        print("  1 - Set time")
        print("  2 - Show current time")
        print("  3 - Exit")

        try:
            choice = get_user_input("Enter your choice (1-3): ")

            if choice == "1":
                success = set_rtc_time_interactive(rtc_device)
                if success:
                    print("Time successfully updated!")

            elif choice == "2":
                current_time = get_formatted_timestamp(rtc_device)
                print(f"Current RTC time: {current_time}")

            elif choice == "3":
                print("Exiting RTC Time Manager...")
                break

            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

        except KeyboardInterrupt:
            print("\nExiting RTC Time Manager...")
            break
        except Exception as e:
            print(f"Error: {e}")


# Main program execution
print("--- Interactive RTC Time Manager ---")

try:
    # Initialize the RTC device
    rtc_device = initialize_rtc()

    # Run the main menu loop
    main_menu_loop(rtc_device)

except Exception as e:
    print(f"Error during RTC initialization: {e}")
    print("Please ensure:")
    print("1. The Adalogger is connected via STEMMA QT connector.")
    print("2. The RTC battery is installed and functional.")
    print("3. The correct RTC library is installed in the lib folder.")

    import traceback

    traceback.print_exception(type(e), e, e.__traceback__)

print("--- RTC Time Manager Complete ---")

# Show final time if RTC was successfully initialized
try:
    if "rtc_device" in locals() and rtc_device is not None:
        final_time = get_formatted_timestamp(rtc_device)
        print(f"Final RTC time: {final_time}")
except:
    pass

# Keep program alive to maintain RTC connection
while True:
    time.sleep(1)
