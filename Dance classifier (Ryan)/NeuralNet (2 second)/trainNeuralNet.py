import ExtractFeatures
import ReadCSVToList
import SegmentData
import numpy as np

SAVE_FLAG = False #Change to true to save the model.
SAVED_MODEL_NAME = "NeuralNet_2_Second"
SAVED_SCALER_NAME = "NeuralNet_2_Second_Scaler"

CHICKEN_FOLDER = "Training/Chicken/"
CHICKEN_LABEL = "CHICKEN"
CHICKEN_DATA = (CHICKEN_FOLDER, CHICKEN_LABEL)

COWBOY_FOLDER = "Training/Cowboy/"
COWBOY_LABEL = "COWBOY"
COWBOY_DATA = (COWBOY_FOLDER, COWBOY_LABEL)

IDLE_FOLDER = "Training/Idle/"
IDLE_LABEL = "IDLE_A"
IDLE_DATA = (IDLE_FOLDER, IDLE_LABEL)

MERMAID_FOLDER = "Training/Mermaid/"
MERMAID_LABEL = "MERMAID"
MERMAID_DATA = (MERMAID_FOLDER, MERMAID_LABEL)

NUMBER6_FOLDER = "Training/Number 6/"
NUMBER6_LABEL = "NUMBER6"
NUMBER6_DATA = (NUMBER6_FOLDER, NUMBER6_LABEL)

NUMBER7_FOLDER = "Training/Number 7/"
NUMBER7_LABEL = "NUMBER7"
NUMBER7_DATA = (NUMBER7_FOLDER, NUMBER7_LABEL)

SALUTE_FOLDER = "Training/Salute/"
SALUTE_LABEL = "SALUTE"
SALUTE_DATA = (SALUTE_FOLDER, SALUTE_LABEL)

SIDESTEP_FOLDER = "Training/Sidestep/"
SIDESTEP_LABEL = "SIDESTEP"
SIDESTEP_DATA = (SIDESTEP_FOLDER, SIDESTEP_LABEL)

SWING_FOLDER = "Training/Swing/"
SWING_LABEL = "SWING"
SWING_DATA = (SWING_FOLDER, SWING_LABEL)

TURNCLAP_FOLDER = "Training/Turnclap/"
TURNCLAP_LABEL = "TURNCLAP"
TURNCLAP_DATA = (TURNCLAP_FOLDER, TURNCLAP_LABEL)

WIPERS_FOLDER = "Training/Wipers/"
WIPERS_LABEL = "WIPERS"
WIPERS_DATA = (WIPERS_FOLDER, WIPERS_LABEL)

DATA_FILES = [CHICKEN_DATA, COWBOY_DATA, IDLE_DATA, MERMAID_DATA, NUMBER6_DATA, NUMBER7_DATA,
              SALUTE_DATA, SIDESTEP_DATA, SWING_DATA, TURNCLAP_DATA, WIPERS_DATA]

TRAINING_LABELS = []
FINAL_TRAINING_DATA = []

def loadData():
    print("Labels used are:")
    for training_data in DATA_FILES:
        folder = training_data[0]
        label = training_data[1]
        counter = 0
        temp_data = SegmentData.processFiles(folder)
        print(label)
        
        for row in temp_data:
            processedRow = ExtractFeatures.extractFeatures(row)
            FINAL_TRAINING_DATA.append(processedRow)
            TRAINING_LABELS.append(label)
    
    print("Done loading training data!\n")
    return

loadData()

X = np.array(FINAL_TRAINING_DATA)
y = np.array(TRAINING_LABELS)

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(-1, 1))
TRANSFORMED_X = scaler.fit_transform(X)

#For saving the model and scaler.
from sklearn.externals import joblib
#Train the NeuralNet
from sklearn.neural_network import MLPClassifier
clf = MLPClassifier(hidden_layer_sizes=(100,), solver='adam', activation='relu')
clf.fit(TRANSFORMED_X, y)

#Save the scaler and model
if (SAVE_FLAG):
    joblib.dump(scaler, SAVED_SCALER_NAME)
    joblib.dump(clf, SAVED_MODEL_NAME)
    print("Scaler and Model saved!")
