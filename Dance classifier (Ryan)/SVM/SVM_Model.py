import ExtractFeatures
import numpy as np

from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

SAVED_MODEL_NAME = "SVM"
SAVED_SCALER_NAME = "SVM_Scaler"

SAMPLING_RATE = 50 #Sampling frequency in Hz
WINDOW_DURATION = 3 #Duration of window in seconds
SAMPLES = SAMPLING_RATE * WINDOW_DURATION
FEATURES = 19
WINDOW_SIZE = SAMPLES * FEATURES

class DanceClassifierSVM:
    def __init__(self):
        self.clf = joblib.load(SAVED_MODEL_NAME)
        self.scaler = joblib.load(SAVED_SCALER_NAME)

    def detectMove(self, window):
        if (len(window) != WINDOW_SIZE):
            print("ERROR: Window size does not match!")
            print("Expected window size is " + str(WINDOW_SIZE) + ". Input size: " + str(len(window)))
            return None
        
        processedData = ExtractFeatures.extractFeatures(window)
        
        scaledData = self.scaler.transform([dataToProcess])

        prediction = self.clf.predict(scaledData)
        return prediction
