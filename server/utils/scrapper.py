from bs4 import BeautifulSoup
import requests

url = 'https://www.sharesoutstandinghistory.com/?symbol='
ticker_symbol = 'AAPL'

response = requests.get(url + ticker_symbol)
print(response)