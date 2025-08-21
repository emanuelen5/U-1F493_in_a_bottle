import utime
from frame_updater import FrameUpdater
from hd44780 import char_envelope_left, char_envelope_right

# Must be at least the width of the display
ship = "." * 16 + char_envelope_left + char_envelope_right


def sleep_gen(ms: float):
    t0 = utime.ticks_ms()
    while utime.ticks_diff(utime.ticks_ms(), t0) < ms:
        yield


def send_envelope_animator(frame: FrameUpdater, time=1000):
    t0 = utime.ticks_ms()
    frame.hide_cursor()
    frame.update_display_optimized("")

    max_pos = len(ship) - 1
    while True:
        diff = utime.ticks_diff(utime.ticks_ms(), t0)
        if diff > time:
            break

        progress = diff / time
        pos = int(round(progress * max_pos))

        visible_part = ship[-pos - 1:]
        visible_part = visible_part[:16]  # Ensure it fits the display width

        text = "Skickar         " + visible_part
        frame.update_display_optimized(text[:32])
        yield from sleep_gen(int(10))

    frame.update_display_optimized("Klart!")
    yield from sleep_gen(1000)
    frame.show_cursor()
    frame.update_display_optimized("")


if __name__ == "__main__":
    from frame_updater import FrameUpdater
    from lcd import setup_lcd
    from hd44780 import get_japanese_keycode_map, add_missing_characters
    lcd = setup_lcd()

    keycode_map = get_japanese_keycode_map()
    add_missing_characters(lcd, keycode_map)
    frame = FrameUpdater(lcd, keycode_map)
    animator = send_envelope_animator(frame)

    for _ in animator:
        pass

