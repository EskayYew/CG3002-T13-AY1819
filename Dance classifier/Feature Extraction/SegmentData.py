import ExtractFeatures
import csv
import os

ACTION = ""
RELEVANT_COLUMNS = 19

def processFiles():
    PROCESSED_DATA = []
    listOfFiles = os.listdir("./")
    for file in listOfFiles:
        if (checkIfCSV(file)):
            convertedFile = makeListFromCSV(file, RELEVANT_COLUMNS)
            segmentedData = segmentData(convertedFile, 90, 30) #Window size is 3 secs, sliding window is 1 sec.

            for sample in segmentedData:
                ExtractFeatures.extractFeatures(sample)

            PROCESSED_DATA.extend(segmentedData)

    writeData(ACTION, PROCESSED_DATA)
    return


#INPUT: A CSV files with training data, number of relevant columns per row.
#OUTPUT: A list of the data
def makeListFromCSV(filename, columns):
    convertedData = []
    counter = 0
    file = open(filename)
    file_data = csv.reader(file, delimiter=",", quotechar='"')
    for temp_data in file_data:
        row = []
        for i in range(columns):
            data = float(temp_data[i])
            row.append(data)
        convertedData.append(row)
    return convertedData

def segmentData(dataList, itemsPerWindow, windowInterval): #dataList is a 2D list
    segmentedData = []
    size = len(dataList)

    for i in range(0, size, windowInterval):
        window = dataList[i: (i + itemsPerWindow)]
        windowSize = len(window)
        if (windowSize < itemsPerWindow): #Exit loop as not enough items for new window
            break
        
        row = []
        for sample in window:
            row.extend(sample)
        segmentedData.append(row)
    return segmentedData


def writeData(actionName, dataset):
    with open(actionName + 'Segmented.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

        for row in dataset:
            writer.writerow(row)

#INPUT: A string of a filename
#OUTPUT: True if the file is a csv file.
def checkIfCSV(file):
    nameLength = len(file)
    if (file[(nameLength-3):nameLength] != 'csv'):
        return False
    else:
        return True

processFiles()
