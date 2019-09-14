import threading
from ps import DataCollection, auto_update
from ftp import download_one

thread = threading.Thread(target=auto_update)
thread.start()

for i in range(4):
    thread = threading.Thread(target=download_one)
    thread.start()
