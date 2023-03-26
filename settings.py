import json
import os


class Settings:
    def __init__(self, filename):
        self.filename = filename
        self.codec = "libx264"
        self.input_dir = ""
        self.output_dir = ""
        self.num_worker_threads = 4

    def save(self):
        with open(self.filename, "w") as f:
            settings = {
                "codec": self.codec,
                "input_dir": self.input_dir,
                "output_dir": self.output_dir,
                "num_worker_threads": self.num_worker_threads
            }
            json.dump(settings, f)

    def load(self):
        try:
            with open(self.filename, "r") as f:
                settings = json.load(f)
                self.codec = settings.get("codec", self.codec)
                self.input_dir = settings.get("input_dir", self.input_dir)
                self.output_dir = settings.get("output_dir", self.output_dir)
                self.num_worker_threads = settings.get(
                    "num_worker_threads", self.num_worker_threads)
        except FileNotFoundError:
            pass

    def exists(self):
        return os.path.exists(self.filename)
