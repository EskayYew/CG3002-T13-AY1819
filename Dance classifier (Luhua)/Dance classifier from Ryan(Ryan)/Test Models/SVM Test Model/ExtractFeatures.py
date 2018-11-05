from scipy.stats import kurtosis
import numpy as np

RELEVANT_COLUMNS = 19

#INPUT: 1-D array of a Window of raw data.
#OUTPUT: Window of raw data with features added at the end. MODIFIES INPUT WINDOW.
def extractFeatures(data):
    readings = extractSensorReadingsAsList(data)
    result = []
    for i in range(len(readings)):
        axis1 = readings[i]
        result.append(extractMin(axis1))
        result.append(extractMax(axis1))
        result.append(extractRMS(axis1))
        result.append(extractKurtosis(axis1))
        result.append(extractEnergy(axis1))
                        
    return result

#INPUT: 1-D array of data IN THE SAME AXIS
#OUTPUT: Min value for the given data

def extractRMS(data):
    squaredSum = 0
    for value in data:
        squaredSum += (value**2)

    mean = squaredSum / len(data)

    result = (mean**0.5)
    return result


#INPUT: 1-D array of data IN THE SAME AXIS
#OUTPUT: Min value for the given data

def extractMin(data):
    return min(data)

#INPUT: 1-D array of data IN THE SAME AXIS
#OUTPUT: Max value for the given data

def extractMax(data):
    return max(data)

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

def extractBoardACCX(data):
    result = data[0:len(data):RELEVANT_COLUMNS]
    return result

def extractBoardACCY(data):
    result = data[1:len(data):RELEVANT_COLUMNS]
    return result

def extractBoardACCZ(data):
    result = data[2:len(data):RELEVANT_COLUMNS]
    return result

def extractBoardGYROX(data):
    result = data[3:len(data):RELEVANT_COLUMNS]
    return result

def extractBoardGYROY(data):
    result = data[4:len(data):RELEVANT_COLUMNS]
    return result

def extractBoardGYROZ(data):
    result = data[5:len(data):RELEVANT_COLUMNS]
    return result

def extractLeftACCX(data):
    result = data[6:len(data):RELEVANT_COLUMNS]
    return result

def extractLeftACCY(data):
    result = data[7:len(data):RELEVANT_COLUMNS]
    return result

def extractLeftACCZ(data):
    result = data[8:len(data):RELEVANT_COLUMNS]
    return result

def extractLeftGYROX(data):
    result = data[9:len(data):RELEVANT_COLUMNS]
    return result

def extractLeftGYROY(data):
    result = data[10:len(data):RELEVANT_COLUMNS]
    return result

def extractLeftGYROZ(data):
    result = data[11:len(data):RELEVANT_COLUMNS]
    return result

def extractRightACCX(data):
    result = data[12:len(data):RELEVANT_COLUMNS]
    return result

def extractRightACCY(data):
    result = data[13:len(data):RELEVANT_COLUMNS]
    return result

def extractRightACCZ(data):
    result = data[14:len(data):RELEVANT_COLUMNS]
    return result

def extractRightGYROX(data):
    result = data[15:len(data):RELEVANT_COLUMNS]
    return result

def extractRightGYROY(data):
    result = data[16:len(data):RELEVANT_COLUMNS]
    return result

def extractRightGYROZ(data):
    result = data[17:len(data):RELEVANT_COLUMNS]
    return result

def extractFlex(data):
    result = data[18:len(data):RELEVANT_COLUMNS]
    return result

#INPUT: 1-D array of a Window of raw data.
#OUTPUT: List of raw data separated by axis.
def extractSensorReadingsAsList(data):
    result = []
    
    boardACCX = extractBoardACCX(data)
    result.append(boardACCX)
    boardACCY = extractBoardACCY(data)
    result.append(boardACCY)
    boardACCZ = extractBoardACCZ(data)
    result.append(boardACCZ)
    boardGYROX = extractBoardGYROX(data)
    result.append(boardGYROX)
    boardGYROY = extractBoardGYROY(data)
    result.append(boardGYROY)
    boardGYROZ = extractBoardGYROZ(data)
    result.append(boardGYROZ)

    leftACCX = extractLeftACCX(data)
    result.append(leftACCX)
    leftACCY = extractLeftACCY(data)
    result.append(leftACCY)
    leftACCZ = extractLeftACCZ(data)
    result.append(leftACCZ)
    leftGYROX = extractLeftGYROX(data)
    result.append(leftGYROX)
    leftGYROY = extractLeftGYROY(data)
    result.append(leftGYROY)
    leftGYROZ = extractLeftGYROZ(data)
    result.append(leftGYROZ)

    rightACCX = extractRightACCX(data)
    result.append(rightACCX)
    rightACCY = extractRightACCY(data)
    result.append(rightACCY)
    rightACCZ = extractRightACCZ(data)
    result.append(rightACCZ)
    rightGYROX = extractRightGYROX(data)
    result.append(rightGYROX)
    rightGYROY = extractRightGYROY(data)
    result.append(rightGYROY)
    rightGYROZ = extractRightGYROZ(data)
    result.append(rightGYROZ)

    flex = extractFlex(data)
    result.append(flex)
    
    return result
