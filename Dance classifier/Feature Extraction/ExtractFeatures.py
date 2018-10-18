from scipy.stats import kurtosis
import numpy as np


#INPUT: 1-D array of data IN THE SAME AXIS
#OUTPUT: Kurtosis value for the given data

def extractKurtosis(data):
    return kurtosis(data)


#INPUT: 1-D array of data IN THE SAME AXIS
#OUTPUT: Energy of the given data
def extractEnergy(data):
    componentSum = 0
    size = len(data)
    transformedData = np.fft.fft(data)
    
    for value in transformedData:
        magnitude = np.absolute(value)
        componentSum += (magnitude**2)

    energy = componentSum / size
    
    return energy
