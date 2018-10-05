import ReadCSVToList
import numpy as np

WALKING_FILE = "Walking/WalkingSegmented.csv"

SQUATTING_FILE = "Squatting/SquattingSegmented.csv"

WAVING_FILE = "Waving/WavingSegmented.csv"

DATA_FILES = [WALKING_FILE, SQUATTING_FILE, WAVING_FILE]

TRAINING_LABELS = []
FINAL_TRAINING_DATA = []

TEST_DATA = []
TEST_DATA_LABELS = []

def loadData():
    for files in DATA_FILES:
        counter = 0
        temp_data = ReadCSVToList.convertFileToList(files)
        label = files[:6] #Cut short filename
        
        for row in temp_data:
            FINAL_TRAINING_DATA.append(row)
            TRAINING_LABELS.append(label)

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
