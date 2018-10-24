import ExtractFeatures
import ReadCSVToList
import numpy as np

SAVE_FLAG = False #Change to true to save the model.
SAVED_MODEL_NAME = "SVM"
SAVED_SCALER_NAME = "SVM_Scaler"

CHICKEN_FILE = "Training/CHICKENSegmented.csv"
CHICKEN_LABEL = "CHICKE"
CHICKEN_DATA = (CHICKEN_FILE, CHICKEN_LABEL)

IDLE_FILE = "Training/IDLE_ACTIONSegmented.csv"
IDLE_LABEL = "IDLE_A"
IDLE_DATA = (IDLE_FILE, IDLE_LABEL)

NUMBER7_FILE = "Training/NUMBER7Segmented.csv"
NUMBER7_LABEL = "NUMBER"
NUMBER7_DATA = (NUMBER7_FILE, NUMBER7_LABEL)

SIDESTEP_FILE = "Training/SIDESTEPSegmented.csv"
SIDESTEP_LABEL = "SIDEST"
SIDESTEP_DATA = (SIDESTEP_FILE, SIDESTEP_LABEL)

TURNCLAP_FILE = "Training/TURNCLAPSegmented.csv"
TURNCLAP_LABEL = "TURNCL"
TURNCLAP_DATA = (TURNCLAP_FILE, TURNCLAP_LABEL)

WIPERS_FILE = "Training/WIPERSSegmented.csv"
WIPERS_LABEL = "WIPERS"
WIPERS_DATA = (WIPERS_FILE, WIPERS_LABEL)

DATA_FILES = [CHICKEN_DATA, IDLE_DATA, NUMBER7_DATA, SIDESTEP_DATA, TURNCLAP_DATA, WIPERS_DATA]

TRAINING_LABELS = []
FINAL_TRAINING_DATA = []

def loadData():
    print("Labels used are:")
    for training_file in DATA_FILES:
        filename = training_file[0]
        label = training_file[1]
        counter = 0
        temp_data = ReadCSVToList.convertFileToList(filename)
        print(label)
        
        for row in temp_data:
            ExtractFeatures.extractFeatures(row)
            FINAL_TRAINING_DATA.append(row)
            TRAINING_LABELS.append(label)
    
    print("Done loading training data!\n")
    return

loadData()

X = np.array(FINAL_TRAINING_DATA)
y = np.array(TRAINING_LABELS)

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
TRANSFORMED_X = scaler.fit_transform(X)

#For saving the model and scaler.
from sklearn.externals import joblib
#Train the SVM
from sklearn.svm import SVC
clf = SVC()
clf.fit(TRANSFORMED_X, y)

#Save the scaler and model
if (SAVE_FLAG):
    joblib.dump(scaler, SAVED_SCALER_NAME)
    joblib.dump(clf, SAVED_MODEL_NAME)
    print("Scaler and Model saved!")


#Uncomment bottom part to do CV testing.
#IMPORTANT: DO NOT FIT ANY DATA TO MODEL BEFORE CV TESTING.
'''
from sklearn.pipeline import make_pipeline
SVM_CV = make_pipeline(StandardScaler(), SVC())

from sklearn.model_selection import ShuffleSplit
rs = ShuffleSplit(n_splits=30, random_state=0, test_size=0.20)

from sklearn.model_selection import cross_val_score
scores = cross_val_score(SVM_CV, X, y, cv=rs)
print("Accuracy: %0.5f (+/- %0.5f)" % (scores.mean(), scores.std() * 2))
'''
