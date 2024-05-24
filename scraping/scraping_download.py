# Import libraries
from selenium import webdriver 
from selenium.webdriver.common.by import By
import os
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from datetime import datetime
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zipfile import ZipFile
from selenium.webdriver.firefox.options import Options
import time
import speedtest

# Define the 1st driver
options = Options()
options.add_argument('--headless')
driver_1 = webdriver.Firefox(options=options)

# Define the URL
url = "https://www.bi.go.id/id/statistik/ekonomi-keuangan/sekda/StatistikRegionalDetail.aspx?idprov=14"

# Calculate the average speed
s = speedtest.Speedtest()
download_speed = s.download() / 1e6  # Convert from bytes to megabits
upload_speed = s.upload() / 1e6  # Convert from bytes to megabits
average_speed = (download_speed + upload_speed) / 2

# Record the start time
start_time = time.time()

# the 1st driver get the url
driver_1.set_page_load_timeout(50)
try:
    driver_1.get(url)
    print("Please wait, start scraping...")
except TimeoutException:
    driver_1.execute_script("window.stop();")
    print("Timeout when loading the page")
    
# Create a new directory to store the downloaded files
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
root_folder = f'scraped_data_{timestamp}'
os.makedirs(os.path.join('scraped_data', root_folder), exist_ok=True)

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

# Function to download and unzip files 
def download_and_unzip(url, folder, province_name):
    # set download dit
    download_dir = os.path.join(os.getcwd(), folder)
    
    # set the path
    local_filename = os.path.join(folder, url.split('/')[-1])
    
    # set the 2nd driver
    options.set_preference("browser.download.folderList", 2) 
    options.set_preference("browser.download.dir", download_dir)
    options.add_argument('--headless')
    driver_2 = webdriver.Firefox(options=options)
        
    # the 2nd driver get the url
    """
    - the download is faster than using requests.get()
    - somehow only works only if add the try-except block/timeout
    """
    driver_2.set_page_load_timeout(60)
    try:
        driver_2.get(url)
    except TimeoutException:
        driver_2.execute_script("window.stop();")
    driver_2.quit()    

    # Unzip the file
    with ZipFile(local_filename, 'r') as zip_ref:
        zip_ref.extractall() 
    
    # rename the files
    old_file_names = ['ii04.xls', 'ii16.xls']
    for old_file_name in old_file_names:
        if os.path.isfile(old_file_name):
            os.rename(old_file_name,
                      os.path.join(folder, province_name+'_'+old_file_name)
            )
    
    # Remove the zip file
    os.remove(local_filename)

# Get all options from the dropdown
total_options = len(get_select('DropDownListProvinsiSekda').options)

# Iterate over each province
for i in range(total_options): 
    # Get the province name
    select_provinsi = get_select('DropDownListProvinsiSekda')
    option = select_provinsi.options[i]
    province_name = option.get_attribute("text")
    print(f"Scraping data for province: {province_name}")
    
    # Select the province
    select_provinsi.select_by_value(option.get_attribute('value'))
     
    # Select category
    select_category = get_select('DropDownListCategorySekda')
    select_category.select_by_visible_text("Kegiatan Perbankan")
    
    # Get hrefs of the categories
    category_details = [get_cell_href(number) for number in [4, 16]]
    
    # Download and unzip files
    for detail_url in category_details:
        download_and_unzip(detail_url,
                           os.path.join('scraped_data', root_folder),
                           province_name)

# Quit the 1st driver
driver_1.quit()

# Record the end time
end_time = time.time()

# Calculate the duration
duration = end_time - start_time

# Count the number of files in the root folder
num_files = len([f for f in os.listdir(root_folder) if os.path.isfile(os.path.join(root_folder, f))])

# Write the log
with open('log.txt', 'a') as f:
    f.write(f"Scraping on {timestamp} with duration {duration} seconds and scraped {num_files} files, and average internet speed was {average_speed} Mbps.\n")
    
print("Scraping completed!")