from lcd_api import LcdApi


class FrameUpdater:
    def __init__(self, lcd: LcdApi, keycode_map: dict[str, int]):
        self.lcd = lcd
        self.display_buffer = [[ord(" ") for _ in range(16)] for _ in range(2)]
        self.keycode_map = keycode_map
        self.last_text = " " * 32
        self.uses_cursor = True

        self.show_cursor()

    def hide_cursor(self):
        self.uses_cursor = False
        self.lcd.hide_cursor()

    def show_cursor(self):
        self.uses_cursor = True
        self.lcd.blink_cursor_on()

    def cursor_hidden(self):
        return CursorHider(self)

    def set_text(self, text):
        """Update only the parts of the display that have changed"""
        if text == self.last_text:
            return  # No changes, skip update

        used_cursor = self.uses_cursor
        self.uses_cursor = False

        charcodes = []
        for c in text:
            charcode = self.keycode_map.get(c, None)
            if charcode is None:
                continue
            charcodes.append(charcode)

        # Make sure the text is adjusted down to the second line
        text_len = len(charcodes)
        if text_len < 16:
            charcodes = [ord(" ")] * 16 + charcodes

        # Make sure we have at maximum 31 characters to display
        while (text_len := len(charcodes)) > (31 if used_cursor else 32):
            charcodes = charcodes[16:]

        # Create new display state
        new_buffer = [[ord(" ") for _ in range(16)] for _ in range(2)]

        # Fill the new buffer with the text
        while len(charcodes) < 32:
            charcodes.append(ord(" "))

        for col in range(16):
            new_buffer[0][col] = charcodes[col]
            new_buffer[1][col] = charcodes[col + 16]

        # Update only changed positions
        cursor_row, cursor_col = -1, -1  # Track where we think the cursor is
        for row in range(2):
            for col in range(16):
                if new_buffer[row][col] == self.display_buffer[row][col]:
                    continue

                # Only move cursor if we're not already at the right position
                if cursor_row != row or cursor_col != col:
                    self.lcd.move_to(col, row)
                    cursor_row, cursor_col = row, col

                self.lcd.hal_write_data(new_buffer[row][col])
                self.display_buffer[row][col] = new_buffer[row][col]
                # Cursor automatically moves right after writing (but doesn't wrap)
                cursor_col += 1

        if used_cursor:
            self.show_cursor()
            self.lcd.move_to(text_len % 16, 1)

        self.last_text = text


class CursorHider:
    def __init__(self, frame: FrameUpdater):
        self.frame = frame

    def __enter__(self):
        self.frame.hide_cursor()

    def __exit__(self, exc_type, exc_value, traceback):
        self.frame.show_cursor()


if __name__ == "__main__":
    import utime
    from lcd import setup_lcd
    from hd44780 import get_japanese_keycode_map, add_missing_characters
    lcd = setup_lcd()

    keycode_map = get_japanese_keycode_map()
    add_missing_characters(lcd, keycode_map)
    frame = FrameUpdater(lcd, keycode_map)

    frame.set_text("Kort text")
    utime.sleep_ms(1000)

    frame.set_text("Rad 1           " + "Rad 2")
    utime.sleep_ms(1000)

    text = ""
    template = "Line {lines:8d}..."
    for line in range(4):
        text += template.format(lines=line)
        frame.set_text(text)
        utime.sleep_ms(100)
