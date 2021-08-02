import os
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

def immonet_parser(page_source):
    ''' Parser extracts infos from immonet.de search results '''

    soup = BeautifulSoup(page_source, "html.parser")

    selObjects = soup.find_all("div", {"id": re.compile("^selObject_")}) # Find all  apartments on page
    print("Found {} apartments on page".format(len(selObjects)))

    df = pd.DataFrame(columns=["id","title","bullets","tags","price","area","rooms"])

    for i, selObject in enumerate(selObjects): # extract info from apartments
        print("- Extracting sell Object: {}/{}".format(i, len(selObjects)-1))
        
        id = selObject.get('id')
        
        try:
            title = selObject.find("a", {"id": re.compile("^lnkToDetails_")})
            title = " ".join(title.get_text().split())
        except Exception as e:
            print("Error extracting title: {}".format(e))

        try:
            bullets = selObject.find("span", class_="text-100")
            bullets = bullets.get_text().split()
        except Exception as e:
            print("Error extracting bullets: {}".format(e))

        try:
            tags = selObject.find_all("span", class_="tag-element-50")
            tags = [t.get_text() for t in tags]
        except Exception as e:
            print("Error extracting tags: {}".format(e))

        try:
            price = selObject.find("div", {"id": re.compile("^selPrice_")})
            price = " ".join(price.get_text().split())
        except Exception as e:
            print("Error extracting price: {}".format(e))

        try:
            area = selObject.find("div", {"id": re.compile("^selArea_")})
            area = " ".join(area.get_text().split())
        except Exception as e:
            print("Error extracting area: {}".format(e))
        
        try:
            rooms = selObject.find("div", {"id": re.compile("^selRooms_")})
            rooms = " ".join(rooms.get_text().split())
        except Exception as e:
            print("Error extracting rooms: {}".format(e))

        df = df.append({"id":id, "title":title, "bullets":bullets, "tags":tags, "price":price, "area":area, "rooms":rooms}, ignore_index=True)
        
    return df


# Initialize browser in headless mode
opts = Options()
opts.headless = False
driver = webdriver.Firefox(options=opts, executable_path="geckodriver.exe") 

# Immonet city codes
city = ["121673", "87372",  "109447",  "113144", "105043",    "143262",   "100207",     "99990",    "102157", "116172"]
       # München, # Berlin, # Hamburg, # Köln,   # Frankfurt, # Stuttgart, # Düsseldorf, # Dortmund, # Essen, # Leipzig 

# TODO
# 1) Federal state 1-16 durchgehen!!! :D
# for state in range(16):
#     url = "https://www.immonet.de/immobiliensuche/sel.do?suchart=1&state=1&marketingtype=2&pageoffset=1&"\
#           "parentcat=1&sortby=19&listsize=26&objecttype=1&federalstate={}&page={}".format(state,page)
# 2) Weniger print statements
# - nur pages + link / selObj nummer bei error
# 3) Weniger CSV dateien speichern. zb nur alle 10 seiten oder so.

page = 0
while True:
    page +=1
    url = "https://www.immonet.de/immobiliensuche/sel.do?parentcat=1&objecttype=1&"\
          "pageoffset=1053&listsize=27&suchart=1&sortby=0&city={}&marketingtype=2&page={}".format(city[0],page)
    
    print("Load website. City: {}, Page: {} \n URL: {} \n".format(city,page,url))
    driver.get(url)

    df = immonet_parser(driver.page_source)

    if df.empty: # stops loop after all pages
        break

    df.to_csv("data/immo_data_city{}_page{}.csv".format(city,page))

    print("Saved data.\n\n")
    time.sleep(5)