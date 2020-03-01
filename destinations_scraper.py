# Import packages
import time
import csv
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions

# Scraping list of all countries using BeauifulSoup

# list of countries data source
country_url = "https://www.britannica.com/topic/list-of-countries-1993160"

country_list = []

try:
    r = requests.get(country_url)
    # converting html to string
    html_doc = r.text
    # initiating a beautifulsoup object
    soup = BeautifulSoup(html_doc, features="html.parser")
    soup.encode("utf-8")
    # finding html tags with country name. identified a tags with the following class attribute value
    scraped_list = soup.find_all("a", class_="md-crosslink")
    country_list = [country.get_text() for country in scraped_list][2:]
except requests.exceptions.ConnectionError:
    raise ConnectionError(
        "Could not connect to \"https://www.britannica.com/topic/list-of-countries-1993160\". Please try again later.")

# ------------------------------------------------------------

# Extracting tourist attractions using Selenium

# initialise firefox browser
browser = webdriver.Firefox()

# empty dict for populating with attractions
country_tourists_attractions_dict = {}


def get_country_tourist_destinations(country_name):
    """
        Using Selenium to automate user actions in getting 
        tourist destinations per country
    """
    # run google.com
    browser.get('https://www.google.com/')
    inputbox = browser.find_element_by_class_name('gLFyf')
    inputbox.send_keys(f'tourist attractions in {country_name}')
    inputbox.send_keys(Keys.ENTER)
    print(f"\nStarting to scrape for {country_name}.", flush=True)
    # wait for browser to load
    time.sleep(3)
    browser.find_element_by_partial_link_text('More ').click()
    # wait for browser to load
    time.sleep(1)
    try:
        # click 'See all top sights'
        browser.find_element_by_xpath('//*[@id="yDmH0d"]/c-wiz[1]/div/div/c-wiz/div/div[2]/div[1]/div/c-wiz/div/div[1]/div[3]/div/div/button/div[2]').click()
        time.sleep(2)
        print(f"Scraping in progress. . .", flush=True)
        # tourist attractions tags are identified by unique class name "YmWhbc"
        destinations_list = browser.find_elements_by_class_name("YmWhbc")
        # unpacking list to retrieve attraction name
        destinations_list = [d.text for d in destinations_list]
        print(f"Scraping for {country_name} completed.\n", flush=True)
        # updating dictionary with country as the key, and list of attractions as the value
        country_tourists_attractions_dict[country_name] = destinations_list
    except exceptions.NoSuchElementException:
        # print(f"Scraping for {country_name} has failed. Please try again later.", flush=True)
        print(f"Scraping in progress. . . More destinations by Google.", flush=True)
        destinations_list = browser.find_elements_by_tag_name("h2")
        destinations_list = [d.text for d in destinations_list]
        print(f"Scraping for {country_name} completed.\n", flush=True)
        country_tourists_attractions_dict[country_name] = destinations_list



# iterate for each country
# for the sake of brevity, only 5 random countries would be run
random.shuffle(country_list)
for country in country_list[:5]:
    get_country_tourist_destinations(country)

# convert to pandas DataFrame from Python dictionary object
df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in country_tourists_attractions_dict.items() ]))

# some DataFrame cleaning
df.drop(index=[0,1,2,3,4,5,6,7,8,], axis=0, inplace=True)

# convert to csv
df.to_csv('tourist_destinations.csv', encoding='utf-8', index=False)

# completion message
print(".\n.\n.\n\nAll Scraping is completed. You can view the csv file now.")