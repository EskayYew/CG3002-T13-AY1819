import ReadCSVToList
import numpy as np

SAVED_MODEL_NAME = "SVM"

SAVED_SCALER_NAME = "SVM_Scaler"

CHICKEN_FILE = "Test/CHICKENSegmentedTest.csv"
CHICKEN_LABEL = "CHICKE"
CHICKEN_DATA = (CHICKEN_FILE, CHICKEN_LABEL)

IDLE_FILE = "Test/IDLE_ACTIONSegmentedTest.csv"
IDLE_LABEL = "IDLE_A"
IDLE_DATA = (IDLE_FILE, IDLE_LABEL)

NUMBER7_FILE = "Test/NUMBER7SegmentedTest.csv"
NUMBER7_LABEL = "NUMBER"
NUMBER7_DATA = (NUMBER7_FILE, NUMBER7_LABEL)

SIDESTEP_FILE = "Test/SIDESTEPSegmentedTest.csv"
SIDESTEP_LABEL = "SIDEST"
SIDESTEP_DATA = (SIDESTEP_FILE, SIDESTEP_LABEL)

TURNCLAP_FILE = "Test/TURNCLAPSegmentedTest.csv"
TURNCLAP_LABEL = "TURNCL"
TURNCLAP_DATA = (TURNCLAP_FILE, TURNCLAP_LABEL)

WIPERS_FILE = "Test/WIPERSSegmentedTest.csv"
WIPERS_LABEL = "WIPERS"
WIPERS_DATA = (WIPERS_FILE, WIPERS_LABEL)

if (False): #Toggle for unseen test data
    pass

DATA_FILES = [CHICKEN_DATA, IDLE_DATA, NUMBER7_DATA, SIDESTEP_DATA, TURNCLAP_DATA, WIPERS_DATA]

TEST_DATA = []
TEST_DATA_LABELS = []

def loadTestData():
    print("Labels used are:")
    for testing_file in DATA_FILES:
        filename = testing_file[0]
        label = testing_file[1]
        temp_data = ReadCSVToList.convertFileToList(filename)
        print(label)

        for row in temp_data:
            TEST_DATA.append(row)
            TEST_DATA_LABELS.append(label)
    print("Done loading data!\n")
    return
            
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