class CustomError(Exception):
    """Custom exception class for LoL Replay Recorder."""

    def __init__(self, *args):
        super().__init__(*args)