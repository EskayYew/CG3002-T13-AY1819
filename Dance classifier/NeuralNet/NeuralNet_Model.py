import ExtractFeatures
import numpy as np

from sklearn.externals import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MinMaxScaler

SAVED_MODEL_NAME = "NeuralNet"
SAVED_SCALER_NAME = "NeuralNet_Scaler"

SAMPLING_RATE = 50 #Sampling frequency in Hz
WINDOW_DURATION = 3 #Duration of window in seconds
SAMPLES = SAMPLING_RATE * WINDOW_DURATION
FEATURES = 19
WINDOW_SIZE = SAMPLES * FEATURES

class DanceClassifierNN:
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
