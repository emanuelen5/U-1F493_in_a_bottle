import time


class Logbook:
    def __init__(self, filename="logbook.txt"):
        self.filename = filename

    def write_entry(self, full_text: str):
        localtime = time.localtime()
        dt = "{:>04d}-{:>02d}-{:>02d} {:>02d}:{:>02d}:{:>02d}".format(*localtime)

        with open(self.filename, "a") as f:
            f.write(f"--- {dt}\n" + full_text + "\n")
