from text_animator import send_envelope_animator
from frame_updater import FrameUpdater
from keyboard import KeyboardTracker, Key, key_f10
from lcd import setup_lcd
from led_animator import LedAnimator
from logbook import Logbook
from ps2_pio import PS2PIODriver
from hd44780 import get_japanese_keycode_map, add_missing_characters
import gc
from ws2812b_pio import WS2812B_Driver

# Initialize PS/2 PIO driver
ps2 = PS2PIODriver(data_pin=2, clock_pin=3)
kbd = KeyboardTracker(verbose=True)

lcd = setup_lcd()

keycode_map = get_japanese_keycode_map()
add_missing_characters(lcd, keycode_map)

frame = FrameUpdater(lcd, keycode_map)
led_strip = WS2812B_Driver(pin_num=15, led_count=50, state_machine_id=1)
led_animator = LedAnimator(led_strip)

print("Main loop started with PIO driver")

full_text = ""
log = Logbook("logbook.txt")

# Display buffer to track what's currently shown (2 lines × 16 chars)
display_buffer = [[ord(" ") for _ in range(16)] for _ in range(2)]

while True:
    gc.collect()

    while scan_code := ps2.get_scan_code():
        kbd.process_code(scan_code)

    if ps2.get_parity_error_count() > 0:
        lcd.clear()
        # Reset display buffer since we cleared the screen
        display_buffer = [[ord(" ") for _ in range(16)] for _ in range(2)]
        lcd.putstr("Parity error. Resetting PIO...")
        ps2.reset_sm()
        continue

    keys: list[Key] = []
    while key := kbd.get_keypress():
        keys.append(key)

    for key in keys:
        if key.char == "\n":
            log.write_entry(full_text)
            led_animator.add_wandering_pulse(red=255, green=0, blue=20, width=1.5, lifetime_ms=3000)
            for _ in send_envelope_animator(frame, time=1500):
                gc.collect()
                led_animator.service()
            ps2.reset_sm()  # Clear any key presses that were queued during animation
            full_text = ""
        elif key.char == "\b":
            full_text = full_text[:-1]
        elif key.char == "\b\b":
            idx = full_text.rfind(" ")
            if idx == -1:
                idx = 0
            full_text = full_text[:idx]
        elif key.char == key_f10:
            led_animator.add_wandering_pulse(red=255, green=0, blue=20, width=1.5, lifetime_ms=3000)
        elif key.char in keycode_map:
            full_text += key.char

    frame.update_display_optimized(full_text)
    led_animator.service()
