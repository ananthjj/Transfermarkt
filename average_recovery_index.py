# Author: ananthjj
# Date: 4/20/23
# Transfermarkt.us Detailed Injury History Web Scraper with Average Recovery Index

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
import pandas as pd
from urllib.parse import urlparse

urls = ['https://www.transfermarkt.us/marc-andre-ter-stegen/verletzungen/spieler/74857/', 'https://www.transfermarkt.us/ronald-araujo/verletzungen/spieler/480267', 'https://www.transfermarkt.us/andreas-christensen/verletzungen/spieler/196948']

class injuryDataCreator():
    def __init__(self, filename):
        self.inputfile = filename
        self.injuriesDf = None
        self.fill = 0
        self.injury_recovery_times = {
            'abdominal influenza': 60,
            'cold': 6,
            'knee surgery': 135,
            'rest': 1,
            'knee injury': 35,
            'knee problems': 28,
            'shoulder injury': 31.5,
            'muscle injury': 14,
            'dental surgery': 10.5,
            'back injury': 38.5,
            'influenza': 10.5,
            'muscular problems': 14,
            'wrist injury': 31.5,
            'wirst injury': 31.5,
            'tendonitis': 24.5,
            'torn muscle fibre': 31.5,
            'fractured toe': 42,
            'ligament tear': 63,
            'fractured finger': 28,
            'achilles tendinitis': 24.5,
            'plantar fasciitis': 63,
            'shin splints': 21,
            'stress fracture': 63,
            'hip flexor strain': 31.5,
            'unknown injury': 22,
            'corona virus': 17.5,
            'ill': 7.5,
            'surgery': 120,
            'tear in the abductor muscle': 35,
            'adductors avulsion': 49,
            'concussion': 14,
            'calf injury': 31.5,
            'hand injury': 21,
            'hamstring injury': 28,
            'ankle injury': 31.5,
            'sprained ankle': 21,
            'head injury': 14,
            'foot injury': 42,
            'back trouble': 30,
            'knock': 7,
            'adductor problems': 21,
            'heart condition': 90,
            'bone chipping': 45,
            'nose injury': 14,
            'malaria': 30,
            'calf problems': 28,
            'dead leg': 7,
            'hip problems': 35,
            'toe injury': 21,
            'bruise': 7,
            'problems with the hip flexor': 32,
            'torn muscle bundle': 40,
            'fractured jaw': 42,
            'thigh muscle strain': 21,
            'thigh problems': 28,
            'achilles tendon problems': 35,
            'groin injury': 21,
            'cruciate ligament rupture': 180,
            'mensical laceration': 30,
            'bruised knee': 7,
            'bruised hip': 7,
            'fitness': 14,
            'torn ankle ligament': 42,
            'pulled hamstring at the adductors': 28,
            'minor knock': 7,
            'disrupted calf muscle': 21,
            'leg injury': 28,
            'calf muscle strain': 21,
            'infection': 14,
            'metatarsal fracture': 90,
            'strain': 14,
            'flu': 7,
            'bone bruise': 21,
            'pubitis': 42,
            'quarantine': 14,
            'stretched ligament': 28,
            'kidney problems': 30,
            'ankle problems': 28,
            'forearm fracture': 56,
            'medial collateral ligament knee injury': 42,
            'back bruise': 14,
            'kidney stone surgery': 21,
            'bruised foot': 14,
            'ligament problems': 28,
            'muscle fiber tear': 35,
            }
        # print(filename)
        
    def loadCsv(self, filename):
        self.injuriesDf = pd.read_csv(filename)
        print(self.injuriesDf)

    def load(self):
        data = {
            'playerEncodedName': [],
            'Id': [],
            'season': [],
            'injury': [],
            'startDate': [],
            'endDate': [],
            'daysOut': [],
            'gamesMissed': []
        }
        self.injuriesDf = pd.DataFrame(data)
        with open(self.inputfile, 'r') as f:
            for line in f:
                print(line)
                try:
                    self.add_injury_data(line.strip())
                except:
                    print(line + " has no data")
                    continue
    
    def get(self, player_id=None, player_encoded_name=None):
        recovery_indices = []
        if player_id is not None:
            # print(self.injuriesDf.dtypes)
            # print(type(player_id))
            if self.injuriesDf['Id'].dtype == int:
                player_id = int(player_id)

            group_df = self.injuriesDf[self.injuriesDf['Id'] == player_id]
            # print(group_df)
            recovery_index = self.get_recovery_index(group_df)
            recovery_indices.append(recovery_index)
            return recovery_indices
        elif player_encoded_name is not None:
            groups = self.injuriesDf[self.injuriesDf['playerEncodedName'] == player_encoded_name].groupby(['Id'])
            if groups.ngroups == 0:
                return recovery_indices
            for group_name, group_df in groups:
                print(group_df)
                recovery_index = self.get_recovery_index(group_df)
                recovery_indices.append(recovery_index)
            return recovery_indices[0] if len(recovery_indices) == 1 else recovery_indices
        else:
            return recovery_indices


    def get_recovery_index(self, group_df):
        
        # Create a dictionary to keep track of injuries in the same season
        seasons_dict = {}
        for season in group_df['season'].unique():
            seasons_dict[season] = {'count': 0}

        # Calculate the Recovery Index for each injury
        recovery_ratios = []
        for i, row in group_df.iterrows():
            print(row)
            if row['endDate'] is not None and row['startDate'] is not None: # Only consider injuries with valid end dates
                # Increment the count of injuries in the season for the current injury
                season = row['season']
                seasons_dict[season]['count'] += 1

                # Get the expected recovery time for the injury, default to 60 if not found
                injury = row['injury']
                expected_recovery_time = self.injury_recovery_times.get(injury.lower(), 60)

                # Calculate the recovery ratio for the injury
                days_out = row['daysOut']
                recovery_ratio = days_out / expected_recovery_time

                # Calculate the weighted recovery ratio by multiplying the recovery ratio by the number of games missed (plus 1 to avoid division by zero)
                gamesMissed = row['gamesMissed']
                weighted_recovery_ratio = recovery_ratio * (gamesMissed + 1)

                # Append the weighted recovery ratio to the list of recovery ratios
                recovery_ratios.append(weighted_recovery_ratio)

        # Calculate the average recovery index
        total_count = sum([seasons_dict[season]['count'] for season in seasons_dict])
        if total_count > 0:
            weighted_sum = sum([recovery_ratios[i] * group_df.iloc[i]['gamesMissed'] for i in range(len(recovery_ratios))])
            index = weighted_sum / total_count
            return index
        return None

    def add_data(self, player_encoded_name, player_id, season, injury, startDate, endDate, daysOut, gamesMissed):
        data = {
            'playerEncodedName': [player_encoded_name],
            'Id': [player_id],
            'season': [season],
            'injury': [injury],
            'startDate': [startDate],
            'endDate': [endDate],
            'daysOut': [daysOut],
            'gamesMissed': [gamesMissed]
        }
        new_row = pd.DataFrame(data)
        print(new_row)
        self.injuriesDf = pd.concat([self.injuriesDf, new_row], ignore_index=True)

    def save(self, filename):
        self.injuriesDf.to_csv(filename)

    def add_injury_data(self, url):
        # print(url)
        parsed_url = urlparse(url)
        encoded_name = parsed_url.path.split('/')[1].replace('-', ' ')
        player_id = parsed_url.path.split('/')[-1]

        options = Options()
        options.headless = True  # run Chrome in headless mode

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        index = 0

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

                    try:
                        date_from = datetime.strptime(cols[2].text.strip(), '%b %d, %Y').strftime('%Y-%m-%d')
                    except ValueError:
                        date_from = None
                    try:
                        date_to = datetime.strptime(cols[3].text.strip(), '%b %d, %Y').strftime('%Y-%m-%d')
                    except ValueError:
                        date_to = None
                    
                    self.add_data(encoded_name, player_id, f"{season_start}-{season_end}", cols[1].text.strip(), date_from, date_to, int(cols[4].text.strip().split(' ')[0]), int(cols[5].text.strip().replace('-', '0')))

            # Check if there is a next page
            next_page = soup.find('li', {'class': 'tm-pagination__list-item--icon-next-page'})
            if not next_page:
                break

            # If there is a next page, click on it and update the soup
            next_page_link = next_page.find('a')['href']
            driver.get('https://www.transfermarkt.us' + next_page_link)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # print('Seasons:', seasons)
        # print('Injuries:', injuries)
        # print('Dates From:', dates_from)
        # print('Dates To:', dates_to)
        # print('Days Out:', days_out)
        # print('Games Missed:', games_missed)
        
    #     def create_season_dict(seasons):
    #         season_dict = {}
    #         for season in seasons:
    #             season_dict[season] = {'season': 0, 'count': 0}
    #         return season_dict

    #     seasons_dict = create_season_dict(seasons)

    #     for i, season in enumerate(seasons):
    #         seasons_dict[season]['count'] += 1

    #     # Check that the length of all injury-related lists are the same
    #     if not all(len(lst) == len(injuries) for lst in [dates_from, dates_to, days_out, games_missed]):
    #         raise ValueError("All injury-related lists must be the same length.")

    #     # Initialize the injury recovery times dictionary
    #     injury_recovery_times = {
    #     'abdominal influenza': 60,
    #     'cold': 6,
    #     'knee surgery': 135,
    #     'rest': 1,
    #     'knee injury': 35,
    #     'knee problems': 28,
    #     'shoulder injury': 31.5,
    #     'muscle injury': 14,
    #     'dental surgery': 10.5,
    #     'back injury': 38.5,
    #     'influenza': 10.5,
    #     'muscular problems': 14,
    #     'wrist injury': 31.5,
    #     'wirst injury': 31.5,
    #     'tendonitis': 24.5,
    #     'torn muscle fibre': 31.5,
    #     'fractured toe': 42,
    #     'ligament tear': 63,
    #     'fractured finger': 28,
    #     'achilles tendinitis': 24.5,
    #     'plantar fasciitis': 63,
    #     'shin splints': 21,
    #     'stress fracture': 63,
    #     'hip flexor strain': 31.5,
    #     'unknown injury': 22,
    #     'corona virus': 17.5,
    #     'ill': 7.5,
    #     'surgery': 120,
    #     'tear in the abductor muscle': 35,
    #     'adductors avulsion': 49,
    #     'concussion': 14,
    #     'calf injury': 31.5,
    #     'hand injury': 21,
    #     'hamstring injury': 28,
    #     'ankle injury': 31.5,
    #     'sprained ankle': 21,
    #     'head injury': 14,
    #     'foot injury': 42,
    #     'back trouble': 30,
    #     'knock': 7,
    #     'adductor problems': 21,
    #     'heart condition': 90,
    #     'bone chipping': 45,
    #     'nose injury': 14,
    #     'malaria': 30,
    #     'calf problems': 28,
    #     'dead leg': 7,
    #     'hip problems': 35,
    #     'toe injury': 21,
    #     'bruise': 7,
    #     'problems with the hip flexor': 32,
    #     'torn muscle bundle': 40,
    #     'fractured jaw': 42,
    #     'thigh muscle strain': 21,
    #     'thigh problems': 28,
    #     'achilles tendon problems': 35,
    #     'groin injury': 21,
    #     'cruciate ligament rupture': 180,
    #     'mensical laceration': 30,
    #     'bruised knee': 7,
    #     'bruised hip': 7,
    #     'fitness': 14,
    #     'torn ankle ligament': 42,
    #     'pulled hamstring at the adductors': 28,
    #     'minor knock': 7,
    #     'disrupted calf muscle': 21,
    #     'leg injury': 28,
    #     'calf muscle strain': 21,
    #     'infection': 14,
    #     'metatarsal fracture': 90,
    #     'strain': 14,
    #     'flu': 7,
    #     'bone bruise': 21,
    #     'pubitis': 42,
    #     'quarantine': 14,
    #     'stretched ligament': 28,
    #     'kidney problems': 30,
    #     'ankle problems': 28,
    #     'forearm fracture': 56,
    #     'medial collateral ligament knee injury': 42,
    #     'back bruise': 14,
    #     'kidney stone surgery': 21,
    #     'bruised foot': 14,
    #     'ligament problems': 28,
    #     'muscle fiber tear': 35,
    #     }

    #     # Create a list of all injuries in lowercase
    #     injuries_lower = [injury.lower() for injury in injuries]

    #     # Get a list of all injuries not in the injury_recovery_times dictionary
    #     missing_injuries = list(set(injuries_lower) - set(injury_recovery_times.keys()))
    #     if missing_injuries:
    #         print(f"The following injuries are not in the injury_recovery_times dictionary: {missing_injuries}")

    #     # Calculate the Recovery Index for each injury
    #     recovery_ratios = []
    #     for i, injury in enumerate(injuries):
    #         if dates_to[i] is not None and dates_from[i] is not None: # Only consider injuries with valid end dates
    #             # Increment the count of injuries in the season for the current injury
    #             seasons_dict[season]['count'] += 1

    #             # Get the expected recovery time for the injury, default to 60 if not found
    #             expected_recovery_time = injury_recovery_times.get(injury.lower(), 60)

    #             # Calculate the recovery ratio for the injury
    #             recovery_ratio = days_out[i] / expected_recovery_time

    #             # Calculate the weighted recovery ratio by multiplying the recovery ratio by the number of games missed (plus 1 to avoid division by zero)
    #             weighted_recovery_ratio = recovery_ratio * (games_missed[i] + 1)

    #             # Append the weighted recovery ratio to the list of recovery ratios
    #             recovery_ratios.append(weighted_recovery_ratio)

    #             # Update the number of injuries in the same season for the current injury
    #             seasons_dict[season]['count'] += 1

    #     # Calculate the average recovery index
    #     average_recovery_index = sum(recovery_ratios) / len(recovery_ratios) if recovery_ratios else 0
    #     try:
    #         index = average_recovery_index
    #     except:
    #         return None

    #     driver.quit()

    # for url in urls:
    #     try:
    #         get_injury_data(url)
    #     except:
    #         #print(f"An error occurred while processing {url}. Skipping to next URL.")
    #         continue

    # with open('url_index.csv', mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(['URL', 'Index'])
        
    #     for url in urls:
    #         try:
    #             index = get_injury_data(url)
    #             if index is not None:
    #                 writer.writerow([url, index])
    #         except:
    #             print(f"An error occurred while processing {url}. Skipping to next URL.")
    #             continue
