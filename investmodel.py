"""
investmodel.py defines an InvestmentModel class to
implement the predictive model
"""

from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import scale
from sklearn.svm import SVC

import numpy as np
import pandas as pd
import pickle

class InvestmentModel():
    """Models an investment strategy using an SVC"""

    def __init__(self, data_source, features, invest_amount=10000, threshold=0, test_size=0.1):

        self.data_source = data_source
        self.data = self.build_data_frame()

        self.features = features
        self.invest_amount = invest_amount
        self.threshold = threshold
        self.test_size = test_size

        self.model = None

    def build_data_frame(self):
        """Builds a dataset for the given features.

        :param data_source: a csv to read data from
        :returns: a pandas DataFrame object
        """

        # read in the csv
        df = pd.DataFrame.from_csv(self.data_source)

        # randomly permute the indices for good train/test sets
        df = df.reindex(np.random.permutation(df.index))

        # zero out all NaN and N/A values
        df = df.replace("NaN",0).replace("N/A",0)

        return df

    def save_model(self, path):
        """Saves the model to a pickle.

        :param path: where to save the pickle
        """

        if not self.model:
            raise ValueError("Model must be trained before saving")

        pickle.dump(self.model, open(path, 'w'))

    def get_X_y(self):
        """Builds an X, y feature/target pair from the data.

        :returns: a tuple of (feature matrix, labels)
        """

        # X
        X = np.array(self.data[self.features])
        X = scale(X)

        # y
        stock_change = np.array(self.data["stock_p_change"])
        sp500_change = np.array(self.data["sp500_p_change"])

        is_above_threshold = stock_change-sp500_change > self.threshold
        y = is_above_threshold.astype('i')

        return (X, y)

    def train(self):
        """Builds the investment model"""

        # Build train sets
        X, y = self.get_X_y()
        X_train, _, y_train, _ = train_test_split(X, y, test_size=self.test_size, random_state=0)

        # fit the model
        model = SVC(kernel="linear")
        model.fit(X_train, y_train)

        self.model = model

    def analysis(self, num_invest, num_correct, strategy_return, market_return):
        """Performs analysis on the results of a model test.

        :param num_invest: the number of investments made
        :param num_correct: the number of correctly assessed values
        :param strategy_return: the return given investment via the strategy
        :param market_return: the return given investment in the market
        :returns: a dictionary of analysis results
        """

        # build a dictionary of results
        accuracy = float(num_correct) / (self.test_size * len(self.data))
        compared = ((strategy_return - market_return) / market_return) * 100.0
        do_nothing = num_invest * self.invest_amount

        avg_market = ((market_return - do_nothing) / do_nothing) * 100.0
        avg_strat = ((strategy_return - do_nothing) / do_nothing) * 100.0

        results = {'accuracy': accuracy,
                   'market_return': market_return,
                   'strategy_return': strategy_return,
                   'num_investments': num_invest,
                   'comp_market_percent': compared,
                   'average_strategy_return': avg_strat,
                   'average_market_return': avg_market}

        return results

    def test(self):
        """Tests the investment model"""

        if not self.model:
            raise ValueError("Model must be trained before calling test")

        # Build test sets
        X, y = self.get_X_y()
        _, X_test, _, y_test = train_test_split(X, y, test_size=self.test_size, random_state=0)

        # test model
        num_invest = 0
        num_correct = 0
        market_return = 0
        strategy_return = 0

        stock_change = np.array(self.data["stock_p_change"])
        sp500_change = np.array(self.data["sp500_p_change"])

        df_invest = pd.DataFrame(columns=["Market Return", "Strategy Return"])

        for i in xrange(0, len(X_test)):

            predicted = self.model.predict(X_test[i])[0]
            expected = y_test[i]

            if predicted == expected:
                num_correct += 1

            if predicted == 1:
                num_invest += 1

                stock_invest_gain = self.invest_amount * (stock_change[i]) / 100
                sp500_invest_gain = self.invest_amount * (sp500_change[i]) / 100

                strategy_return += self.invest_amount + stock_invest_gain
                market_return += self.invest_amount + sp500_invest_gain

                df_invest = df_invest.append({"Strategy Return": strategy_return,
                                              "Market Return": market_return},
                                              ignore_index=True)

        df_invest.to_csv('return.csv', index=False)

        return self.analysis(num_invest, num_correct, strategy_return, market_return)
