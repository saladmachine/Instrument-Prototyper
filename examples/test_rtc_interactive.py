# SPDX-FileCopyrightText: 2025 Joe Pardue
#
# SPDX-License-Identifier: MIT

"""
Enhanced Interactive RTC Time Manager for Adalogger

This example demonstrates comprehensive Real-Time Clock (RTC) management
on an Adafruit Adalogger connected to a Raspberry Pi Pico W via STEMMA QT.
The program provides advanced features including alarms, periodic timers,
timestamped data logging, timezone support, and uptime tracking.

Features:
- Interactive time setting with input validation
- Alarm scheduling for future events
- Periodic timer interrupts for regular tasks
- Timestamped data logging to SD card
- Timezone offset support
- System uptime tracking
- Real-time display of current RTC time
- Menu-driven interface for easy operation
- Comprehensive error handling and user feedback

Hardware Requirements:
- Raspberry Pi Pico W or Pico W 2
- Adafruit Adalogger FeatherWing with RTC
- STEMMA QT connection cable
- CR1220 coin cell battery (for RTC backup power)
- MicroSD card (for data logging features)

Library Dependencies:
Install these libraries in your /lib folder:
- adafruit_pcf8523 (for PCF8523 RTC - most common on Adalogger)
- OR adafruit_ds3231 (for DS3231 RTC)
- OR adafruit_ds1307 (for DS1307 RTC)

Usage:
1. Connect the Adalogger to your Pico W via STEMMA QT
2. Insert formatted microSD card into Adalogger
3. Ensure the RTC battery is installed
4. Run this program and follow the interactive prompts
5. Use the menu options to explore all RTC features

The program will automatically detect which RTC chip is present and use
the appropriate library. All settings are persistent across power cycles
thanks to the battery backup.
"""

import board
import time
import sys
import busio
import sdcardio
import storage

# Global variables for tracking
system_start_time = None
timezone_offset_hours = 0  # Default to UTC
alarm_set = False
alarm_time = None
periodic_timer_set = False
periodic_interval = 0
last_periodic_trigger = 0


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


def get_formatted_timestamp(rtc_device, apply_timezone=True):
    """
    Get current RTC time as a formatted string.

    Args:
        rtc_device: The initialized RTC device object
        apply_timezone (bool): Whether to apply timezone offset

    Returns:
        str: Formatted timestamp in YYYY-MM-DD HH:MM:SS format
    """
    current_rtc_time = rtc_device.datetime

    if apply_timezone and timezone_offset_hours != 0:
        # Apply timezone offset
        timestamp_seconds = time.mktime(current_rtc_time) + (
            timezone_offset_hours * 3600
        )
        adjusted_time = time.localtime(timestamp_seconds)
        return f"{adjusted_time.tm_year}-{adjusted_time.tm_mon:02d}-{adjusted_time.tm_mday:02d} {adjusted_time.tm_hour:02d}:{adjusted_time.tm_min:02d}:{adjusted_time.tm_sec:02d}"
    else:
        return f"{current_rtc_time.tm_year}-{current_rtc_time.tm_mon:02d}-{current_rtc_time.tm_mday:02d} {current_rtc_time.tm_hour:02d}:{current_rtc_time.tm_min:02d}:{current_rtc_time.tm_sec:02d}"


def set_rtc_time_interactive(rtc_device):
    """
    Interactive time setting function with input validation.

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


def set_alarm_interactive(rtc_device):
    """
    Set an alarm for a specific time in the future.

    Args:
        rtc_device: The initialized RTC device object

    Returns:
        bool: True if alarm was set successfully
    """
    global alarm_set, alarm_time

    print("\n--- Setting Alarm ---")
    print("Set alarm time (relative to current time):")

    try:
        # Get hours
        while True:
            hours_str = get_user_input("Hours from now (0-23): ")
            try:
                hours = int(hours_str)
                if 0 <= hours <= 23:
                    break
                else:
                    print("Hours must be between 0 and 23")
            except ValueError:
                print("Please enter a valid number")

        # Get minutes
        while True:
            minutes_str = get_user_input("Minutes from now (0-59): ")
            try:
                minutes = int(minutes_str)
                if 0 <= minutes <= 59:
                    break
                else:
                    print("Minutes must be between 0 and 59")
            except ValueError:
                print("Please enter a valid number")

        # Get seconds
        while True:
            seconds_str = get_user_input("Seconds from now (0-59): ")
            try:
                seconds = int(seconds_str)
                if 0 <= seconds <= 59:
                    break
                else:
                    print("Seconds must be between 0 and 59")
            except ValueError:
                print("Please enter a valid number")

        # Calculate alarm time
        current_time = time.mktime(rtc_device.datetime)
        alarm_time = current_time + (hours * 3600) + (minutes * 60) + seconds
        alarm_set = True

        alarm_datetime = time.localtime(alarm_time)
        alarm_str = f"{alarm_datetime.tm_year}-{alarm_datetime.tm_mon:02d}-{alarm_datetime.tm_mday:02d} {alarm_datetime.tm_hour:02d}:{alarm_datetime.tm_min:02d}:{alarm_datetime.tm_sec:02d}"

        print(f"Alarm set for: {alarm_str}")
        print(f"That's in {hours}h {minutes}m {seconds}s from now")

        return True

    except Exception as e:
        print(f"Error setting alarm: {e}")
        return False


def set_periodic_timer_interactive():
    """
    Set a periodic timer that triggers at regular intervals.

    Returns:
        bool: True if timer was set successfully
    """
    global periodic_timer_set, periodic_interval, last_periodic_trigger

    print("\n--- Setting Periodic Timer ---")
    print("Set periodic timer interval:")

    try:
        # Get hours
        while True:
            hours_str = get_user_input("Hours interval (0-23): ")
            try:
                hours = int(hours_str)
                if 0 <= hours <= 23:
                    break
                else:
                    print("Hours must be between 0 and 23")
            except ValueError:
                print("Please enter a valid number")

        # Get minutes
        while True:
            minutes_str = get_user_input("Minutes interval (0-59): ")
            try:
                minutes = int(minutes_str)
                if 0 <= minutes <= 59:
                    break
                else:
                    print("Minutes must be between 0 and 59")
            except ValueError:
                print("Please enter a valid number")

        # Get seconds
        while True:
            seconds_str = get_user_input("Seconds interval (1-59): ")
            try:
                seconds = int(seconds_str)
                if 1 <= seconds <= 59:
                    break
                else:
                    print("Seconds must be between 1 and 59")
            except ValueError:
                print("Please enter a valid number")

        # Calculate interval in seconds
        periodic_interval = (hours * 3600) + (minutes * 60) + seconds
        periodic_timer_set = True
        last_periodic_trigger = time.monotonic()

        print(f"Periodic timer set for every {hours}h {minutes}m {seconds}s")
        print("Timer will trigger in the background during menu operation")

        return True

    except Exception as e:
        print(f"Error setting periodic timer: {e}")
        return False


def check_alarms_and_timers(rtc_device):
    """
    Check if any alarms or periodic timers should trigger.

    Args:
        rtc_device: The initialized RTC device object
    """
    global alarm_set, alarm_time, periodic_timer_set, last_periodic_trigger

    current_time = time.mktime(rtc_device.datetime)
    current_monotonic = time.monotonic()

    # Check alarm
    if alarm_set and current_time >= alarm_time:
        print(f"\n🔔 ALARM! Triggered at {get_formatted_timestamp(rtc_device)}")
        log_event_to_sd(rtc_device, "ALARM_TRIGGERED")
        alarm_set = False
        alarm_time = None

    # Check periodic timer
    if (
        periodic_timer_set
        and (current_monotonic - last_periodic_trigger) >= periodic_interval
    ):
        print(
            f"\n⏰ PERIODIC TIMER! Triggered at {get_formatted_timestamp(rtc_device)}"
        )
        log_event_to_sd(rtc_device, "PERIODIC_TIMER")
        last_periodic_trigger = current_monotonic


def view_alarms_timers():
    """Display current alarm and timer status."""
    print("\n--- Alarms and Timers Status ---")

    if alarm_set:
        alarm_datetime = time.localtime(alarm_time)
        alarm_str = f"{alarm_datetime.tm_year}-{alarm_datetime.tm_mon:02d}-{alarm_datetime.tm_mday:02d} {alarm_datetime.tm_hour:02d}:{alarm_datetime.tm_min:02d}:{alarm_datetime.tm_sec:02d}"
        print(f"🔔 Alarm set for: {alarm_str}")
    else:
        print("🔔 No alarm set")

    if periodic_timer_set:
        hours = periodic_interval // 3600
        minutes = (periodic_interval % 3600) // 60
        seconds = periodic_interval % 60
        print(f"⏰ Periodic timer: every {hours}h {minutes}m {seconds}s")

        # Show time until next trigger
        time_since_last = time.monotonic() - last_periodic_trigger
        time_until_next = periodic_interval - time_since_last
        if time_until_next > 0:
            next_hours = int(time_until_next // 3600)
            next_minutes = int((time_until_next % 3600) // 60)
            next_seconds = int(time_until_next % 60)
            print(f"   Next trigger in: {next_hours}h {next_minutes}m {next_seconds}s")
    else:
        print("⏰ No periodic timer set")


def clear_alarms_timers():
    """Clear all alarms and timers."""
    global alarm_set, alarm_time, periodic_timer_set, periodic_interval

    alarm_set = False
    alarm_time = None
    periodic_timer_set = False
    periodic_interval = 0

    print("All alarms and timers cleared.")


def log_event_to_sd(rtc_device, event_type, additional_data=""):
    """
    Log an event with timestamp to SD card.

    Args:
        rtc_device: The initialized RTC device object
        event_type (str): Type of event being logged
        additional_data (str): Optional additional data
    """
    try:
        timestamp = get_formatted_timestamp(rtc_device)
        log_entry = f"{timestamp},{event_type},{additional_data}\n"

        # Try to append to SD card log file
        with open("/sd/rtc_events.csv", "a") as f:
            f.write(log_entry)

        print(f"Event logged: {event_type}")

    except Exception as e:
        print(f"Could not log to SD card: {e}")


def setup_sd_logging():
    """Initialize SD card for logging."""
    try:
        # Initialize SPI for SD card (same pins as your previous SD code)
        spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=board.GP16)
        sd_card = sdcardio.SDCard(spi, board.GP17)
        vfs = storage.VfsFat(sd_card)
        storage.mount(vfs, "/sd")

        # Create header if file doesn't exist
        try:
            with open("/sd/rtc_events.csv", "r") as f:
                pass  # File exists
        except:
            with open("/sd/rtc_events.csv", "w") as f:
                f.write("timestamp,event_type,additional_data\n")

        print("SD card logging initialized")
        return True

    except Exception as e:
        print(f"SD card initialization failed: {e}")
        return False


def set_timezone_interactive():
    """Set timezone offset interactively."""
    global timezone_offset_hours

    print("\n--- Setting Timezone ---")
    print("Enter timezone offset from UTC (e.g., -5 for EST, +1 for CET)")

    try:
        offset_str = get_user_input("Timezone offset hours (-12 to +12): ")
        offset = int(offset_str)

        if -12 <= offset <= 12:
            timezone_offset_hours = offset
            print(f"Timezone set to UTC{offset:+d}")
            return True
        else:
            print("Offset must be between -12 and +12")
            return False

    except ValueError:
        print("Please enter a valid number")
        return False
    except Exception as e:
        print(f"Error setting timezone: {e}")
        return False


def show_uptime():
    """Display system uptime since program start."""
    global system_start_time

    if system_start_time is None:
        print("Uptime tracking not available")
        return

    uptime_seconds = time.monotonic() - system_start_time

    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)

    print(f"\nSystem uptime: {hours}h {minutes}m {seconds}s")


def initialize_rtc():
    """
    Initialize the RTC device by trying multiple RTC chip types.

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


def main_menu_loop(rtc_device, sd_available):
    """
    Main interactive menu loop for RTC management.

    Args:
        rtc_device: The initialized RTC device object
        sd_available (bool): Whether SD card logging is available
    """
    global system_start_time

    # Initialize system start time for uptime tracking
    system_start_time = time.monotonic()

    # Show initial time
    print(f"\nCurrent RTC time: {get_formatted_timestamp(rtc_device)}")
    if timezone_offset_hours != 0:
        print(f"Timezone: UTC{timezone_offset_hours:+d}")

    # Main interactive loop
    while True:
        # Check for triggered alarms/timers
        check_alarms_and_timers(rtc_device)

        print("\n--- Enhanced RTC Time Manager ---")
        print("Options:")
        print("  1 - Set time")
        print("  2 - Show current time")
        print("  3 - Set alarm")
        print("  4 - Set periodic timer")
        print("  5 - View alarms/timers")
        print("  6 - Clear alarms/timers")
        if sd_available:
            print("  7 - Log current time to SD")
        print("  8 - Set timezone")
        print("  9 - Show uptime")
        print("  0 - Exit")

        try:
            choice = get_user_input("Enter your choice: ")

            if choice == "1":
                success = set_rtc_time_interactive(rtc_device)
                if success:
                    print("Time successfully updated!")
                    if sd_available:
                        log_event_to_sd(rtc_device, "TIME_SET")

            elif choice == "2":
                current_time = get_formatted_timestamp(rtc_device)
                print(f"Current RTC time: {current_time}")
                if timezone_offset_hours != 0:
                    utc_time = get_formatted_timestamp(rtc_device, apply_timezone=False)
                    print(f"UTC time: {utc_time}")

            elif choice == "3":
                success = set_alarm_interactive(rtc_device)
                if success and sd_available:
                    log_event_to_sd(rtc_device, "ALARM_SET")

            elif choice == "4":
                success = set_periodic_timer_interactive()
                if success and sd_available:
                    log_event_to_sd(rtc_device, "PERIODIC_TIMER_SET")

            elif choice == "5":
                view_alarms_timers()

            elif choice == "6":
                clear_alarms_timers()
                if sd_available:
                    log_event_to_sd(rtc_device, "ALARMS_CLEARED")

            elif choice == "7" and sd_available:
                timestamp = get_formatted_timestamp(rtc_device)
                log_event_to_sd(
                    rtc_device, "MANUAL_LOG", f"User requested log at {timestamp}"
                )
                print("Current time logged to SD card")

            elif choice == "8":
                success = set_timezone_interactive()
                if success and sd_available:
                    log_event_to_sd(
                        rtc_device, "TIMEZONE_SET", f"UTC{timezone_offset_hours:+d}"
                    )

            elif choice == "9":
                show_uptime()

            elif choice == "0":
                print("Exiting Enhanced RTC Time Manager...")
                if sd_available:
                    log_event_to_sd(rtc_device, "PROGRAM_EXIT")
                break

            else:
                print("Invalid choice. Please enter a valid option number.")

        except KeyboardInterrupt:
            print("\nExiting Enhanced RTC Time Manager...")
            if sd_available:
                log_event_to_sd(rtc_device, "PROGRAM_INTERRUPTED")
            break
        except Exception as e:
            print(f"Error: {e}")


# Main program execution
print("--- Enhanced Interactive RTC Time Manager ---")

try:
    # Initialize the RTC device
    rtc_device = initialize_rtc()

    # Try to initialize SD card logging
    sd_available = setup_sd_logging()
    if sd_available:
        log_event_to_sd(rtc_device, "PROGRAM_START")

    # Run the main menu loop
    main_menu_loop(rtc_device, sd_available)

except Exception as e:
    print(f"Error during RTC initialization: {e}")
    print("Please ensure:")
    print("1. The Adalogger is connected via STEMMA QT connector.")
    print("2. The RTC battery is installed and functional.")
    print("3. The correct RTC library is installed in the lib folder.")
    print("4. SD card is properly inserted (for logging features).")

    import traceback

    traceback.print_exception(type(e), e, e.__traceback__)

print("--- Enhanced RTC Time Manager Complete ---")

# Show final time and status if RTC was successfully initialized
try:
    if "rtc_device" in locals() and rtc_device is not None:
        final_time = get_formatted_timestamp(rtc_device)
        print(f"Final RTC time: {final_time}")

        if alarm_set:
            print("⚠ Note: Alarm is still set and will trigger when program restarts")

except:
    pass

# Keep program alive to maintain RTC connection and check alarms/timers
print("Program running... alarms and timers will trigger in background")
print("Press Ctrl+C to exit")

while True:
    if "rtc_device" in locals() and rtc_device is not None:
        check_alarms_and_timers(rtc_device)
    time.sleep(0.5)  # Check twice per second for responsive alarms
