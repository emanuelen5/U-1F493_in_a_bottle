import utime
from machine import Pin

from keyboard import keyboard

# Use GP2 for Data, GP3 for Clock
DATA_PIN = Pin(2, Pin.IN, Pin.PULL_UP)
CLOCK_PIN = Pin(3, Pin.IN, Pin.PULL_UP)

scan_bits = []
scan_codes: list[int] = []
last_key_time = utime.ticks_ms()

# Debug counters for monitoring frame quality
frame_stats = {
    'total_frames': 0,
    'start_bit_errors': 0,
    'stop_bit_errors': 0,
    'parity_errors': 0,
    'valid_frames': 0
}


def ps2_irq_handler(pin):
    global scan_bits, scan_codes, frame_stats, last_key_time
    value = DATA_PIN.value()
    scan_bits.append(value)
    last_key_time = utime.ticks_ms()

    scan_code = 0
    for i in range(len(scan_bits)):
        scan_code |= (scan_bits[i] << i)
    print(f"Data bit {len(scan_bits)} received: {value}, 0b{scan_code:011b}")  # Debug output
    if len(scan_bits) == 11:
        # Process the complete scan code
        bits = scan_bits.copy()
        scan_bits = []

        # Validate PS/2 frame format
        start_bit = bits[0]
        data_bits = bits[1:9]
        parity_bit = bits[9]
        stop_bit = bits[10]

        # Check start bit (should be 0)
        if start_bit != 0:
            frame_stats['start_bit_errors'] += 1
            return  # Invalid frame, ignore

        # Check stop bit (should be 1)
        if stop_bit != 1:
            frame_stats['stop_bit_errors'] += 1
            return  # Invalid frame, ignore

        # Calculate and check parity (odd parity)
        data_parity = sum(data_bits) % 2
        expected_parity = 1 - data_parity  # Odd parity
        if parity_bit != expected_parity:
            frame_stats['parity_errors'] += 1
            return  # Parity error, ignore

        # Extract data value (LSB first)
        value = 0
        for i, bit in enumerate(data_bits):
            value |= (bit << i)

        # Append the scan code to the list
        scan_codes.append(value)

        # Process the scan code for key tracking
        keyboard.process_scan_code(value)

        frame_stats['valid_frames'] += 1


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
    """Get debug information including recent scan codes and frame statistics"""
    return {
        'recent_scan_codes': keyboard.get_last_scan_codes(),
        'shift_pressed': keyboard.is_shift_pressed(),
        'typed_text': keyboard.get_keys_string(),
        'pending_scan_codes': len(scan_codes),
        'frame_stats': get_frame_stats()
    }

def get_frame_stats():
    """Get statistics about frame validation"""
    return frame_stats.copy()

def reset_frame_stats():
    """Reset frame statistics"""
    global frame_stats
    for key in frame_stats:
        frame_stats[key] = 0

def check_bus_timeout():
    """Check if PS/2 bus has been inactive for 10ms and clear scan_bits if so"""
    global scan_bits, last_key_time
    if scan_bits and utime.ticks_diff(utime.ticks_ms(), last_key_time) > 10:
        print(f"PS/2 bus timeout - clearing {len(scan_bits)} pending bits")
        scan_bits.clear()
