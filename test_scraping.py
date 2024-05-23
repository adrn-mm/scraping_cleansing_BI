# Import libraries
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
from selenium.common.exceptions import TimeoutException
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Load environment variables from .env file
load_dotenv()

# Define driver with headless option
options = webdriver.FirefoxOptions()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

# Define the url
url = "https://www.bi.go.id/id/statistik/ekonomi-keuangan/sekda/StatistikRegionalDetail.aspx?idprov=14"

# Print status
print("Please wait, start scraping...")

# Solution for timeout
driver.set_page_load_timeout(50)
try:
    driver.get(url)
except TimeoutException:
    driver.quit()
    raise  # Re-raise the exception to stop the script

# Define the numbers of the categories to scrape
scrape_category_numbers = [4, 16]

# Function to get href of a cell
def get_cell_href(number):
    cell_xpath = f'//*[@id="ctl00_ctl54_g_077c3f62_96a4_43aa_b013_8e274cf2ce9d_ctl00_divIsi"]/table/tbody/tr[{number}]/td[2]/a'
    cell_element = driver.find_element(By.XPATH, cell_xpath)
    return cell_element.get_attribute('href')

# Function to get select element
def get_select(id):
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, id))
    )
    select = Select(dropdown)
    return select

# Select province
select_provinsi = get_select('DropDownListProvinsiSekda')

# Get all options from the dropdown
options = select_provinsi.options
total_options = len(select_provinsi.options)

# List to store all hrefs
all_hrefs = []

# Iterate over each option
for i in range(total_options):
    # Select province
    select_provinsi = get_select('DropDownListProvinsiSekda')
    option = select_provinsi.options[i]
    option_value = option.get_attribute('value')
    province_name = option.get_attribute("text")
    print(f"Scraping data for province: {province_name}")
    select_provinsi.select_by_value(option_value)
    
    # Select category
    select_category = get_select('DropDownListCategorySekda')
    select_category.select_by_visible_text("Kegiatan Perbankan")
    
    # Get hrefs of the categories
    category_details = [get_cell_href(number) for number in scrape_category_numbers]
    
    # Add the hrefs to the list
    all_hrefs.extend(category_details)

# Print the hrefs
# print(all_hrefs)

# Create a new directory to store the downloaded files
os.makedirs('downloaded_files', exist_ok=True)

# Setup retry strategy for requests
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

# Iterate over all hrefs
for href in all_hrefs:
    # Get the file name from the href
    file_name = href.split('/')[-1]
    
    try:
        # Send a GET request to the href
        response = http.get(href, stream=True)
        
        # Check if the request is successful
        if response.status_code == 200:
            # Open the file in write and binary mode
            with open(f'downloaded_files/{file_name}', 'wb') as f:
                # Write the content of the response to the file
                f.write(response.content)
                
            # Print a success message
            print(f"Berhasil mendownload {file_name}")
        else:
            print(f"Failed to download {file_name}, status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# Quit the driver
driver.quit()