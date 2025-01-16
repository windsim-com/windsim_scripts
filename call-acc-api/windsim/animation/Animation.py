import sys
import threading
import time


class Animation:
    def __init__(self):
        """Initialize the spinner state and thread variables."""
        self.spinner_running = False
        self.spinner_thread = None

    def start_spinner(self, message: str):
        """Start a spinner animation in the console with a given message."""

        def spinner():
            spinner_chars = ['|', '/', '-', '\\']
            idx = 0
            while self.spinner_running:
                sys.stdout.write(f"\r{message} {spinner_chars[idx % len(spinner_chars)]}")
                sys.stdout.flush()
                idx += 1
                time.sleep(0.1)
            sys.stdout.write("\r")
            sys.stdout.flush()

        if self.spinner_running:
            return  # Prevent starting a second spinner
        self.spinner_running = True
        self.spinner_thread = threading.Thread(target=spinner)
        self.spinner_thread.start()

    def stop_spinner(self):
        """Stop the spinner animation."""
        if not self.spinner_running:
            return
        self.spinner_running = False
        self.spinner_thread.join()
        self.spinner_thread = None
        sys.stdout.write("\rOperation complete! \n")
        sys.stdout.flush()
