import threading
from time import sleep
import shutil
import os
lock = threading.Lock()
def clean_temp_files(interval=3600, temp_dir="file"):
    def cleaner():
        while True:
            sleep(interval)
            if os.path.exists(temp_dir):
                lock.acquire()
                try:
                    shutil.rmtree(temp_dir)
                    os.makedirs(temp_dir)
                finally:
                    lock.release()
    thread = threading.Thread(target=cleaner, daemon=True)
    thread.start()