# Author: ananthjj
# Date: 3/31/23
# Transfermarkt.us Detailed Injury History Web Scraper

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

options = Options()
options.headless = True  # run Chrome in headless mode

url = 'https://www.transfermarkt.us/pedri/verletzungen/spieler/683840/plus/1'

driver = webdriver.Chrome(options=options)
driver.get(url)

soup = BeautifulSoup(driver.page_source, 'html.parser')

table = soup.find('table', {'class': 'items'})
rows = table.find_all('tr', {'class': ['odd', 'even', 'odd selected','even selected']})

seasons = []
injuries = []
dates_from = []
dates_to = []
days_out = []
games_missed = []

for row in rows:
    cols = row.find_all('td')
    if len(cols) >= 6:
        seasons.append(cols[0].text.strip())
        injuries.append(cols[1].text.strip())
        dates_from.append(cols[2].text.strip())
        dates_to.append(cols[3].text.strip())
        days_out.append(cols[4].text.strip())
        games_missed.append(cols[5].text.strip())

print('Seasons:', seasons)
print('Injuries:', injuries)
print('Dates From:', dates_from)
print('Dates To:', dates_to)
print('Days Out:', days_out)
print('Games Missed:', games_missed)

driver.quit()