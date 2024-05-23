from bs4 import BeautifulSoup
import requests
import csv

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

scrape_shares("vrsn")