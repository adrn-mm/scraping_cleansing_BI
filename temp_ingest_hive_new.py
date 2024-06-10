import os
import subprocess
import glob
from datetime import datetime
import re

parent_dir = '/root/python_scripts/crawling_btn'
scraped_data_dir = os.path.join(parent_dir, 'data')

dirs = [d for d in os.listdir(scraped_data_dir) if os.path.isdir(os.path.join(scraped_data_dir, d))]
dirs.sort(key=lambda d: datetime.strptime(re.search(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', d).group(), '%Y-%m-%d_%H-%M-%S'))
latest_dir = dirs[-1]

database_name = 'scraping'

# Function to escape spaces in directory names
def escape_spaces(directory_name):
    return directory_name.replace(' ', '\\ ')

# Iterate through each subdirectory
for subdir in os.listdir(os.path.join(scraped_data_dir, latest_dir)):
    # Get all CSV files in this subdirectory
    csv_files = glob.glob(os.path.join(scraped_data_dir, latest_dir, subdir, '*.csv'))

    # Iterate through each CSV file
    for csv_file in csv_files:
        # Get the province name and file number from the file name
        province_name, file_number = os.path.basename(csv_file).replace('.', '_').split('_')[0:2]

        # Escape spaces in subdir
        escaped_subdir = escape_spaces(subdir)
        hdfs_directory_path = f'/user/admin/csv/{latest_dir}/{escaped_subdir}/'

        # Building the query to create the external table
        hive_query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {database_name}.{province_name}_{file_number} (
            Propinsi STRING,
            Dati_II STRING,
            Tahun INT,
            Bulan STRING,
            Tipe STRING,
            Nominal DOUBLE,
            Jumlah INT
        )
        ROW FORMAT DELIMITED
        FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
        LOCATION 'file://{hdfs_directory_path}';
        """

        # Using Beeline to connect to Hive and execute the query
        beeline_cmd = [
            'beeline', '-u', 'jdbc:hive2://bootstrap.lps.go.id:10000/raw;principal=hive/_HOST@LPS.GO.ID;ssl=true;sslTrustStore=/var/lib/cloudera-scm-agent/agent-cert/cm-auto-global_truststore.jks;trustStorePassword=tAhytZ0OxQX0XlrLUyoyOwT2jjik3B3PAUDrUSO8TvL',
            '--silent=true',
            '-e', hive_query
        ]

        # Running the Beeline command
        subprocess.call(beeline_cmd)
