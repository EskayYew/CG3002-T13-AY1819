import ExtractFeatures
import numpy as np

from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

SAVED_MODEL_NAME = "SVM"
SAVED_SCALER_NAME = "SVM_Scaler"

SAMPLES = 90
FEATURES = 19
WINDOW_SIZE = SAMPLES * FEATURES



class DanceClassifierSVM:
    def __init__(self):
        self.clf = joblib.load(SAVED_MODEL_NAME)
        self.scaler = joblib.load(SAVED_SCALER_NAME)

    def detectMove(self, window):
        if (len(window) != WINDOW_SIZE):
            print("ERROR: Window size does not match!")
            return None
        
        dataToProcess = window.copy()
        ExtractFeatures.extractFeatures(dataToProcess)
        
        scaledData = self.scaler.transform([dataToProcess])

        prediction = self.clf.predict(scaledData)
        return prediction
