from urllib.request import urlopen
from bs4 import BeautifulSoup
from pprint import pprint
import re
import sys
import datetime

URL = 'https://www.justetf.com/uk/etf-profile.html?isin={0}'

def process_string(s):
    s = s.strip()
    s = re.sub(' +', ' ', s)
    s = re.sub('\n', '', s)
    return s.strip()

def scrape_etf_params(response):
    etf = {}
    etf['name'] = response.find('span', attrs={'class': 'h1'}
            ).text.strip()
    isin, ticker = response.find('span', attrs={'class': 'identfier'}
            ).findAll('span', attrs={'class': 'val'})
    etf['isin'] = isin.text.strip()[:-1] # they put ',' after ISIN in the tag
    etf['ticker'] = ticker.text.strip()
    etf['description'] = response.find(string=re.compile('Investment strategy')
            ).findNext('p').contents[0].strip()
    etf['description'] = process_string(etf['description'])
    etf['last_quote'] = ' '.join(map(lambda x: x.contents[0], response.find('div', string=re.compile('Quote')
        ).findNext('div', attrs={'class': 'val'}
        ).findAll('span')))
    etf['one_year_low_high'] = list(response.find('div', string=re.compile("52 weeks low/high")
        ).parent.div.children)
    del etf['one_year_low_high'][1]
    etf['one_year_low_high'] = re.sub('[\t\n]', '', '/'.join(etf['one_year_low_high']))
    etf['one_year_low_high'] = process_string(etf['one_year_low_high'])
    etf['fund_size'] = re.sub('[\t\n]', '', response.find('div', string=re.compile('Fund size')
        ).findPrevious('div').contents[0].strip())
    etf['fund_size'] = process_string(etf['fund_size'])
    fs_category = response.find('img', attrs={'alt': 'Fund size category', 'data-toggle': 'tooltip'}
        )['class']
    etf['fund_size_category'] = "low cap" if fs_category[-1] == "1" else "mid cap" if fs_category[-1] == "2" else "high cap"
    etf['replication'] = re.sub('[\t\n]', '', response.find(string=re.compile("Replication")
        ).parent.parent.find_next_sibling('td').text.strip())
    etf['replication'] = process_string(etf['replication'])
    etf['currency'] = response.find(string=re.compile("Fund currency")
            ).parent.find_next_sibling('td').text.strip()
    etf['inception_date'] = datetime.datetime.strptime(response.find(string=re.compile("Inception/ Listing Date")
        ).parent.find_next_sibling('td').text.strip(), "%d %B %Y")
    etf['ter'] = response.find(string=re.compile("Total expense ratio")
        ).parent.find_previous_sibling('div').text.strip()
    etf['distribution_policy'] = response.find(string=re.compile("Distribution policy")
        ).parent.find_next_sibling('td').text.strip()
    etf['fund_domicile'] = response.find(string=re.compile("Fund domicile")
        ).parent.find_next_sibling('td').text.strip()
    # etf['listings'] = []
    # for r in response.find('h3', string=re.compile('Listings')
    #         ).parent.parent.parent.find_next_sibling().findAll('tr'):
    #     etf['listings'].append(r.td.text.strip())
    return etf

def scrape_etf(isin):
    etf = {}
    try:
        with urlopen(URL.format(isin)) as connection:
            response = BeautifulSoup(connection, 'html.parser')
        return scrape_etf_params(response)
    except AttributeError as e:
        print("Fund isin '{}' not found!".format(isin), file=sys.stderr)
    return None

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


