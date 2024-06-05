import subprocess

hdfs_directory_path = '/user/admin/csv'

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
    'beeline',
    '--silent=true',  # Optional: Reduces unnecessary logging
    '-e', hive_query
]

# Running the Beeline command
subprocess.call(beeline_cmd)
print("External table berhasil dibuat di Hive.")