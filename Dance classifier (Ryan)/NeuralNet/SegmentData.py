import csv
import os

SAMPLING_RATE = 50 #Sampling frequency in Hz
WINDOW_DURATION = 3 #Duration of window in seconds
SLIDING_WINDOW = 1 #Duration of sliding window in seconds
RELEVANT_COLUMNS = 19 #Number of relevant columns in data

POINTS_PER_WINDOW = WINDOW_DURATION * SAMPLING_RATE
POINTS_PER_SLIDE = SLIDING_WINDOW * SAMPLING_RATE

#INPUT: A folder containing CSV files with training data.
#OUTPUT: A list of the consolidated data.
def processFiles(folderDirectory):
    PROCESSED_DATA = []
    listOfFiles = os.listdir(folderDirectory)
    
    for file in listOfFiles:
        filepath = folderDirectory + "/" + file
        if (checkIfCSV(filepath)):
            convertedFile = makeListFromCSV(filepath, RELEVANT_COLUMNS)
            segmentedData = segmentData(convertedFile, POINTS_PER_WINDOW, POINTS_PER_SLIDE)
            #Window size is 3 secs, sliding window is 1 sec.

            PROCESSED_DATA.extend(segmentedData)

    return PROCESSED_DATA


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

#INPUT: A string of a filename
#OUTPUT: True if the file is a csv file.
def checkIfCSV(file):
    nameLength = len(file)
    if (file[(nameLength-3):nameLength] != 'csv'):
        return False
    else:
        return True
