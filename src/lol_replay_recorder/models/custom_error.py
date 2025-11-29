class CustomError(Exception):
    """Custom exception class for LoL Replay Recorder."""

    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        if self.args:
            return str(self.args[0])
        return ""