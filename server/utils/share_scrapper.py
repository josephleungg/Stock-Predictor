from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import yfinance as yf
import requests
import pandas as pd
import matplotlib.pyplot as plt
import csv

# converts csv strings from M, B, T to float
def milbiltril_to_float(x):
    if 'B' in x:
        multi = 10**9
    elif 'M' in x:
        multi = 10**6
    elif 'T' in x:
        multi = 10**12
    else:
        multi = 10**6
    convert_part = float(x.replace('B','').replace('M','').replace('T',''))
    return convert_part * multi

# function to scrape site for shares outstanding data for any company
def scrape_shares(ticker):
    # url for parsing
    url = 'https://www.sharesoutstandinghistory.com/?symbol='
    ticker_symbol = ticker.upper()

    # get the page and parse the outstanding shares table
    page = requests.get(url + ticker_symbol)

    # checking if the ticker symbol is valid
    if(page.status_code != 200):
        print('Scraping Failed')
        return

    soup = BeautifulSoup(page.text, 'html.parser')

    # making sure the ticker symbol exists
    try:
        shares_table_rows = soup.table.table.find_all('tr')
    except:
        print("Ticker Symbol not found")
        return

    # write each cell in the table to a list
    row_data = []
    for rows in shares_table_rows:
        row_data.append([rows.find_all('td')[0].text.strip(), rows.find_all('td')[1].text.strip()])

    # open a new csv file with write
    with open('../data/' + ticker_symbol + '_outstanding_shares.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        # write the list to the csv file
        writer.writerows(row_data)

    print('Scraping Successful')

    # read the csv file and fill in missing dates
    df = pd.read_csv('../data/' + ticker_symbol + '_outstanding_shares.csv',parse_dates=['Date'])
    df = df.set_index('Date')
    df = df.resample('D').asfreq()
    df = df.ffill(axis=0)
    df = df[df.index.dayofweek < 5]

    # convert the shares outstanding number to float
    df['{} Shares Outstanding'.format(ticker_symbol)] = df['{} Shares Outstanding'.format(ticker_symbol)].apply(milbiltril_to_float)

    # save the modified data to a new csv file
    df.to_csv('../data/' + ticker_symbol + '_outstanding_shares.csv')

    print('Data Modified')

    return df

# finding the marketcap with the shares outstanding data and the stock price
def find_marketcap(ticker, df):
    ticker_symbol = ticker.upper()

    # getting stock price data from yahoo finance
    stock_price = yf.Ticker(ticker_symbol)
    
    stock_price = stock_price.history(start=df.index.min().date(), end=df.index.max() + timedelta(days=1))
    stock_price = stock_price.drop(['Open','High','Low','Volume','Dividends','Stock Splits'], axis=1)

    print('Successfully retrieved stock price data')

    # Convert the timezone-aware datetime index to a timezone-naive datetime index
    df.index = df.index.tz_localize(None)
    stock_price.index = stock_price.index.tz_localize(None)

    # concatenate the two dataframes to multiply the data together to get marketcap
    new_df = pd.concat([df,stock_price],axis=1)
    new_df['marketcap'] = new_df['{} Shares Outstanding'.format(ticker_symbol)] * new_df['Close']

    # drop rows with missing values
    new_df = new_df.dropna()

    # overwrite the csv file with the new data
    new_df.to_csv('../data/' + ticker_symbol + '_outstanding_shares.csv')

    # renaming file to better naming convention
    os.rename('../data/' + ticker_symbol + '_outstanding_shares.csv', '../data/' + ticker_symbol + '_data.csv')

    print('Marketcap data saved to csv file')

dataframe = scrape_shares("TSLA")
find_marketcap("TSLA", dataframe)