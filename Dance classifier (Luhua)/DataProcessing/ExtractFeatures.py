import numpy as np
from scipy.stats import kurtosis as kt


def extract_features(window):
    result = [[]]
    result_row = []

    for i in range(0, window.size):

        average = np.average(window[:, i])
        variance = np.var(window[:, i])
        max = np.max(window[:, i])
        min = np.min(window[:, i])
        kts = kt.kurtosis(window[:, i])

        result_row.append(average)
        result_row.append(variance)
        result_row.append(max)
        result_row.append(min)
        result_row.append(kts)

    return
