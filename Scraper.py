import os
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

def immonet_parser(page_source):
    ''' Parser extracts infos from immonet.de search results '''

    soup = BeautifulSoup(page_source, "html.parser")

    # find divs of all apartments on page
    selObjects = soup.find_all("div", {"id": re.compile("^selObject_")}) # Find all 
    print("Found {} aparments on page".format(len(selObjects)))

    df = pd.DataFrame(columns=["id","title","bullets","tags","price","area","rooms"])
    for i, selObject in enumerate(selObjects):
        print("- Extracting sell Object: {}/{}".format(i, len(selObjects)-1))
        id = selObject.get('id')

        # extract elements                      #TODO add error handling!
        title = selObject.find("a", {"id": re.compile("^lnkToDetails_")})
        title = " ".join(title.get_text().split())

        bullets = selObject.find("span", class_="text-100")
        bullets = bullets.get_text().split()
        
        tags = selObject.find_all("span", class_="tag-element-50")
        tags = [t.get_text() for t in tags]
        
        price = selObject.find("div", {"id": re.compile("^selPrice_")})
        price = " ".join(price.get_text().split())
        
        area = selObject.find("div", {"id": re.compile("^selArea_")})
        area = " ".join(area.get_text().split())
        
        rooms = selObject.find("div", {"id": re.compile("^selRooms_")})
        rooms = " ".join(rooms.get_text().split())
        
        df = df.append({"id":id, "title":title, "bullets":bullets, "tags":tags, "price":price, "area":area, "rooms":rooms}, ignore_index=True)
    return df


# Operating in headless mode
opts = Options()
opts.headless = False

# Try these websites: https://trusted.de/immoscout24-alternativen
print("Loading webpage..")
driver = webdriver.Firefox(options=opts, executable_path="geckodriver.exe")
driver.get("https://www.immonet.de/immobiliensuche/sel.do?parentcat=1&objecttype=1&pageoffset=1&listsize=26&suchart=1&sortby=0&city=121673&marketingtype=2&page=2")

df = immonet_parser(driver.page_source)
df.to_csv("immo_data.csv")