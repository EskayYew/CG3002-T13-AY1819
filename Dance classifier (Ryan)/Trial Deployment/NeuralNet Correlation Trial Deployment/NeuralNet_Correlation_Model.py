from ExtractFeaturesCorrelation import extractFeatures
import numpy as np

from sklearn.externals import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MinMaxScaler

SAVED_MODEL_NAME = "NeuralNet_Correlation"
SAVED_SCALER_NAME = "NeuralNet_Correlation_Scaler"

IDLE_LABEL = "IDLE_A"
UNSURE_PREDICTION = "UNSURE"
MAX_PREDICTION_ATTEMPTS = 3

SAMPLING_RATE = 50 #Sampling frequency in Hz
WINDOW_DURATION = 2 #Duration of window in seconds
SAMPLES = SAMPLING_RATE * WINDOW_DURATION
FEATURES = 19
WINDOW_SIZE = SAMPLES * FEATURES

#Prediction is returned as a STRING

class DanceClassifierNN:
    def __init__(self):
        self.clf = joblib.load(SAVED_MODEL_NAME)
        self.scaler = joblib.load(SAVED_SCALER_NAME)
        self.bestPrediction = ''
        self.bestConfidence = 0
        self.predictionAttempts = 0

    def detectMove(self, window):
        if (len(window) != WINDOW_SIZE):
            print("ERROR: Window size does not match!")
            print("Expected window size is " + str(WINDOW_SIZE) + ". Input size: " + str(len(window)))
            return None
        
        processedData = extractFeatures(window)
        
        scaledData = self.scaler.transform([processedData])

        currentPrediction = (self.clf.predict(scaledData)[0])
        
        confidence_array = self.clf.predict_proba(scaledData)
        currentConfidence = max(confidence_array[0])
        
        if (currentConfidence < 0.95): #If confidence is below 95%
            self.predictionAttempts += 1

            if (currentConfidence > self.bestConfidence): #If it's the most confident so far
                self.bestConfidence = currentConfidence #Update best confidence and prediction
                self.bestPrediction = currentPrediction

            if (self.predictionAttempts >= MAX_PREDICTION_ATTEMPTS): #Prevent stalling too long
                self.bestConfidence = 0 #Reset best confidence and number of attempts
                self.predictionAttempts = 0
                print("GUESS:", self.bestPrediction) #Debug output to evaluate performance.
                return self.bestPrediction #Return the best prediction obtained so far

            else: #We stall until we hit max prediction attempts or get confidence >= 95%
                return UNSURE_PREDICTION
        else:
            print("CONFIDENT:", currentPrediction) #Debug output to evaluate performance.
            if (currentPrediction == IDLE_LABEL): #Confident IDLE move, but don't flush past predictions at IDLE will stall the RPi.
                return currentPrediction

            else: #Confident of current move, safe to flush past predictions.
                self.bestConfidence = 0 #Reset best confidence and number of attempts
                self.predictionAttempts = 0
                return currentPrediction #We return current prediction as it is more than 95% sure.
