import requests

# function to get the CIK of a company from the SEC database
def get_cik(ticker):
    ticker_symbol = ticker.upper()

    # getting all the companies ticker and CIK from the SEC database as a dictionary
    companyTickers = requests.get('https://www.sec.gov/files/company_tickers.json', headers={'User-Agent': "testing@gmail.com"}).json().values()

    # returns {'cik_str': 320193, 'ticker': 'AAPL', 'title': 'Apple Inc.'} for each company
    for company in companyTickers:
        if company['ticker'] == ticker_symbol:
            return(company)

    return('Ticker CIK not found in SEC database')

# function to get the SEC financial reports of a company
def sec_filings(ticker):

    ticker_symbol = ticker.upper()

    # grab CIK and fill leading zeroes
    cik = str(get_cik(ticker_symbol)['cik_str']).zfill(10)

    filingData = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json',headers={'User-Agent': "testing@gmail.com"}).json()

    # used to check the key names for category of data
    print(filingData['facts']['us-gaap'].keys())

    # this is how to grab the data from the json api
    print(filingData['facts']['us-gaap']['AccountsReceivableNetCurrent']['units']['USD'])

    return

print(sec_filings('RL'))