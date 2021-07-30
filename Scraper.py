import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

# Operating in headless mode
opts = Options()
opts.headless = False

# Try these websites: https://trusted.de/immoscout24-alternativen

driver = webdriver.Firefox(options=opts, executable_path=os.path.dirname(__file__) + "/geckodriver.exe")
driver.get("https://www.immonet.de/immobiliensuche/sel.do?parentcat=1&objecttype=1&pageoffset=1&listsize=26&suchart=1&sortby=0&city=121673&marketingtype=2&page=2")
#driver.get("https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Munchen.90.1.1.0.html")
#driver.get("https://www.immobilienscout24.de/Suche/de/bayern/muenchen/wohnung-mieten") #?pagenumber=2

time.sleep(10)
print("try page 1")
soup1 = BeautifulSoup(driver.page_source, 'html.parser')
print(soup1.prettify)
