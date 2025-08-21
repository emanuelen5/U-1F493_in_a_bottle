import utime
from frame_updater import FrameUpdater
from hd44780 import char_envelope_left, char_envelope_right

# Must be at least the width of the display
ship = "                .................. " + char_envelope_left + char_envelope_right


def sleep_gen(ms: float):
    t0 = utime.ticks_ms()
    while utime.ticks_diff(utime.ticks_ms(), t0) < ms:
        yield


def send_envelope_animator(frame: FrameUpdater, initial_speed_ms=300, final_speed_ms=50):
    frame.lcd.hide_cursor()
    frame.update_display_optimized("")

    yield from sleep_gen(100)

    total_steps = len(ship)
    for pos in range(total_steps):
        progress = min(max(0, pos / 10), 1)
        current_speed = initial_speed_ms - progress * (initial_speed_ms - final_speed_ms)

        visible_part = ship[-pos - 1:]
        visible_part = visible_part[:16]  # Ensure it fits the display width

        frame.update_display_optimized(visible_part)
        yield from sleep_gen(int(current_speed))

    yield from sleep_gen(300)
    frame.update_display_optimized("    Sparat!")
    yield from sleep_gen(1000)
    frame.update_display_optimized("")
    frame.lcd.blink_cursor_on()


if __name__ == "__main__":
    from frame_updater import FrameUpdater
    from lcd import setup_lcd
    from hd44780 import get_japanese_keycode_map, add_missing_characters
    lcd = setup_lcd()
    lcd.blink_cursor_on()

    keycode_map = get_japanese_keycode_map()
    add_missing_characters(lcd, keycode_map)
    frame = FrameUpdater(lcd, keycode_map)
    animator = send_envelope_animator(frame)

    for _ in animator:
        pass

