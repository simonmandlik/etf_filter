# ETF scraping tool

Personally, I use this to filter the [free ETF funds offered on DeGiro](https://www.degiro.co.uk/data/pdf/uk/commission-free-etfs-list.pdf) and select the most suitable for me.
Usage:

``` bash
python3 etf.py etf.txt
```
where `etf.txt` is a text file containing ISINs of all required ETFs (see `etf.txt` in the repo). The script scrapes information from [JustETF](http://justetf.com) and retrieves information about every ETF in a python dictionary. The fields are:

* *name* - The name of the fund
* *description* - A brief description of the ETF
* *ticker* - Fund's ticker
* *isin* - Fund's ISIN
* *currency* - Fund currency
* *fund_size* - The size of the fund
* *fund_size_category* - One of the three categories based on the assets under management - low/high/middle cap
* *ter* - Total Expense Ratio of the fund
* *distribution_policy* - The way how the fund distributes the gains (Accumulating, Dividend, etc...)
* *replication* - The means of replication (Physical, Synthetic, etd...)
* *listings* - Stock markets, where the fund is traded
* *last_quote* - The last quote
* *one_year_low_high* - The lowest/highest value over the last 52 weeks
* *inception_date* - The date when the fund was established
* *fund_domicile* - The domicile of the fund

## Filtering

The results can be further filtered by changing the `suitable` method:

``` python
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
```

For example, this selects all mid or high cap accumulating funds performing any kind of physical replication (there are more types listed on JustEtf), which are at least 3 years old.

## Disclaimer

Do not use for commercial purposes
