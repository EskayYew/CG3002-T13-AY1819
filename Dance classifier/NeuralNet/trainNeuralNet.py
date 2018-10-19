import ReadCSVToList
import numpy as np

SAVED_MODEL_NAME = "NeuralNet"

SAVED_SCALER_NAME = "NeuralNet_Scaler"

CHICKEN_FILE = "CHICKENSegmented.csv"

IDLE_ACTION_FILE = "IDLE_ACTIONSegmented.csv"

NUMBER7_FILE = "NUMBER7Segmented.csv"

SIDESTEP_FILE = "SIDESTEPSegmented.csv"

TURNCLAP_FILE = "TURNCLAPSegmented.csv"

WIPERS_FILE = "WIPERSSegmented.csv"

DATA_FILES = [CHICKEN_FILE, IDLE_ACTION_FILE, NUMBER7_FILE, SIDESTEP_FILE, TURNCLAP_FILE, WIPERS_FILE]

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

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
TRANSFORMED_X = scaler.fit_transform(X)

#Save the scaler
from sklearn.externals import joblib
joblib.dump(scaler, SAVED_SCALER_NAME)

#Train the NeuralNet
from sklearn.neural_network import MLPClassifier
clf = MLPClassifier(solver='adam')
#clf.fit(TRANSFORMED_X, y)

#Save the model
#joblib.dump(clf, SAVED_MODEL_NAME)

#Uncomment bottom part to do CV testing.
#IMPORTANT: DO NOT FIT ANY DATA TO MODEL BEFORE CV TESTING.
'''
from sklearn.model_selection import ShuffleSplit
rs = ShuffleSplit(n_splits=10, random_state=0)

from sklearn.model_selection import cross_val_score
scores = cross_val_score(clf, TRANSFORMED_X, y, cv=10)
print("Accuracy: %0.5f (+/- %0.5f)" % (scores.mean(), scores.std() * 2))
'''
