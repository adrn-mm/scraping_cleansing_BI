import subprocess

hdfs_directory_path = '/user/admin/csv/scraped_data_2024-06-10_09-15-43/nanggroe_aceh_darussalam/summary_16.csv'

# Building the query to create the external table
hive_query = """
CREATE EXTERNAL TABLE IF NOT EXISTS test_scraping_table (
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
LOCATION '{}';
""".format(hdfs_directory_path)

# Replace 'your_username' and 'your_password' with the actual credentials.
# username = 'admin'
# password = 'P4ssw0rd1!'

# Using the format() method for string formatting, which is compatible with Python 2.7 and all Python 3 versions.
# beeline_url = "jdbc:hive2://10.10.62.215:10000/default;user={username};password={password}".format(username=username, password=password)

# Using Beeline to connect to Hive and execute the query
beeline_cmd = [
'beeline', '-u', 'jdbc:hive2://bootstrap.lps.go.id:10000/raw;principal=hive/_HOST@LPS.GO.ID;ssl=true;sslTrustStore=/var/lib/cloudera-scm-agent/agent-cert/cm-auto-global_truststore.jks;trustStorePassword=tAhytZ0OxQX0XlrLUyoyOwT2jjik3B3PAUDrUSO8TvL',
'--silent=true',
'-e', hive_query
]

# Running the Beeline command
subprocess.call(beeline_cmd)
print("External table berhasil dibuat di Hive.")