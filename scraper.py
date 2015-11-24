"""
scraper.py defines the YahooScraper class to scrape yahoo for finance data.
"""

import pickle
import re
import requests

class YahooScraper():
    """Scrapes Yahoo Finance for data"""

    def __init__(self, features, feature_source_map, source_path):
        self.features = features
        self.feature_source_map = feature_source_map
        self.model = self.load_model(source_path)

    def load_model(self, source='model.pkl'):
        """Loads the model to use to predict

        :param source: the source pkl
        """

        return pickle.load(open(source))

    def check_invest(self, ticker):
        """Determines whether someone should invest in a given ticker

        :param ticker: the stock ticker
        :returns: True or False for whether one should invest
        """

        source = self.get_latest_source(ticker)
        feature_vector = self.scrape(source)

        feature_vector["stock_p_change"] = self.get_stock_p_change(ticker)
        feature_vector["sp500_p_change"] = self.get_sp500_p_change()

        x = []

        for f in self.features:
            if feature_vector[f] == "N/A":
                x.append(0.0)
            else:
                x.append(feature_vector[f])

        evaluation = self.model.predict(x)[0]

        return evaluation

    def get_stock_p_change(self, ticker):
        """Gets the percentage change between the current stock price and
        the stock price one year ago

        :param ticker: the stock ticker
        :returns: a tuple of the stock pct change and the current stock value
        """

        url = "http://finance.yahoo.com/d/quotes.csv?s=" + ticker + "&f=pm6"

        resp = requests.get(url)
        results = resp.text.split(',')

        current_price = float(results[0])
        percent_change = float(results[1][1:-2]) / 100

        return (percent_change, current_price)

    def get_sp500_p_change(self):
        """Get the percentage change between the current S&P500 price and
        the S&P500 price one year ago

        :returns: a tuple of the S&P500 pct change and the current S&P500 value
        """

        url = "http://finance.yahoo.com/d/quotes.csv?s=^GSPC&f=bm6"
        return (0.0, 0.0)

    def get_latest_source(self, ticker):
        """Gets the most recent Yahoo Finance data for a ticker

        :param ticker: the stock ticker
        :returns: the latest HTML source for the ticker
        """

        url = "http://finance.yahoo.com/q/ks?s=" + ticker + "+Key+Statistics"
        resp = requests.get(url)

        if resp.status_code != 200:
            raise ValueError("Invalid ticker")

        return resp.text

    def scrape(self, source):
        """Scrapes HTML files for data and saves it as a CSV.

        :param source: Yahoo Finance HTML page source
        :returns: a dict of feature/value pairs scraped from the source
        """

        feature_vector = {}

        for feature in self.features:

            source_feature = self.feature_source_map[feature]

            if source_feature == "N/A":
                feature_vector[feature] = "N/A"
                continue

            if source_feature == "Ticker":
                feature_vector[feature] = ticker
                continue

            r = re.escape(source_feature) + r'.*?(\d{1,8}\.\d{1,8}M?B?|N/A)%?'

            try:
                val = re.search(r, source).group(1)
            except AttributeError:
                val = "N/A"

            try:
                if "B" == val[-1]:
                    val = float(val[:-1]) * (10 ** 9)
                elif "M" == val[-1]:
                    val = float(val[:-1]) * (10 ** 6)

            except ValueError:
                val = "N/A"

            feature_vector[feature] = val

        return feature_vector
