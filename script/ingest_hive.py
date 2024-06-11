import os
from datetime import datetime
import re
import subprocess
import warnings
import time
import itertools
import sys
import threading

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

# Create the 'scraping' database if it doesn't exist
create_database_query = "CREATE DATABASE IF NOT EXISTS scraping;"
beeline_cmd = [
    'beeline', '-u','jdbc:hive2://bootstrap.lps.go.id:10000/scraping;principal=hive/_HOST@LPS.GO.ID;ssl=true;sslTrustStore=/var/lib/cloudera-scm-agent/agent-cert/cm-auto-global_truststore.jks;trustStorePassword=tAhytZ0OxQX0XlrLUyoyOwT2jjik3B3PAUDrUSO8TvL',
    '--silent=true',
    '-e', create_database_query
]
subprocess.call(beeline_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

parent_dir = os.path.dirname(os.getcwd())
scraped_data_dir = os.path.join(parent_dir, 'data')
dirs = [d for d in os.listdir(scraped_data_dir) if os.path.isdir(os.path.join(scraped_data_dir, d))]
dirs.sort(key=lambda d: datetime.strptime(re.search(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', d).group(), '%Y-%m-%d_%H-%M-%S'))
latest_dir = dirs[-1]
# Get all subdirectories in scraped_data_dir
province_dirs = [d for d in os.listdir(os.path.join(parent_dir, 'data', latest_dir)) if os.path.isdir(os.path.join(parent_dir, 'data', latest_dir, d))]
# For each subdirectory, create a corresponding subdirectory in transformed_data_dir
for province in province_dirs:
    filename = 'ii04'
    filenumber = '04'
    hdfs_path = f'/user/admin/csv/{latest_dir}/{province}/{filename}/'
    hive_query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {'scraping'}.{province}_{filename} (
            Propinsi STRING,
            Dati_II STRING,
            Tahun STRING,
            Bulan STRING,
            Tipe STRING,
            Nominal STRING,
            Jumlah STRING
        )
        ROW FORMAT DELIMITED
        FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
        LOCATION '{hdfs_path}';
        """
    # Using Beeline to connect to Hive and execute the query
    beeline_cmd = [
        'beeline', '-u','jdbc:hive2://bootstrap.lps.go.id:10000/scraping;principal=hive/_HOST@LPS.GO.ID;ssl=true;sslTrustStore=/var/lib/cloudera-scm-agent/agent-cert/cm-auto-global_truststore.jks;trustStorePassword=tAhytZ0OxQX0XlrLUyoyOwT2jjik3B3PAUDrUSO8TvL',
        '--silent=true',
        '-e', hive_query
        ]
    
    # Running the Beeline command
    subprocess.call(beeline_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
# For each subdirectory, create a corresponding subdirectory in transformed_data_dir
for province in province_dirs:
    filename = 'ii16'
    filenumber = '16'
    hdfs_path = f'/user/admin/csv/{latest_dir}/{province}/{filename}/'
    # Change the permission of the directory
    subprocess.run(['hadoop', 'fs', '-chmod', '-R', '755', hdfs_path])
    hive_query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {'scraping'}.{province}_{filename} (
            Propinsi STRING,
            Dati_II STRING,
            Tahun STRING,
            Bulan STRING,
            Tipe STRING,
            Nominal STRING,
            Jumlah STRING
        )
        ROW FORMAT DELIMITED
        FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
        LOCATION '{hdfs_path}';
        """
    # Using Beeline to connect to Hive and execute the query
    beeline_cmd = [
        'beeline', '-u','jdbc:hive2://bootstrap.lps.go.id:10000/scraping;principal=hive/_HOST@LPS.GO.ID;ssl=true;sslTrustStore=/var/lib/cloudera-scm-agent/agent-cert/cm-auto-global_truststore.jks;trustStorePassword=tAhytZ0OxQX0XlrLUyoyOwT2jjik3B3PAUDrUSO8TvL',
        '--silent=true',
        '-e', hive_query
        ]

    # Running the Beeline command
    subprocess.call(beeline_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

stop_event.set()
spinner_thread.join()
print("External table berhasil dibuat di Hive.")