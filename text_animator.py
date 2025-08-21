import utime
import math
from frame_updater import FrameUpdater
from hd44780 import char_envelope_left, char_envelope_right

# Must be at least the width of the display
ship = "." * 16 + char_envelope_left + char_envelope_right


def sleep_gen(ms: float):
    t0 = utime.ticks_ms()
    while utime.ticks_diff(utime.ticks_ms(), t0) < ms:
        yield


def ease_out(progress):
    return 1 - math.cos(progress * math.pi / 2)


def send_envelope_animator(frame: FrameUpdater, time=1500):
    t0 = utime.ticks_ms()
    frame.hide_cursor()
    frame.set_text("")

    max_pos = len(ship) - 1
    while True:
        diff = utime.ticks_diff(utime.ticks_ms(), t0)
        if diff > time:
            break

        linear_progress = diff / time
        eased_progress = ease_out(linear_progress)
        pos = int(round(eased_progress * max_pos))

        visible_part = ship[-pos - 1:]
        visible_part = visible_part[:16]  # Ensure it fits the display width

        text = "Skickar         " + visible_part
        frame.set_text(text[:32])
        yield from sleep_gen(int(10))

    frame.set_text("Klart!")
    yield from sleep_gen(1000)
    frame.show_cursor()
    frame.set_text("")


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

