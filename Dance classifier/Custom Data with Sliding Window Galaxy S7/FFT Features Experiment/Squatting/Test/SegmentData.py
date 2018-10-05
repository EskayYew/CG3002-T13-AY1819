import csv

import numpy as np

FILE = "AccelerometerLinear.csv"

def makeListFromCSV(filename):
    processedData = []
    groupList = []
    counter = 0
    file = open(filename)
    file_data = csv.reader(file, delimiter=",", quotechar='"')
    for temp_data in file_data:
        row = []
        for i in range(3): #Each row has only 3 items.
            data = float(temp_data[i])
            row.append(data)
        processedData.append(row)
    return processedData

def segmentData(dataList, itemsPerWindow, windowInterval): #dataList is a 2D list
    segmentedData = []
    size = len(dataList)

    for i in range(0, size, windowInterval):
        window = dataList[i: (i + itemsPerWindow)]
        windowSize = len(window)
        if (windowSize < 40): #Exit loop as not enough items for new window
            break

        addedFeatures = extractFeatures(window)
        segmentedData.append(addedFeatures)

    return segmentedData

def extractFeatures(window): #Derive FFT of X,Y,Z
    result = []
    X_values = []
    Y_values = []
    Z_values = []

    for item in window:
        X_values.append(item[0])
        Y_values.append(item[1])
        Z_values.append(item[2])

    X_FFT = np.fft.fft(X_values)
    Y_FFT = np.fft.fft(Y_values)
    Z_FFT = np.fft.fft(Z_values)

    result.extend(X_FFT)
    result.extend(Y_FFT)
    result.extend(Z_FFT)
    
    return result


def writeData(actionName, dataset):
    with open(actionName + 'Segmented.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

        for row in dataset:
            writer.writerow(row)

raw_data = makeListFromCSV(FILE)
segmentedData = segmentData(raw_data, 40, 10)
writeData("Squatting", segmentedData)
