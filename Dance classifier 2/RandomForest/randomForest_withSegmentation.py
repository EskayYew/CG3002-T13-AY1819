import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import glob
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from scipy.stats import kurtosis as kt

# Squatting : 1
# Walking : 2
# Waving : 3
# Sampling rate: 50ms

# Note: 1. Dont use max, min it 0.9995651386120674 0.9993674698795181
# 2. # bigger segment, much higher accuracy. bigger window, less accuracy: wrong, 30 is the smallest
# 3. Unseen test is very unclear and different from train data, the accuracy is low, it does not mean the algorithm is bad
# 4. Use segmentation can help us get much higher train data accuracy, but lower unseen test data accuracy
# 5. Due to overfitting, the unseen data does not perform good on RF
# 6. Gaussian: normal distribution, like height, weight, size


def segment_data(array, segment_size, window_size):
    segmented_data = []
    size = len(array)

    for i in range(0, size, window_size):
        window = array[i: (i + segment_size)]
        actual_window_size = len(window)
        if actual_window_size < segment_size:
            break

        result = extract_features(window)
        segmented_data.append(result)

    return segmented_data


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


rdf = RandomForestRegressor()
# rdf = GaussianNB()

# 7
# whole_data = [[1, 1, 1, 1, 1, 1, 1]]
# whole_test = [[1, 1, 1, 1, 1, 1, 1]]

# whole_data = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
# whole_test = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

whole_data = []
whole_test = []

segment_size = 100
window_size = 20

# bigger segment, much higher accuracy
# bigger window, less accuracy: wrong, 30 is the smallest



# wipers : 1
# sidestep : 2
# chicken: 3
# number7: 4
# idle: 5
# turnclap: 6


for filename in glob.iglob('rawAccelerometerData/Wipers/*.csv', recursive=True):
    train_data = pd.read_csv(filename).values
    segmentedData = segment_data(train_data, segment_size, window_size)

    for row in segmentedData:
        whole_data = np.append(whole_data, [np.append(row, 1)], axis=0)

# print(whole_data)

for filename in glob.iglob('rawAccelerometerData/Sidestep/*.csv', recursive=True):
    train_data = pd.read_csv(filename).values
    segmentedData = segment_data(train_data, segment_size, window_size)

    for row in segmentedData:
        whole_data = np.append(whole_data, [np.append(row, 2)], axis=0)

# print(whole_data)
for filename in glob.iglob('rawAccelerometerData/Chicken/*.csv', recursive=True):
    train_data = pd.read_csv(filename).values
    segmentedData = segment_data(train_data, segment_size, window_size)

    for row in segmentedData:
        whole_data = np.append(whole_data, [np.append(row, 3)], axis=0)


for filename in glob.iglob('rawAccelerometerData/Number7/*.csv', recursive=True):
    train_data = pd.read_csv(filename).values
    segmentedData = segment_data(train_data, segment_size, window_size)

    for row in segmentedData:
        # print([np.append(row, 1)])
        whole_data = np.append(whole_data, [np.append(row, 4)], axis=0)

# print(whole_data)

for filename in glob.iglob('rawAccelerometerData/Idle/*.csv', recursive=True):
    train_data = pd.read_csv(filename).values
    segmentedData = segment_data(train_data, segment_size, window_size)

    for row in segmentedData:
        whole_data = np.append(whole_data, [np.append(row, 5)], axis=0)

# print(whole_data)
for filename in glob.iglob('rawAccelerometerData/Turnclap/*.csv', recursive=True):
    train_data = pd.read_csv(filename).values
    segmentedData = segment_data(train_data, segment_size, window_size)

    for row in segmentedData:
        whole_data = np.append(whole_data, [np.append(row, 6)], axis=0)



# # Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test
#
# for filename in glob.iglob('rawAccelerometerData/Squatting/UnseenTest/**/*.csv', recursive=True):
#     test_data = pd.read_csv(filename).values
#     segmentedData = segment_data(test_data, segment_size, window_size)
#
#     for row in segmentedData:
#         whole_test = np.append(whole_test, [np.append(row, 1)], axis=0)
#
# # print(whole_data)
#
# for filename in glob.iglob('rawAccelerometerData/Walking/UnseenTest/**/*.csv', recursive=True):
#     test_data = pd.read_csv(filename).values
#     segmentedData = segment_data(test_data, segment_size, window_size)
#
#     for row in segmentedData:
#         whole_test = np.append(whole_test, [np.append(row, 2)], axis=0)
#
# # print(whole_data)
# for filename in glob.iglob('rawAccelerometerData/Waving/UnseenTest/**/*.csv', recursive=True):
#     test_data = pd.read_csv(filename).values
#     segmentedData = segment_data(test_data, segment_size, window_size)
#
#     for row in segmentedData:
#         whole_test = np.append(whole_test, [np.append(row, 3)], axis=0)

# X = whole_data[1:, 0:6]
# y = whole_data[1:, 6]

X = whole_data[1:, 0:12]
y = whole_data[1:, 12]

# X_test = whole_test[1:, 0:6]
# y_test = whole_test[1:, 6]

# X_test = whole_test[1:, 0:12]
# y_test = whole_test[1:, 12]


X, X_test, y, y_test = train_test_split(X, y, test_size=0.2)

rdf.fit(X, y)
joblib.dump(rdf, "randomforest")
rdf_module = joblib.load("randomforest")

print(y_test)

y_pre = rdf_module.predict(X_test)
y_pre_round = []

for item in y_pre:
    y_pre_round.append(round(item))

print(y_pre)
print(accuracy_score(y_test, y_pre_round))
print(confusion_matrix(y_test, y_pre_round))

print(f"Accuracy of train data: {rdf_module.score(X, y)}")
print(f"Accuracy of test data: {rdf_module.score(X_test, y_test)}")













