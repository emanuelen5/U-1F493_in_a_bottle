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

    def update_display_optimized(self, text):
        """Update only the parts of the display that have changed"""
        if text == self.last_text:
            return  # No changes, skip update

        # Convert text to character codes (last 31 chars, reversed order)
        charcodes = []
        for c in reversed(text):
            if len(charcodes) >= (31 if self.uses_cursor else 32):
                break
            charcode = self.keycode_map.get(c, None)
            if charcode is None:
                continue
            charcodes.insert(0, charcode)

        # Create new display state
        new_buffer = [[ord(" ") for _ in range(16)] for _ in range(2)]

        # Fill the new buffer with the text
        for i, charcode in enumerate(charcodes):
            row = i // 16
            col = i % 16
            if row < 2:
                new_buffer[row][col] = charcode

        # Update only changed positions
        cursor_row, cursor_col = -1, -1  # Track where we think the cursor is
        for row in range(2):
            for col in range(16):
                if new_buffer[row][col] != self.display_buffer[row][col]:
                    # Only move cursor if we're not already at the right position
                    if cursor_row != row or cursor_col != col:
                        self.lcd.move_to(col, row)
                        cursor_row, cursor_col = row, col

                    self.lcd.hal_write_data(new_buffer[row][col])
                    self.display_buffer[row][col] = new_buffer[row][col]
                    # Cursor automatically moves right after writing (but doesn't wrap)
                    cursor_col += 1

        if self.uses_cursor:
            # Position cursor at the end of text
            text_len = len(charcodes)
            if text_len > 32:
                self.lcd.move_to(15, 1)
            else:
                self.lcd.move_to(text_len % 16, text_len // 16)

        self.last_text = text
