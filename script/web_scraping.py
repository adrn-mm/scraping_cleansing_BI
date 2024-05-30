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
from selenium.webdriver.firefox.service import Service
import time

# Define the 1st driver
service = Service(executable_path=os.getcwd(),
                  service_log_path=False)
options = Options()
options.add_argument('--headless')
driver_1 = webdriver.Firefox(options=options, service=service)

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
    all_province_names.append(province_name)
    print(f"Scraping data for province: {province_name}")
    
    # Select the province
    select_provinsi.select_by_value(option.get_attribute('value'))
     
    # Select category
    select_category = get_select('DropDownListCategorySekda')
    select_category.select_by_visible_text("Kegiatan Perbankan")
    
    # Get hrefs of the categories
    category_details = [get_cell_href(number) for number in [4, 16]]
    
    all_links.append(category_details)

# close the browser 1
driver_1.quit()
print("Scraping completed!")
# print(all_links)

# download all links to the root folder
print("Downloading files...")    
for links, province_name in zip(all_links, all_province_names):
    # set download dir
    parent_dir = os.path.dirname(os.getcwd())
    download_dir = os.path.join(parent_dir, 'data', root_folder, province_name)
    
    # Create the directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    
    for link in links:
        # set the path
        local_filename =  os.path.join(download_dir, link.split('/')[-1])
    
        # set the 2nd driver
        options.set_preference("browser.download.folderList", 2) 
        options.set_preference("browser.download.dir", download_dir)
        options.add_argument('--headless')
        driver_2 = webdriver.Firefox(options=options)
        
        driver_2.set_page_load_timeout(10)
        try:
            print(f"Downloading {province_name} file...")
            driver_2.get(link)
        except TimeoutException:
            # driver_2.execute_script("window.stop();")
            driver_2.quit()
        
        # Unzip the file
        with ZipFile(local_filename, 'r') as zip_ref:
            # Extract the file into the province directory
            zip_ref.extractall(path=download_dir)
        # Remove the zip file
        os.remove(local_filename)

# download complete
print("Download completed!")

# Record the end time
end_time = time.time()

# Calculate the duration
duration = (end_time - start_time)/60

# Count the number of files in the root folder
folder_path = os.path.join(parent_dir, 'data', root_folder)
num_folders = len([f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))])

# Convert the existing timestamp to the desired format
timestamp = datetime.strptime(timestamp, '%Y-%m-%d_%H-%M-%S')
formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

# Write the log
with open('log.txt', 'a') as f:
    f.write(f"Scraping on {formatted_timestamp} with duration {duration} minutes and scraped {num_folders} folders.\n")    