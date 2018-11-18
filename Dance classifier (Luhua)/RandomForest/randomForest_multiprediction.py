import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import glob
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from scipy.stats import kurtosis
from sklearn.preprocessing import minmax_scale

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
        # segmented_data.flatten();

    return segmented_data


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


rdf = RandomForestClassifier()

whole_data = []
whole_test = []

segment_size = 48
window_size = 16

# bigger segment, much higher accuracy
# bigger window, less accuracy: wrong, 30 is the smallest

# wipers : 1
# sidestep : 2
# chicken: 3
# number7: 4
# idle: 5
# turn clap: 6

for i in range(0, 91):
    whole_data = np.append(whole_data, 1)

whole_data = [whole_data]

for filename in glob.iglob('../../ClassifiedTrainingSet_5moves/Wipers/*.csv', recursive=True):
    train_data = minmax_scale(pd.read_csv(filename).values)
    segmentedData = segment_data(train_data, segment_size, window_size)
    for row in segmentedData:
        whole_data = np.append(whole_data, [np.append(row, 'Wipers')], axis=0)

# print(whole_data)

for filename in glob.iglob('../../ClassifiedTrainingSet_5moves/Sidestep/*.csv', recursive=True):
    train_data = minmax_scale(pd.read_csv(filename).values)
    segmentedData = segment_data(train_data, segment_size, window_size)

    for row in segmentedData:
        whole_data = np.append(whole_data, [np.append(row, 'Sidestep')], axis=0)

# print(whole_data)
for filename in glob.iglob('../../ClassifiedTrainingSet_5moves/Chicken/*.csv', recursive=True):
    train_data = minmax_scale(pd.read_csv(filename).values)
    segmentedData = segment_data(train_data, segment_size, window_size)

    for row in segmentedData:
        whole_data = np.append(whole_data, [np.append(row, 'Chicken')], axis=0)


for filename in glob.iglob('../../ClassifiedTrainingSet_5moves/Number7/*.csv', recursive=True):
    train_data = minmax_scale(pd.read_csv(filename).values)
    segmentedData = segment_data(train_data, segment_size, window_size)

    for row in segmentedData:
        whole_data = np.append(whole_data, [np.append(row, 'Number7')], axis=0)

for filename in glob.iglob('../../ClassifiedTrainingSet_5moves/Idle/*.csv', recursive=True):
    train_data = minmax_scale(pd.read_csv(filename).values)
    segmentedData = segment_data(train_data, segment_size, window_size)

    for row in segmentedData:
        whole_data = np.append(whole_data, [np.append(row, 'Idle')], axis=0)

for filename in glob.iglob('../../ClassifiedTrainingSet_5moves/Turnclap/*.csv', recursive=True):
    train_data = minmax_scale(pd.read_csv(filename).values)
    segmentedData = segment_data(train_data, segment_size, window_size)

    for row in segmentedData:
        whole_data = np.append(whole_data, [np.append(row, 'Turnclap')], axis=0)

# # Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test
#
# for filename in glob.iglob('ClassifiedTrainingSet_5moves/Squatting/UnseenTest/**/*.csv', recursive=True):
#     test_data = pd.read_csv(filename).values
#     segmentedData = segment_data(test_data, segment_size, window_size)
#
#     for row in segmentedData:
#         whole_test = np.append(whole_test, [np.append(row, 1)], axis=0)
#
# # print(whole_data)
#
# for filename in glob.iglob('ClassifiedTrainingSet_5moves/Walking/UnseenTest/**/*.csv', recursive=True):
#     test_data = pd.read_csv(filename).values
#     segmentedData = segment_data(test_data, segment_size, window_size)
#
#     for row in segmentedData:
#         whole_test = np.append(whole_test, [np.append(row, 2)], axis=0)
#
# # print(whole_data)
# for filename in glob.iglob('ClassifiedTrainingSet_5moves/Waving/UnseenTest/**/*.csv', recursive=True):
#     test_data = pd.read_csv(filename).values
#     segmentedData = segment_data(test_data, segment_size, window_size)
#
#     for row in segmentedData:
#         whole_test = np.append(whole_test, [np.append(row, 3)], axis=0)

X = whole_data[1:, 0:90]
y = whole_data[1:, 90]

X, X_test, y, y_test = train_test_split(X, y, test_size=0.2)

rdf.fit(X, y)
joblib.dump(rdf, "randomforest")
rdf_module = joblib.load("randomforest")
#
# for item in X_test:
#     rdf.predict([item])

y_pre = rdf.predict(X_test)

print(y_pre)
# y_pre_round = []
#
# for item in y_pre:
#     y_pre_round.append(round(item))

print(accuracy_score(y_test, y_pre))
print(confusion_matrix(y_test, y_pre))

print(f"Accuracy of train data: {rdf.score(X, y)}")
print(f"Accuracy of test data: {rdf.score(X_test, y_test)}")













