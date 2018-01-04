#!/usr/bin/env python

from sklearn import svm
from sklearn.linear_model import LinearRegression, Ridge, Lasso, BayesianRidge


class MachineLearning():

    def __init__(self):
        self.bays_md = BayesianRidge()
        self.lr_md = LinearRegression()
        # self.svm_md = svm.SVR(kernel='rbf')
        self.rdg_md = Ridge(alpha=.5)
        self.lass_md = Lasso(alpha=.1)

    def execute(self, _data):
        x, y, last_price, pred = _data
        if len(x) > 0 and len(y) > 0:
            self.bays_md.fit(x, y)
            self.lr_md.fit(x, y)
            # self.svm_md.fit(x, y)
            self.rdg_md.fit(x, y)
            self.lass_md.fit(x, y)
            return self.__predict(pred)
        return .0, .0, .0, .0, .0

    def __predict(self, pred):
        return (
            [.0],  # self.bays_md.predict([pred]),
            [.0],  # self.lr_md.predict([pred]),
            # self.svm_md.predict([pred]),
            [.0],  # self.rdg_md.predict([pred]),
            [.0],  # self.lass_md.predict([pred])
        )
