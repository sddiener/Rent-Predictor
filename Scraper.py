import os
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time



def immonet_parser(page_source):
    ''' Parser extracts infos from immonet.de search results '''

    soup = BeautifulSoup(page_source, "html.parser")

    # find divs of all apartments on page
    selObjects = soup.find_all("div", {"id": re.compile("^selObject_")}) # Find all 
    print("Found {} aparments on page".format(len(selObjects)))

    for i, selObject in enumerate(selObjects):
        print("- Extracting sell Object: {}".format(i))
        id = selObject.get('id')

        # extract elements
        titles = selObject.find_all("a", {"id": re.compile("^lnkToDetails_")})
        bullets = selObject.find_all("span", class_="text-100")      
        tags = selObject.find_all("span", class_="tag-element-50")
        price = selObject.find_all("div", {"id": re.compile("^selPrice_")})
        area = selObject.find_all("div", {"id": re.compile("^selArea_")})
        rooms = selObject.find_all("div", {"id": re.compile("^selRooms_")})

        # convert to text # TODO better way to extract relevant information? split/strip
        title_txt = [i.get_text() for i in titles]
        bullets_txt = [i.get_text() for i in bullets]
        tags_txt = [i.get_text() for i in tags]
        price_txt = [i.get_text() for i in price]
        area_txt = [i.get_text() for i in area]
        rooms_txt = [i.get_text() for i in rooms]

        return # TODO return sth. 





# Operating in headless mode
opts = Options()
opts.headless = False

# Try these websites: https://trusted.de/immoscout24-alternativen
print("Loading webpage..")
driver = webdriver.Firefox(options=opts, executable_path="geckodriver.exe")
driver.get("https://www.immonet.de/immobiliensuche/sel.do?parentcat=1&objecttype=1&pageoffset=1&listsize=26&suchart=1&sortby=0&city=121673&marketingtype=2&page=2")

# # save page to file
# with open("soup1.html", "w", encoding='utf-8') as file:
#     file.write(str(soup))

# # load file again
# page_source_html = open("soup1.html").read()

immonet_parser(driver.page_source)

# DESCRIPTION:
# < a id="lnkToDetails_44898080" title="HELLES 3-ZI DACHGESCHOSS-LOFT / TOP AUSSTATTUNG / IM GRÜNEN"
# - HELLES 3-ZI DACHGESCHOSS-LOFT / TOP AUSSTATTUNG / IM GRÜNEN

# TAGS:
# <div class="box-25">
# 			<span class="tag-element-50">Balkon</span>
# 			<span class="tag-element-50">Garten</span>

# KEYFACTS: 
# PRICE:
# <div id="keyfacts-bar"
# - <div id="selPrice_42828686" >
# -- <span> 1000 €

# AREA:
# - <div id="selArea_42828686" > 
# -- <p> 36 m²

# ROOM NR:
# - <div id="selRooms_42828686" >
# -- <p> 2 rooms