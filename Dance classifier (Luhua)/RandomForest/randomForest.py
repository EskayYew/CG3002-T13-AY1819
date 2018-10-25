import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import export_graphviz
from sklearn import metrics
import graphviz
import itertools
import numpy as np
import glob
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
from sklearn import svm, datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

# Squatting : 1
# Walking : 2
# Waving : 3

pd.options.display.max_rows = 20

# rdf = RandomForestRegressor()
rdf = GaussianNB()

whole_data = [[1, 1, 1, 1]]
whole_test = [[1, 1, 1, 1]]

for filename in glob.iglob('rawAccelerometerData/Squatting/Train/**/*.csv', recursive=True):
    train_data = pd.read_csv(filename).values

    for row in train_data:
        whole_data = np.append(whole_data, [np.append(row, 1)], axis=0)

# print(whole_data)

for filename in glob.iglob('rawAccelerometerData/Walking/Train/**/*.csv', recursive=True):
    train_data = pd.read_csv(filename).values

    for row in train_data:
        whole_data = np.append(whole_data, [np.append(row, 2)], axis=0)

# print(whole_data)
for filename in glob.iglob('rawAccelerometerData/Waving/Train/**/*.csv', recursive=True):
    train_data = pd.read_csv(filename).values

    for row in train_data:
        whole_data = np.append(whole_data, [np.append(row, 3)], axis=0)


# Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test

for filename in glob.iglob('rawAccelerometerData/Squatting/UnseenTest/**/*.csv', recursive=True):
    test_data = pd.read_csv(filename).values

    for row in test_data:
        whole_test = np.append(whole_test, [np.append(row, 1)], axis=0)

# print(whole_data)

for filename in glob.iglob('rawAccelerometerData/Walking/UnseenTest/**/*.csv', recursive=True):
    test_data = pd.read_csv(filename).values

    for row in test_data:
        whole_test = np.append(whole_test, [np.append(row, 2)], axis=0)

# print(whole_data)
for filename in glob.iglob('rawAccelerometerData/Waving/UnseenTest/**/*.csv', recursive=True):
    test_data = pd.read_csv(filename).values

    for row in test_data:
        whole_test = np.append(whole_test, [np.append(row, 3)], axis=0)

X = whole_data[1:, 0:3]
y = whole_data[1:, 3]

# X_test = whole_test[1:, 0:3]
# y_test = whole_test[1:, 3]

X, X_test, y, y_test = train_test_split(X, y, test_size=0.2)

rdf.fit(X, y)

cross_val_score()

print(f"Accuracy of train data: {rdf.score(X, y)}")
print(f"Accuracy of train data: {rdf.score(X_test, y_test)}")













