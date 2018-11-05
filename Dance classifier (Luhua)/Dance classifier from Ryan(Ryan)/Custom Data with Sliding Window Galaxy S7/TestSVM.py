import ReadCSVToList
import numpy as np

WALKING_TEST_FILE = "Walking/WalkingSegmentedTest.csv"

SQUATTING_TEST_FILE = "Squatting/SquattingSegmentedTest.csv"

WAVING_TEST_FILE = "Waving/WavingSegmentedTest.csv"

if (False): #Toggle for unseen test data
    WALKING_TEST_FILE = "Walking/WalkingSegmentedUnseenTest.csv"

    SQUATTING_TEST_FILE = "Squatting/SquattingSegmentedUnseenTest.csv"

    WAVING_TEST_FILE = "Waving/WavingSegmentedUnseenTest.csv"

DATA_FILES = [WALKING_TEST_FILE, WAVING_TEST_FILE, SQUATTING_TEST_FILE]

TEST_DATA = []
TEST_DATA_LABELS = []

def loadTestData():
    for files in DATA_FILES:
        counter = 0
        temp_data = ReadCSVToList.convertFileToList(files)
        label = files[:6] #Cut short filename

        for row in temp_data:
            TEST_DATA.append(row)
            TEST_DATA_LABELS.append(label)
            
loadTestData()

from sklearn.svm import SVC
from sklearn.externals import joblib
SAVED_MODEL_NAME = "SVM"
clf = joblib.load(SAVED_MODEL_NAME)

PREDICTED_DATA = []

#Calculate accuracy
TEST_DATA_SIZE = len(TEST_DATA)
correct = 0

for i in range(TEST_DATA_SIZE):
    prediction = clf.predict([TEST_DATA[i]])
    PREDICTED_DATA.append(prediction[0])
    if (prediction == TEST_DATA_LABELS[i]):
        correct +=1

from sklearn.metrics import confusion_matrix
CONFUSION_MATRIX_LABELS = ["Squatt", "Walkin", "Waving"]
#Format is confusion_matrix(y_true, y_pred, labels)
print("Confusion Matrix")
print(confusion_matrix(TEST_DATA_LABELS, PREDICTED_DATA, CONFUSION_MATRIX_LABELS), "\n")

from sklearn.metrics import classification_report
print(classification_report(TEST_DATA_LABELS, PREDICTED_DATA, target_names=CONFUSION_MATRIX_LABELS))

from sklearn.metrics import precision_score
print("Precision:", precision_score(TEST_DATA_LABELS, PREDICTED_DATA, average='weighted'))

from sklearn.metrics import accuracy_score
accuracy = accuracy_score(TEST_DATA_LABELS, PREDICTED_DATA)
print("Accuracy:", str(accuracy))
