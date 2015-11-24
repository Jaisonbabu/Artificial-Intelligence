"""main.py contains main"""

from investmodel import InvestmentModel
from scraper import YahooScraper
import json
import pickle

def main():

    # load features
    f_feat = open('features.pkl')
    features = pickle.load(f_feat)

    f_map = open('feature_source_map.pkl')
    feature_source_map = pickle.load(f_map)

    im = InvestmentModel(data_source="data.csv", features=features)
    im.train()
    results = im.test()

    # save the model to a pkl
    model_save_path = 'model.pkl'
    im.save_model(model_save_path)

    ys = YahooScraper(features, feature_source_map, model_save_path)
    print "AAPL: " + str(ys.check_invest("AAPL"))
    print "SPLS: " + str(ys.check_invest("SPLS"))
    print json.dumps(results, indent=4, sort_keys=True)
  
if __name__ == "__main__":
    main()
