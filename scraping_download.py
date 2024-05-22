# Import libraries
from selenium import webdriver 
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import subprocess
from datetime import datetime
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# define driver
options = webdriver.FirefoxOptions()
driver = webdriver.Firefox(options=options)

# define the url
url= "https://www.bi.go.id/id/statistik/ekonomi-keuangan/sekda/StatistikRegionalDetail.aspx?idprov=14"

# print status
print("Please wait, start scraping...")

# solution for timeout
driver.set_page_load_timeout(50)
try:
    driver.get(url)
except TimeoutException:
    driver.execute_script("window.stop();")

# Function to get select element
def get_select(id):
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, id))
    )
    select = Select(dropdown)
    return select

# Select province
select_provinsi = get_select('DropDownListProvinsiSekda')
select_provinsi.select_by_visible_text("Bengkulu")

# Select category
select_category = get_select('DropDownListCategorySekda')
select_category.select_by_visible_text("Kegiatan Perbankan")

# Define the numbers of the categories to scrape
scrape_category_numbers = [4, 16]

# Function to get href of a cell
def get_cell_href(number):
    cell_xpath = f'//*[@id="ctl00_ctl54_g_077c3f62_96a4_43aa_b013_8e274cf2ce9d_ctl00_divIsi"]/table/tbody/tr[{number}]/td[2]/a'
    cell_element = driver.find_element(By.XPATH, cell_xpath)
    return cell_element.get_attribute('href')

# Get hrefs of the categories
category_details = [get_cell_href(number) for number in scrape_category_numbers]

# Print the hrefs
print(category_details)


# Quit the driver
driver.quit()