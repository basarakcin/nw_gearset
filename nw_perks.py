import os
# import requests
import pip._vendor.requests as requests
from bs4 import BeautifulSoup

GENERATED_PERKS_LIST_URL="https://nwdb.info/db/perks/generated/page/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

def get_perks_from_page(filename):
    # Open the HTML file and parse it with BeautifulSoup
    with open(filename, encoding='utf-8') as file:
        soup = BeautifulSoup(file, "html.parser")

    # Initialize an empty list to hold the perks
    perks = []

    # Find all 'td' elements with class 'ellipsis svelte-o9f32n'
    for td in soup.find_all('td', {'class': 'ellipsis svelte-o9f32n'}):
        # Find the 'a' tag within the 'td' tag
        a = td.find('a', {'class': 'align-middle table-item-name color-rarity-0 svelte-o9f32n'})
        # If an 'a' tag was found
        if a:
            # Get the text of the 'a' tag, remove newline characters, and add it to the perks list
            perk = ' '.join(a.get_text().split())
            perks.append(perk)

    # Remove duplicates from the list
    perks = list(set(perks))

    return perks


def save_response_content_to_file(response, filename):
    with open(filename, "w", encoding='utf-8') as file:
        file.write(response.text)

def get_all_generated_perks():
    all_perks = []
    for page_num in range(1, 9):
        url = GENERATED_PERKS_LIST_URL + str(page_num)
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            filename = "{:02d}.html".format(page_num)
            save_response_content_to_file(response, filename)

            # Process the data here, e.g., parse the saved HTML file
            # or do whatever you need to do with the data.
            page_perks = get_perks_from_page(filename)
            all_perks.extend(page_perks)

            # delete the file after parsing it
            os.remove(filename)
        else:
            print(f"Failed to fetch data from page {page_num}. Status code: {response.status_code}")

    return all_perks
