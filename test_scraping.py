# Import libraries
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
from selenium.common.exceptions import TimeoutException
import time

# Load environment variables from .env file
load_dotenv()

# Define driver
options = webdriver.FirefoxOptions()
driver = webdriver.Firefox(options=options)

# Define the url
url= "https://www.bi.go.id/id/statistik/ekonomi-keuangan/sekda/StatistikRegionalDetail.aspx?idprov=14"

# Print status
print("Please wait, start scraping...")

# Solution for timeout
driver.set_page_load_timeout(50)
try:
    driver.get(url)
except TimeoutException:
    driver.quit()

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
    select_provinsi.select_by_value(option_value)
    # select_provinsi.select_by_visible_text(option.text)
    
    # Select category
    select_category = get_select('DropDownListCategorySekda')
    select_category.select_by_visible_text("Kegiatan Perbankan")
    
    # Get hrefs of the categories
    category_details = [get_cell_href(number) for number in scrape_category_numbers]
    
    # Add the hrefs to the list
    all_hrefs.extend(category_details)

# Print the hrefs
print(all_hrefs)

# Quit the driver
driver.quit()