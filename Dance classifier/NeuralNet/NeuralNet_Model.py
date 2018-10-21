import ExtractFeatures
import numpy as np

from sklearn.externals import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MinMaxScaler

SAVED_MODEL_NAME = "NeuralNet"
SAVED_SCALER_NAME = "NeuralNet_Scaler"

SAMPLES = 90
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
