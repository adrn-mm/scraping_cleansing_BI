import os
import glob
import warnings
from datetime import datetime
import re
import pandas as pd
import subprocess
import threading
import sys
import time
import warnings
import itertools

# Ignore all warnings
warnings.filterwarnings("ignore")

# Function to display a spinner with elapsed time
def spinner(msg, stop_event):
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    start_time = time.time()
    while not stop_event.is_set():
        elapsed_time = time.time() - start_time
        sys.stdout.write('\r' + msg + ' ' + next(spinner) + f' Elapsed time: {elapsed_time:.2f}s')
        sys.stdout.flush()
        time.sleep(0.1)
    elapsed_time = time.time() - start_time
    sys.stdout.write('\r' + msg + ' done! ' + f'Total time: {elapsed_time:.2f}s\n')

# Start spinner
stop_event = threading.Event()
spinner_thread = threading.Thread(target=spinner, args=("Please wait, start ingest data to HDFS...", stop_event))
spinner_thread.start()

# get the folder with the latest scraped data
parent_dir = os.path.dirname(os.getcwd())
scraped_data_dir = os.path.join(parent_dir, 'data')
dirs = [d for d in os.listdir(scraped_data_dir) if os.path.isdir(os.path.join(scraped_data_dir, d))]
dirs.sort(key=lambda d: datetime.strptime(re.search(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', d).group(), '%Y-%m-%d_%H-%M-%S'))
latest_dir = dirs[-1]
# Get all subdirectories in scraped_data_dir
province_dirs = [d for d in os.listdir(os.path.join(parent_dir, 'data', latest_dir)) if os.path.isdir(os.path.join(parent_dir, 'data', latest_dir, d))]

# Ignore all warnings
warnings.filterwarnings("ignore")

# Lokasi target di HDFS (pastikan ini adalah direktori, bukan file)
hdfs_directory_path = '/user/admin/csv/'

subprocess.call(['hadoop', 'fs', '-mkdir', '-p', hdfs_directory_path])
subprocess.call(['hadoop', 'fs', '-put', '-f', os.path.join(parent_dir, 'data', latest_dir), hdfs_directory_path])

stop_event.set()
spinner_thread.join()
print("Data has been ingested to HDFS.")    