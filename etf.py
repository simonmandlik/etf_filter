from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import sys
from pprint import pprint
import datetime

URL_OVERVIEW = 'https://www.justetf.com/uk/etf-profile.html?isin={0}&tab=overview'
URL_LISTING = 'https://www.justetf.com/uk/etf-profile.html?isin={0}&tab=listing'

def scrape_etf_overview(response):
    etf = {}
    etf['name'] = response.find('span', attrs={'class': 'h1'}).text.strip()
    isin, ticker = response.find('span', attrs={'class': 'identfier'}).findAll('span', attrs={'class': 'val'})
    etf['isin'] = isin.text.strip()[:-1] # they put ',' after ISIN in the tag
    etf['ticker'] = ticker.text.strip()
    etf['description'] = response.find(string='Investment strategy').findNext('p').contents[0].strip()
    etf['last_quote'] = ' '.join(map(lambda x: x.contents[0], response.find('h2', string='Quote').findNext('div', attrs={'class': 'val'}).findAll('span')))
    etf['one_year_low_high'] = list(response.find('div', string="52 weeks low/high").parent.div.children)
    del etf['one_year_low_high'][1]
    etf['one_year_low_high'] = re.sub('[\t\n]', '', '/'.join(etf['one_year_low_high']))
    etf['fund_size'] = re.sub('[\t\n]', '', response.find('div', string='Fund size').findPrevious('div').contents[0].strip())
    fs_category = response.find('img', attrs={'class': 'uielem', 'data-toggle': 'tooltip'})['src']
    etf['fund_size_category'] = "low cap" if fs_category[-5] == "1" else "mid cap" if fs_category[-5] == "2" else "high cap"
    etf['replication'] = re.sub('[\t\n]', '', response.find(string="Replication").parent.parent.find_next_sibling('td').text.strip())
    etf['currency'] = response.find(string="Fund currency").parent.find_next_sibling('td').text.strip()
    etf['inception_date'] = datetime.datetime.strptime(response.find(string="Inception Date").parent.find_next_sibling('td').text.strip(), "%d %B %Y")
    etf['ter'] = response.find(string="Total expense ratio").parent.find_previous_sibling('div').text.strip()
    etf['distribution_policy'] = response.find(string="Distribution policy").parent.find_next_sibling('td').text.strip()
    etf['fund_domicile'] = response.find(string="Fund domicile").parent.find_next_sibling('td').text.strip()
    return etf

def scrape_etf_listing(response):
    etf = {}
    etf['listings'] = []
    for r in response.find('h2', string='Listing').parent.parent.parent.find_next_sibling().findAll('tr'):
        etf['listings'].append(r.td.text.strip())
    return etf

def scrape_etf(isin):
    etf = {}
    try:
        with urlopen(URL_OVERVIEW.format(isin)) as connection:
            response = BeautifulSoup(connection, 'html.parser')
    except AttributeError as e:
        print("Fund isin '{}' not found!".format(isin), file=sys.stderr)
    etf = {**etf, **scrape_etf_overview(response)}
    try:
        with urlopen(URL_LISTING.format(isin)) as connection:
            response = BeautifulSoup(connection, 'html.parser')
    except AttributeError as e:
        print("Fund isin '{}' not found!".format(isin), file=sys.stderr)
    etf = {**etf, **scrape_etf_listing(response)}
    return etf

def suitable(etf):
    if etf['distribution_policy'] != 'Accumulating':
        return False
    if etf['fund_size_category'] not in ['mid cap', 'high cap']:
        return False
    if re.match(r"[pP]hysical", etf['replication']) is None:
        return False
    # at least 3 years old
    dt = datetime.timedelta(days=3*365)
    if etf['inception_date'] > datetime.datetime.now() - dt:
        return False
    return True

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("usage: python3 etf.py etf_list.txt", file=sys.stderr)
    else:
        with open(sys.argv[1], 'r') as f:
            for line in f:
                etf = scrape_etf(line.strip())
                if suitable(etf):
                    pprint(etf)


