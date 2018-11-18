import numpy as np
from scipy.stats import kurtosis
from scipy.stats import kurtosis as kt


def extract_features(window):

    result_row = []

    for i in range(0, window[0].size-5):

        average = np.average(window[0:, i])
        variance = np.var(window[0:, i])
        max = np.max(window[0:, i])
        min = np.min(window[0:, i])
        kts = kurtosis(window[0:, i])
        result_row.append(average)
        result_row.append(variance)
        result_row.append(max)
        result_row.append(min)
        result_row.append(kts)

    return result_row

