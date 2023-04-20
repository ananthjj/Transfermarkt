# Author: ananthjj
# Date: 4/20/23
# Transfermarkt.us Detailed Injury History Web Scraper

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def get_injury_data(url):
    options = Options()
    options.headless = True  # run Chrome in headless mode

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    seasons = []
    injuries = []
    dates_from = []
    dates_to = []
    days_out = []
    games_missed = []

    recovery_indices = []

    while True:
        table = soup.find('table', {'class': 'items'})
        rows = table.find_all('tr', {'class': ['odd', 'even', 'odd selected','even selected']})

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 6:
                season = cols[0].text.strip()
                season_start = int(season[:2]) + 2000
                season_end = int(season[-2:]) + 2000
                seasons.append(f"{season_start}-{season_end}")
                injuries.append(cols[1].text.strip())

                try:
                    date_from = datetime.strptime(cols[2].text.strip(), '%b %d, %Y').strftime('%Y-%m-%d')
                except ValueError:
                    date_from = None
                dates_from.append(date_from)

                try:
                    date_to = datetime.strptime(cols[3].text.strip(), '%b %d, %Y').strftime('%Y-%m-%d')
                except ValueError:
                    date_to = None
                dates_to.append(date_to)

                days_out.append(int(cols[4].text.strip().split(' ')[0]))
                games_missed.append(int(cols[5].text.strip().replace('-', '0')))

        # Check if there is a next page
        next_page = soup.find('li', {'class': 'tm-pagination__list-item--icon-next-page'})
        if not next_page:
            break

        # If there is a next page, click on it and update the soup
        next_page_link = next_page.find('a')['href']
        driver.get('https://www.transfermarkt.us' + next_page_link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    print('Seasons:', seasons)
    print('Injuries:', injuries)
    print('Dates From:', dates_from)
    print('Dates To:', dates_to)
    print('Days Out:', days_out)
    print('Games Missed:', games_missed)

    driver.quit()

while True:
    url = input("Enter the URL of the player's injury history on Transfermarkt: ")
    if url.lower() == "quit":
        break
    get_injury_data(url)
