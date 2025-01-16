# Spinner animation function
import itertools
import threading
import time
import sys
class Animation:
    def __init__(self):
        self.spinner_thread = None

    @staticmethod
    def spinner_animation(message="Loading..."):
        for char in itertools.cycle('|/-\\'):
            status = f"\r{message} {char}"
            sys.stdout.write(status)
            sys.stdout.flush()
            time.sleep(0.1)

    # Function to start the spinner in a separate thread
    def start_spinner(self, message):
        spinner_thread = threading.Thread(target=self.spinner_animation, args=(message,))
        spinner_thread.start()
        return spinner_thread

    # Function to stop the spinner
    @staticmethod
    def stop_spinner(spinner_thread):
        if spinner_thread:
            spinner_thread.do_run = False
            spinner_thread.join()