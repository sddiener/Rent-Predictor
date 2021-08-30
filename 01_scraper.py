import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


def immonet_parser(page_source):
    ''' Parser extracts infos from immonet.de search results '''

    soup = BeautifulSoup(page_source, 'html.parser')

    # find all  apartments on page
    selObjects = soup.find_all('div', {'id': re.compile('^selObject_')})
    #print('- Extracting {} apartments'.format(len(selObjects)))

    df = pd.DataFrame()

    for i, selObject in enumerate(selObjects):  # extract info from apartments
        id = selObject.get('id')

        try:
            title = selObject.find('a', {'id': re.compile('^lnkToDetails_')})
            title = ' '.join(title.get_text().split())
        except Exception as e:
            print('- Error extracting title (selObj {}/{}): {}'.format(i, len(selObjects)-1, e))

        try:
            bullets = selObject.find_all('span', class_='text-100')
            bullets = [b.get_text().split() for b in bullets]
        except Exception as e:
            print('- Error extracting bullets (selObj {}/{}): {}'.format(i, len(selObjects)-1, e))

        try:
            tags = selObject.find_all('span', class_='tag-element-50')
            tags = [t.get_text() for t in tags]
        except Exception as e:
            print('- Error extracting tags (selObj {}/{}): {}'.format(i,
                  len(selObjects)-1, e))

        try:
            price = selObject.find('div', {'id': re.compile('^selPrice_')})
            price = ' '.join(price.get_text().split())
        except Exception as e:
            print('- Error extracting price (selObj {}/{}): {}'.format(i, len(selObjects)-1, e))

        try:
            area = selObject.find('div', {'id': re.compile('^selArea_')})
            area = ' '.join(area.get_text().split())
        except Exception as e:
            print('- Error extracting area (selObj {}/{}): {}'.format(i, len(selObjects)-1, e))

        try:
            rooms = selObject.find('div', {'id': re.compile('^selRooms_')})
            rooms = ' '.join(rooms.get_text().split())
        except Exception as e:
            print('- Error extracting rooms (selObj {}/{}): {}'.format(i, len(selObjects)-1, e))

        df = df.append({'id': id, 'title': title, 'bullets': bullets, 'tags': tags,
                       'price': price, 'area': area, 'rooms': rooms}, ignore_index=True)

    return df


if __name__ == '__main__':
    # Initialize browser
    opts = Options()
    opts.headless = True  # show browser bool
    driver = webdriver.Firefox(options=opts, executable_path='geckodriver.exe')

    # Loop through all 16 states
    for state in range(1, 17):  # loop 16 federal states
        page = 0

        # Loop through all pages
        while True:
            page += 1

            url = 'https://www.immonet.de/immobiliensuche/sel.do?suchart=1&state=1'\
                  '&marketingtype=2&pageoffset=1&parentcat=1&sortby=19&listsize=26'\
                  '&objecttype=1&federalstate={}&page={}'.format(state, page)

            print('Load State: {}, Page: {} URL: {}'.format(state, page, url))
            driver.get(url)

            # extract 6 cols: id, title, bullets, tags, price, area, rooms
            df = immonet_parser(driver.page_source)

            if df.empty:  # stops loop after all pages
                print("*** Parser returned empty data frame. Break while Loop. *** \n")
                break

            df['page'] = page
            df['state'] = state

            df.to_csv('downloads/state_{}/immo_data_state{}_page{}.csv'.format(state, state, page))
            time.sleep(0.5)
