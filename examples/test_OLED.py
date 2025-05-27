# SPDX-FileCopyrightText: 2025 Joe Pardue
#
# SPDX-License-Identifier: MIT

"""
Simple Test Suite for Adafruit 938 OLED Display (128x64 SSD1306)

Basic functionality testing for the Adafruit 938 OLED display to verify
text and graphics output capabilities. Tests the core display functions
to ensure proper operation with CircuitPython.

Features:
- Display initialization and I2C communication
- Text rendering and positioning
- Basic graphics primitives (pixels, lines, shapes)
- Display clearing and updating
- Power control functions

Hardware Requirements:
- Raspberry Pi Pico 2 W
- Adafruit 938 OLED Display (128x64, SSD1306, I2C)
- I2C connections: SDA to GP0, SCL to GP1, VCC to 3V3, GND to GND

Library Dependencies:
Install these libraries in your /lib folder:
- adafruit_ssd1306.mpy (SSD1306 display driver)
- adafruit_bus_device (I2C communication)

Usage:
1. Connect the OLED display via I2C
2. Copy this file to your Pico 2 W
3. Install required libraries from Adafruit CircuitPython bundle
4. Run the test and observe display output

Integration Notes:
This test validates basic OLED functionality for any CircuitPython project
requiring a simple monochrome display for status and data output.
"""

import board
import busio
import time
import adafruit_ssd1306

# =============================================================================
# GLOBAL CONFIGURATION
# =============================================================================

# Display Configuration
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64
DISPLAY_I2C_ADDR = 0x3C  # Default address, try 0x3D if this fails

# Hardware pins
SDA_PIN = board.GP0
SCL_PIN = board.GP1

# Global variables for hardware instances
i2c = None
display = None

# =============================================================================
# HARDWARE SETUP FUNCTIONS
# =============================================================================


def setup_hardware():
    """
    Initialize I2C bus and OLED display.

    Sets up the I2C communication and creates the display instance
    for testing. Handles common initialization errors.

    Args:
        None

    Returns:
        bool: True if setup successful, False otherwise

    Raises:
        RuntimeError: If I2C or display initialization fails
    """
    global i2c, display

    try:
        print("Setting up I2C bus...")
        i2c = busio.I2C(SCL_PIN, SDA_PIN)

        print("Initializing OLED display...")
        display = adafruit_ssd1306.SSD1306_I2C(
            DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c, addr=DISPLAY_I2C_ADDR
        )

        # Test basic functionality
        display.fill(0)
        display.show()

        print("Hardware setup successful")
        return True

    except Exception as e:
        print(f"Hardware setup failed: {e}")
        return False


# =============================================================================
# TEST FUNCTIONS
# =============================================================================


def test_display_clear():
    """
    Test display clearing functionality.

    Verifies that the display can be cleared to black and white,
    and that changes are properly shown on the display.

    Args:
        None

    Returns:
        bool: True if clearing works correctly

    Raises:
        Exception: If display operations fail
    """
    print("Testing display clear...")

    try:
        # Clear to black
        display.fill(0)
        display.show()
        time.sleep(1)

        # Fill white
        display.fill(1)
        display.show()
        time.sleep(1)

        # Clear to black
        display.fill(0)
        display.show()

        print("✓ Display clear test passed")
        return True

    except Exception as e:
        print(f"✗ Display clear test failed: {e}")
        return False


def test_text_output():
    """
    Test text rendering at various positions.

    Validates text display functionality including positioning,
    multiple lines, and edge cases for text placement.

    Args:
        None

    Returns:
        bool: True if text rendering works correctly

    Raises:
        Exception: If text operations fail
    """
    print("Testing text output...")

    try:
        display.fill(0)

        # Test basic text
        display.text("Hello World!", 0, 0, 1)
        display.text("Line 2", 0, 10, 1)
        display.text("Line 3", 0, 20, 1)

        # Test positioning
        display.text("Center", 40, 30, 1)
        display.text("Bottom", 20, 55, 1)

        display.show()
        time.sleep(3)

        print("✓ Text output test passed")
        return True

    except Exception as e:
        print(f"✗ Text output test failed: {e}")
        return False


def test_pixel_graphics():
    """
    Test individual pixel drawing.

    Verifies pixel-level graphics by drawing individual pixels
    at various positions including corners and center.

    Args:
        None

    Returns:
        bool: True if pixel operations work correctly

    Raises:
        Exception: If pixel operations fail
    """
    print("Testing pixel graphics...")

    try:
        display.fill(0)

        # Draw corner pixels
        display.pixel(0, 0, 1)  # Top-left
        display.pixel(DISPLAY_WIDTH - 1, 0, 1)  # Top-right
        display.pixel(0, DISPLAY_HEIGHT - 1, 1)  # Bottom-left
        display.pixel(DISPLAY_WIDTH - 1, DISPLAY_HEIGHT - 1, 1)  # Bottom-right

        # Draw center cross
        center_x = DISPLAY_WIDTH // 2
        center_y = DISPLAY_HEIGHT // 2

        for i in range(-5, 6):
            display.pixel(center_x + i, center_y, 1)
            display.pixel(center_x, center_y + i, 1)

        display.show()
        time.sleep(2)

        print("✓ Pixel graphics test passed")
        return True

    except Exception as e:
        print(f"✗ Pixel graphics test failed: {e}")
        return False


def test_line_graphics():
    """
    Test line drawing functions.

    Validates horizontal and vertical line drawing capabilities
    with various lengths and positions.

    Args:
        None

    Returns:
        bool: True if line drawing works correctly

    Raises:
        Exception: If line operations fail
    """
    print("Testing line graphics...")

    try:
        display.fill(0)

        # Horizontal lines
        display.hline(10, 10, 50, 1)
        display.hline(10, 20, 30, 1)

        # Vertical lines
        display.vline(70, 10, 40, 1)
        display.vline(80, 10, 20, 1)

        # Grid pattern
        for i in range(0, DISPLAY_WIDTH, 16):
            display.vline(i, 45, 15, 1)

        for i in range(45, 60, 5):
            display.hline(0, i, DISPLAY_WIDTH, 1)

        display.show()
        time.sleep(2)

        print("✓ Line graphics test passed")
        return True

    except Exception as e:
        print(f"✗ Line graphics test failed: {e}")
        return False


def test_shape_graphics():
    """
    Test rectangle drawing functions.

    Validates rectangle outline and filled rectangle drawing
    with various sizes and positions.

    Args:
        None

    Returns:
        bool: True if shape drawing works correctly

    Raises:
        Exception: If shape operations fail
    """
    print("Testing shape graphics...")

    try:
        display.fill(0)

        # Rectangle outlines
        display.rect(5, 5, 30, 20, 1)
        display.rect(40, 5, 25, 15, 1)

        # Filled rectangles
        display.fill_rect(70, 5, 20, 25, 1)
        display.fill_rect(95, 10, 15, 15, 1)

        # Nested rectangles
        display.rect(10, 35, 50, 25, 1)
        display.rect(15, 40, 40, 15, 1)
        display.fill_rect(20, 45, 30, 5, 1)

        display.show()
        time.sleep(2)

        print("✓ Shape graphics test passed")
        return True

    except Exception as e:
        print(f"✗ Shape graphics test failed: {e}")
        return False


def test_power_functions():
    """
    Test display power control functions.

    Validates power on/off and invert functions which are
    known to work on the Adafruit 938 display.

    Args:
        None

    Returns:
        bool: True if power functions work correctly

    Raises:
        Exception: If power control fails
    """
    print("Testing power functions...")

    try:
        # Test display with some content
        display.fill(0)
        display.text("Power Test", 20, 25, 1)
        display.show()
        time.sleep(1)

        # Test invert
        display.invert(True)
        time.sleep(1)
        display.invert(False)
        time.sleep(1)

        # Test power off/on
        display.poweroff()
        time.sleep(2)
        display.poweron()
        time.sleep(1)

        print("✓ Power functions test passed")
        return True

    except Exception as e:
        print(f"✗ Power functions test failed: {e}")
        return False


def test_animation():
    """
    Test simple animation capabilities.

    Creates a simple moving dot animation to test display
    update speed and smooth graphics transitions.

    Args:
        None

    Returns:
        bool: True if animation works smoothly

    Raises:
        Exception: If animation fails
    """
    print("Testing animation...")

    try:
        # Moving dot animation
        for x in range(0, DISPLAY_WIDTH - 1, 2):
            display.fill(0)
            display.text("Animation", 30, 10, 1)
            display.pixel(x, 30, 1)
            display.show()
            time.sleep(0.05)

        # Simple progress bar
        for width in range(0, 101, 5):
            display.fill(0)
            display.text("Progress", 30, 20, 1)

            # Progress bar outline
            display.rect(10, 35, 100, 10, 1)

            # Progress fill
            if width > 0:
                display.fill_rect(11, 36, width - 2, 8, 1)

            display.show()
            time.sleep(0.1)

        print("✓ Animation test passed")
        return True

    except Exception as e:
        print(f"✗ Animation test failed: {e}")
        return False


# =============================================================================
# MAIN TEST EXECUTION
# =============================================================================


def run_tests():
    """
    Execute all OLED display tests.

    Runs the complete test suite in logical order and reports
    results for each test category.

    Args:
        None

    Returns:
        None

    Raises:
        Exception: Individual test failures are handled and reported
    """
    print("=" * 50)
    print("ADAFRUIT 938 OLED DISPLAY TEST SUITE")
    print("=" * 50)

    if not setup_hardware():
        print("Hardware setup failed - cannot continue with tests")
        return

    # List of test functions
    tests = [
        test_display_clear,
        test_text_output,
        test_pixel_graphics,
        test_line_graphics,
        test_shape_graphics,
        test_power_functions,
        test_animation,
    ]

    passed = 0
    total = len(tests)

    print(f"\nRunning {total} tests...\n")

    for test in tests:
        try:
            if test():
                passed += 1
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"✗ {test.__name__} failed with exception: {e}")

    # Final results
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("✓ All tests passed - OLED display is fully functional")
    elif passed >= total * 0.8:
        print("⚠ Most tests passed - Display functional with minor issues")
    else:
        print("✗ Multiple tests failed - Check hardware and connections")

    # Clear display
    display.fill(0)
    display.text("Tests Complete", 10, 25, 1)
    display.show()


def main():
    """
    Main execution function.

    Entry point for the test suite with basic error handling
    for development and debugging use.

    Args:
        None

    Returns:
        None

    Raises:
        KeyboardInterrupt: Handles user interruption gracefully
    """
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        # Cleanup
        if display:
            try:
                display.fill(0)
                display.show()
            except:
                pass


# Execute main function if this file is run directly
if __name__ == "__main__":
    main()
