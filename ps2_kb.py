from machine import Pin
from keyboard import keyboard

# Use GP2 for Data, GP3 for Clock
DATA_PIN = Pin(2, Pin.IN, Pin.PULL_UP)
CLOCK_PIN = Pin(3, Pin.IN, Pin.PULL_UP)

scan_bits = []
scan_ready = False
scan_codes: list[int] = []


def ps2_irq_handler(pin):
    global scan_bits, scan_ready, scan_codes
    scan_bits.append(DATA_PIN.value())
    if len(scan_bits) == 11:
        # Process the complete scan code
        bits = scan_bits.copy()
        scan_bits = []
        scan_ready = False

        # Extract data bits (bits 1-8, excluding start, parity, and stop bits)
        data_bits = bits[1:9]
        value = 0
        for i, bit in enumerate(data_bits):
            value |= bit << i

        # Append the scan code to the list
        scan_codes.append(value)
        
        # Process the scan code for key tracking
        keyboard.process_scan_code(value)
        
        scan_ready = True


CLOCK_PIN.irq(trigger=Pin.IRQ_FALLING, handler=ps2_irq_handler)

def get_scan_code():
    """Get the next available scan code from the buffer, or None if empty"""
    global scan_codes
    if scan_codes:
        return scan_codes.pop(0)
    return None

def has_scan_code():
    """Check if there are scan codes available"""
    return len(scan_codes) > 0

def get_typed_text():
    """Get the current typed text string"""
    return keyboard.get_keys_string()

def clear_typed_text():
    """Clear the typed text string"""
    keyboard.clear_keys()

def is_shift_held():
    """Check if shift is currently pressed"""
    return keyboard.is_shift_pressed()

def get_debug_info():
    """Get debug information including recent scan codes"""
    return {
        'recent_scan_codes': keyboard.get_last_scan_codes(),
        'shift_pressed': keyboard.is_shift_pressed(),
        'typed_text': keyboard.get_keys_string(),
        'pending_scan_codes': len(scan_codes)
    }
