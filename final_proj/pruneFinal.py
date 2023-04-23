import os.path
import re

input_file = 'output2.txt'
output_file = 'final.txt'

# Check if output file already exists
if os.path.isfile(output_file):
    i = 0
    while os.path.isfile(f'final{i}.txt'):
        i += 1
    output_file = f'final{i}.txt'

# Read input file and check URLs for "spieler" and correct format
with open(input_file, 'r') as f:
    urls = f.readlines()

correct_format_urls = set()
for url in urls:
    if 'spieler' in url:
        match = re.search(r'^(https?://\S+/)\S+/spieler/(\d+)', url)
        if match:
            # Replace "profil" with "verletzungen" and construct the correct format URL
            domain = match.group(1)
            player_id = match.group(2)
            correct_url = f'{domain}verletzungen/spieler/{player_id}'
            correct_format_urls.add(correct_url)

# Write unique URLs with correct format to output file
with open(output_file, 'w') as f:
    for url in correct_format_urls:
        f.write(url + '\n')
