# Import libraries
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from datetime import datetime
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zipfile import ZipFile
from selenium.webdriver.chrome.options import Options as chromeOptions
from selenium.webdriver.firefox.service import Service
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import warnings
import itertools
import threading
import sys
import requests
from dotenv import load_dotenv
import os
import getpass
import subprocess

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

# Before starting the web scraping, start the Docker Compose services
subprocess.run(["docker-compose", "up", "-d"], check=True)
subprocess.run(["docker-compose", "restart"], check=True)
time.sleep(10)

# kinit process
# Get the password
password = os.getenv("ADMIN_PASSWORD")
# If the password is not set in the .env file, ask for it
if password is None:
    password = getpass.getpass("Enter the password: ")
# Run the kinit command
subprocess.run(["kinit", "admin"], input=password, encoding='utf-8')

# Define the 1st driver
driver_1 = webdriver.Remote("http://127.0.0.1:4444/wd/hub", DesiredCapabilities.CHROME)

# Define the URL
url = "https://www.bi.go.id/id/statistik/ekonomi-keuangan/sekda/StatistikRegionalDetail.aspx?idprov=14"

# Create a new directory to store the downloaded files
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
root_folder = f'scraped_data_{timestamp}'
parent_dir = os.path.dirname(os.getcwd())
os.makedirs(os.path.join(parent_dir, 'data', root_folder), exist_ok=True)

# Function to get select element
def get_select(id):
    dropdown = WebDriverWait(driver_1, 10).until(
        EC.element_to_be_clickable((By.ID, id))
    )
    select = Select(dropdown)
    return select

# Function to get href of a cell
def get_cell_href(number):
    cell_xpath = f'//*[@id="ctl00_ctl54_g_077c3f62_96a4_43aa_b013_8e274cf2ce9d_ctl00_divIsi"]/table/tbody/tr[{number}]/td[2]/a'
    cell_element = driver_1.find_element(By.XPATH, cell_xpath)
    return cell_element.get_attribute('href')

# function to download file
def download_file(url, download_dir):
    local_filename = os.path.join(download_dir, url.split('/')[-1])
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        return local_filename
    except Exception as e:
        return f"Failed to download {url}: {e}"

# the 1st driver get the url
stop_event = threading.Event()
spinner_thread = threading.Thread(target=spinner, args=("Please wait, start scraping...", stop_event))
spinner_thread.start()
driver_1.set_page_load_timeout(50)
try:
    driver_1.get(url)
except TimeoutException:
    driver_1.execute_script("window.stop();")
    print("Timeout when loading the page")

# Get all options from the dropdown
total_options = len(get_select('DropDownListProvinsiSekda').options)

# links for downloading and province names
all_links = []
all_province_names = []

# Iterate over each province
for i in range(total_options): 
    # Get the province name
    select_provinsi = get_select('DropDownListProvinsiSekda')
    option = select_provinsi.options[i]
    province_name = option.get_attribute("text")
    province_name = province_name.lower().replace(' ', '_')
    all_province_names.append(province_name)
    
    # Select the province
    select_provinsi.select_by_value(option.get_attribute('value'))
     
    # Select category
    select_category = get_select('DropDownListCategorySekda')
    select_category.select_by_visible_text("Kegiatan Perbankan")
    
    # Get hrefs of the categories
    category_details = [get_cell_href(number) for number in [4, 16]]
    
    all_links.append(category_details)

# close the browser 1
stop_event.set()
spinner_thread.join()
driver_1.quit()

# download all links to the root folder
stop_event = threading.Event()
spinner_thread = threading.Thread(target=spinner, args=("Please wait, start downloading...", stop_event))
spinner_thread.start()
for links, province_name in zip(all_links, all_province_names):
    # set download dir
    parent_dir = os.path.dirname(os.getcwd())
    download_dir = os.path.join(parent_dir, 'data')
    scraped_data_dir = os.path.join(parent_dir,
                                'data',
                                root_folder, province_name)
    
    # Create the directory if it doesn't exist
    os.makedirs(scraped_data_dir, exist_ok=True)
    
    for link in links:
        # set the path
        file_name_without_extension = os.path.splitext(link.split('/')[-1])[0]
        file_name_without_extension = file_name_without_extension.split('-')[-1]
        local_filename =  os.path.join(scraped_data_dir, link.split('/')[-1])
        zip_filename =  os.path.join(parent_dir, link.split('/')[-1])
        new_scraped_data_dir = os.path.join(scraped_data_dir, file_name_without_extension)

        # Download the file
        os.makedirs(new_scraped_data_dir, exist_ok=True)
        download_file(link, scraped_data_dir)
        
        # Unzip the file
        time.sleep(10)
        with ZipFile(local_filename, 'r') as zip_ref:
            # Extract the file into the province directory
            zip_ref.extractall(path=new_scraped_data_dir)
        # Remove the zip file
        os.remove(local_filename)

# download complete
stop_event.set()
spinner_thread.join()
    
# After the web scraping is done, stop the Docker Compose services
subprocess.run(["docker-compose", "down"], check=True)