import numpy as np

TRAINING_LABELS = []
FINAL_TRAINING_DATA = []

TEST_DATA = []
TEST_DATA_LABELS = []

def loadData():
    return

loadData()

#print(TRAINING_LABELS)
#print(TEST_DATA_LABELS)

X = np.array(FINAL_TRAINING_DATA)
y = np.array(TRAINING_LABELS)

from sklearn.neural_network import MLPClassifier
clf = MLPClassifier(solver='lbfgs')
clf.fit(X, y)

from sklearn.externals import joblib
SAVED_MODEL_NAME = "NeuralNet"
joblib.dump(clf, SAVED_MODEL_NAME)

from sklearn.model_selection import cross_val_score
scores = cross_val_score(clf, X, y, cv=10)
print("Accuracy: %0.5f (+/- %0.5f)" % (scores.mean(), scores.std() * 2))
