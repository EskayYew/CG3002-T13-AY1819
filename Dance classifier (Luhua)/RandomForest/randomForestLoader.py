from sklearn.externals import joblib
import numpy as np
from scipy.stats import kurtosis


rdf_module = joblib.load("randomforest")


def random_forest_loader(data):
    data_1 = extract_features(data[0:48])
    data_2 = extract_features(data[48:96])
    data_3 = extract_features(data[96:144])
    result_1 = rdf_module.predict(data_1)
    result_2 = rdf_module.predict(data_2)
    result_3 = rdf_module.predict(data_3)

    if result_1 == result_2:
        return result_1

    elif result_1 == result_3:
        return result_2

    elif result_2 == result_3:
        return result_3

    else:
        return 'Cannot determine'


def extract_features(window):

    result_row = []

    for i in range(0, window[0].size-5):

        average = np.average(window[0:, i])
        variance = np.var(window[0:, i])
        max = np.max(window[0:, i])
        min = np.min(window[0:, i])
        kts = kurtosis(window[0:, i])
        # psd = welch(window[1:, i])
        result_row.append(average)
        result_row.append(variance)
        result_row.append(max)
        result_row.append(min)
        result_row.append(kts)
        # result_row.append(psd)

    return result_row