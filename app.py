from flask import Flask, request, Response, jsonify
from scraper import YahooScraper
from json import dumps
from flask.ext.cors import CORS

import pickle

app = Flask(__name__)
cors = CORS(app)

def get_yahoo_scraper():

    # load features
    f_feat = open('features.pkl')
    features = pickle.load(f_feat)

    f_map = open('feature_source_map.pkl')
    feature_source_map = pickle.load(f_map)

    return YahooScraper(features, feature_source_map, "model.pkl")

ys = get_yahoo_scraper()

@app.route('/', methods=['POST'])
def check_ticker():
    ticker = request.form['ticker']
    return str(ys.check_invest(ticker))

@app.route('/tickers', methods=['GET'])
def get_tickers():
    tickers = pickle.load(open('symbols.pkl'))
    response = Response(dumps(tickers.tolist()), mimetype="application/json")
    return response

if __name__ == "__main__":
    app.run(debug=True)
