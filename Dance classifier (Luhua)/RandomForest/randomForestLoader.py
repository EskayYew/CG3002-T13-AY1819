from sklearn.externals import joblib
import numpy as np
from scipy.stats import kurtosis


class RandomForestModel:
    def __init__(self):
        self.model = joblib.load("randomforest")

    def predict(self, window):
        data = np.array(window)

        if len(data) != 150:
            print("ERROR: Window size does not match!")
            print("Expected window size is " + str(150) + ". Input size: " + str(len(data)))
            return None

        data_1 = self.extract_features(data[0:48])
        data_2 = self.extract_features(data[48:96])
        data_3 = self.extract_features(data[96:144])
        result_1 = self.model.predict(data_1)
        result_2 = self.model.predict(data_2)
        result_3 = self.model.predict(data_3)

        if result_1 == result_2:
            return result_1

        elif result_1 == result_3:
            return result_2

        elif result_2 == result_3:
            return result_3

        else:
            return ['Unsure']

    def extract_features(self, window):
        result_row = []

        for i in range(0, window[0].size-5):

            average = np.average(window[0:, i])
            variance = np.var(window[0:, i])
            _max = np.max(window[0:, i])
            _min = np.min(window[0:, i])
            kts = kurtosis(window[0:, i])
            result_row.append(average)
            result_row.append(variance)
            result_row.append(_max)
            result_row.append(_min)
            result_row.append(kts)

        return result_row
