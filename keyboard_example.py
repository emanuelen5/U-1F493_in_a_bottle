"""
Example usage of the PS/2 keyboard with key tracking
This demonstrates how to use the keyboard module to track typed text
"""

import time

from ps2_kb import clear_typed_text, get_debug_info, get_typed_text, is_shift_held


def main():
    print("PS/2 Keyboard Text Tracker")
    print("Type on your PS/2 keyboard. Press Ctrl+C to exit.")
    print("=" * 50)

    last_text = ""

    try:
        while True:
            # Get the current typed text
            current_text = get_typed_text()

            # Only update display if text has changed
            if current_text != last_text:
                print(f"\rTyped: '{current_text}'", end="")
                if is_shift_held():
                    print(" [SHIFT]", end="")
                print("    ", end="")  # Clear any leftover characters
                last_text = current_text

            # Show debug info every 5 seconds (optional)
            if int(time.time()) % 5 == 0:
                debug = get_debug_info()
                if debug['pending_scan_codes'] > 0:
                    print(f"\n[DEBUG] Pending scan codes: {debug['pending_scan_codes']}")

            time.sleep(0.1)  # Small delay to prevent excessive CPU usage

    except KeyboardInterrupt:
        print("\n\nFinal typed text:")
        print(f"'{get_typed_text()}'")
        print("\nExiting...")

def demo_with_display():
    """
    Example function for use with an LCD display
    This shows how you might integrate with your LCD code
    """
    # This would typically import your LCD modules
    # from lcd import LCD
    # lcd = LCD()

    while True:
        text = get_typed_text()

        # Update your display here
        # lcd.clear()
        # lcd.write(text[:16])  # Assuming 16 character display

        print(f"Display would show: '{text[:16]}'")  # Simulation
        time.sleep(0.2)

if __name__ == "__main__":
    main()
