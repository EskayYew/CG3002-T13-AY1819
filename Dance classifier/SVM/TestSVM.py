import ReadCSVToList
import numpy as np

SAVED_MODEL_NAME = "SVM"

SAVED_SCALER_NAME = "SVM_Scaler"

CHICKEN_FILE = "CHICKENSegmentedTest.csv"

IDLE_ACTION_FILE = "IDLE_ACTIONSegmentedTest.csv"

NUMBER7_FILE = "NUMBER7SegmentedTest.csv"

SIDESTEP_FILE = "SIDESTEPSegmentedTest.csv"

TURNCLAP_FILE = "TURNCLAPSegmentedTest.csv"

WIPERS_FILE = "WIPERSSegmentedTest.csv"

if (False): #Toggle for unseen test data
    WALKING_TEST_FILE = "Walking/WalkingSegmentedUnseenTest.csv"

    SQUATTING_TEST_FILE = "Squatting/SquattingSegmentedUnseenTest.csv"

    WAVING_TEST_FILE = "Waving/WavingSegmentedUnseenTest.csv"

DATA_FILES = [CHICKEN_FILE, IDLE_ACTION_FILE, NUMBER7_FILE, SIDESTEP_FILE, TURNCLAP_FILE, WIPERS_FILE]

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

from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import SVM_Model

clf = SVM_Model.DanceClassifierSVM()


PREDICTED_DATA = []

#Calculate accuracy
TEST_DATA_SIZE = len(TEST_DATA)
correct = 0

for i in range(TEST_DATA_SIZE):
    prediction = clf.detectMove(TEST_DATA[i])
    PREDICTED_DATA.append(prediction[0])
    if (prediction == TEST_DATA_LABELS[i]):
        correct +=1
    else:
        print(TEST_DATA_LABELS[i], "detected as", prediction)

print()
#print("Accuracy: " + str(correct/TEST_DATA_SIZE))

from sklearn.metrics import confusion_matrix
CONFUSION_MATRIX_LABELS = ["CHICKE", "IDLE_A", "NUMBER", "SIDEST", "TURNCL", "WIPERS"]
#Format is confusion_matrix(y_true, y_pred, labels)
#Y - Axis is Actual Class, X-Axis is Predicted Class
print("Confusion Matrix")
matrix = confusion_matrix(TEST_DATA_LABELS, PREDICTED_DATA, CONFUSION_MATRIX_LABELS)
print(matrix, "\n")

from sklearn.metrics import classification_report
print(classification_report(TEST_DATA_LABELS, PREDICTED_DATA, target_names=CONFUSION_MATRIX_LABELS))

#Precision = TP / (TP + FP)
#Recall = TP / (TP + FN)
from sklearn.metrics import precision_score
print("Precision:", precision_score(TEST_DATA_LABELS, PREDICTED_DATA, average='weighted'))

from sklearn.metrics import accuracy_score
accuracy = accuracy_score(TEST_DATA_LABELS, PREDICTED_DATA)
print("Accuracy:", str(accuracy))
