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
    
    def create_season_dict(seasons):
        season_dict = {}
        for season in seasons:
            season_dict[season] = {'season': 0, 'count': 0}
        return season_dict

    seasons_dict = create_season_dict(seasons)

    for i, season in enumerate(seasons):
        seasons_dict[season]['count'] += 1

    # Check that the length of all injury-related lists are the same
    if not all(len(lst) == len(injuries) for lst in [dates_from, dates_to, days_out, games_missed]):
        raise ValueError("All injury-related lists must be the same length.")

    # Initialize the injury recovery times dictionary
    injury_recovery_times = {
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

    # Create a list of all injuries in lowercase
    injuries_lower = [injury.lower() for injury in injuries]

    # Get a list of all injuries not in the injury_recovery_times dictionary
    missing_injuries = list(set(injuries_lower) - set(injury_recovery_times.keys()))
    if missing_injuries:
        print(f"The following injuries are not in the injury_recovery_times dictionary: {missing_injuries}")

    # Calculate the Recovery Index for each injury
    recovery_ratios = []
    for i, injury in enumerate(injuries):
        if dates_to[i] is not None:  # Only consider injuries with valid end dates
            # Increment the count of injuries in the season for the current injury
            seasons_dict[season]['count'] += 1

            # Get the expected recovery time for the injury, default to 60 if not found
            expected_recovery_time = injury_recovery_times.get(injury.lower(), 60)

            # Calculate the recovery ratio for the injury
            recovery_ratio = days_out[i] / expected_recovery_time

            # Calculate the weighted recovery ratio by multiplying the recovery ratio by the number of games missed (plus 1 to avoid division by zero)
            weighted_recovery_ratio = recovery_ratio * (games_missed[i] + 1)

            # Append the weighted recovery ratio to the list of recovery ratios
            recovery_ratios.append(weighted_recovery_ratio)

            # Update the number of injuries in the same season for the current injury
            seasons_dict[season]['count'] += 1

    # Calculate the average recovery index
    average_recovery_index = sum(recovery_ratios) / len(recovery_ratios) if recovery_ratios else 0
    print(f"Average Recovery Index: {average_recovery_index}")

    driver.quit()

while True:
    url = input("Enter the URL of the player's injury history on Transfermarkt: ")
    if url.lower() == "quit":
        break
    get_injury_data(url)