import ReadCSVToList
import SegmentData

import numpy as np

CHICKEN_FOLDER = "Test/Chicken/"
CHICKEN_LABEL = "CHICKEN"
CHICKEN_DATA = (CHICKEN_FOLDER, CHICKEN_LABEL)

COWBOY_FOLDER = "Test/Cowboy/"
COWBOY_LABEL = "COWBOY"
COWBOY_DATA = (COWBOY_FOLDER, COWBOY_LABEL)

IDLE_FOLDER = "Test/Idle/"
IDLE_LABEL = "IDLE_A"
IDLE_DATA = (IDLE_FOLDER, IDLE_LABEL)

MERMAID_FOLDER = "Test/Mermaid/"
MERMAID_LABEL = "MERMAID"
MERMAID_DATA = (MERMAID_FOLDER, MERMAID_LABEL)

NUMBER6_FOLDER = "Test/Number 6/"
NUMBER6_LABEL = "NUMBER6"
NUMBER6_DATA = (NUMBER6_FOLDER, NUMBER6_LABEL)

NUMBER7_FOLDER = "Test/Number 7/"
NUMBER7_LABEL = "NUMBER7"
NUMBER7_DATA = (NUMBER7_FOLDER, NUMBER7_LABEL)

SALUTE_FOLDER = "Test/Salute/"
SALUTE_LABEL = "SALUTE"
SALUTE_DATA = (SALUTE_FOLDER, SALUTE_LABEL)

SIDESTEP_FOLDER = "Test/Sidestep/"
SIDESTEP_LABEL = "SIDESTEP"
SIDESTEP_DATA = (SIDESTEP_FOLDER, SIDESTEP_LABEL)

SWING_FOLDER = "Test/Swing/"
SWING_LABEL = "SWING"
SWING_DATA = (SWING_FOLDER, SWING_LABEL)

TURNCLAP_FOLDER = "Test/Turnclap/"
TURNCLAP_LABEL = "TURNCLAP"
TURNCLAP_DATA = (TURNCLAP_FOLDER, TURNCLAP_LABEL)

WIPERS_FOLDER = "Test/Wipers/"
WIPERS_LABEL = "WIPERS"
WIPERS_DATA = (WIPERS_FOLDER, WIPERS_LABEL)

DATA_FILES = [CHICKEN_DATA, COWBOY_DATA, IDLE_DATA, MERMAID_DATA, NUMBER6_DATA, NUMBER7_DATA,
              SALUTE_DATA, SIDESTEP_DATA, SWING_DATA, TURNCLAP_DATA, WIPERS_DATA]

TEST_DATA = []
TEST_DATA_LABELS = []

def loadTestData():
    print("Labels used are:")
    for training_data in DATA_FILES:
        folder = training_data[0]
        label = training_data[1]
        counter = 0
        temp_data = SegmentData.processFiles(folder)
        print(label)
        
        for row in temp_data:
            TEST_DATA.append(row)
            TEST_DATA_LABELS.append(label)
    
    print("Done loading training data!\n")
    return

loadTestData()

from sklearn.externals import joblib
import NeuralNet_Model_TESTING_ONLY

clf = NeuralNet_Model_TESTING_ONLY.DanceClassifierNN_TEST_MODE()

PREDICTED_DATA = []

#Calculate accuracy
TEST_DATA_SIZE = len(TEST_DATA)
correct = 0

for i in range(TEST_DATA_SIZE):
    prediction = clf.TEST_MODE_DETECT_MOVE(TEST_DATA[i])
    PREDICTED_DATA.append(prediction[0])
    if (prediction == TEST_DATA_LABELS[i]):
        correct +=1
    else:
        print(TEST_DATA_LABELS[i], "detected as", prediction)
        clf.TEST_MODE_GET_CONFIDENCE(TEST_DATA[i])

print()
#print("Accuracy: " + str(correct/TEST_DATA_SIZE))

from sklearn.metrics import confusion_matrix
CONFUSION_MATRIX_LABELS = [CHICKEN_LABEL, COWBOY_LABEL, MERMAID_LABEL, NUMBER6_LABEL, NUMBER7_LABEL,
              SALUTE_LABEL, SIDESTEP_LABEL, SWING_LABEL, TURNCLAP_LABEL, WIPERS_LABEL]
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
