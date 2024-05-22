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

# define driver
options = webdriver.FirefoxOptions()
driver = webdriver.Firefox(options=options)

# define the url
url= "https://www.google.com/"

# print status
print("Please wait, start scraping...")

# wait for elements to show up
time.sleep(50)