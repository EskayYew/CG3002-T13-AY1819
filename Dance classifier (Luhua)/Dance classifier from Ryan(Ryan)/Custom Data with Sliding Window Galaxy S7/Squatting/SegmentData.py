import csv

FILE = "SquattingWindow.csv"

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

def extractFeatures(window): #Extract max, min and range from a list

    result = []
    
    max_x = -999
    min_x = 999
    max_y = -999
    min_y = 999
    max_z = -999
    min_z = 999

    for item in window:
        temp_list = []
        for i in range(3): #Each row has only 3 items.
            data = item[i]

            if (i==0): #Check for X value
                if (data > max_x):
                    max_x = data
                if (data < min_x):
                    min_x = data

            elif (i==1): #Check for Y value
                if (data > max_y):
                    max_y = data
                if (data < min_y):
                    min_y = data

            else:
                if (data > max_z):
                    max_z = data
                if (data < min_z):
                    min_z = data
                    
            result.append(data)

        range_x = max_x - min_x
        range_y = max_y - min_y
        range_z = max_z - min_z

    features = [max_x, min_x, range_x, max_y, min_y, range_y, max_z, min_z, range_z]
    result.extend(features)
    return result


def writeData(actionName, dataset):
    with open(actionName + 'Segmented.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

        for row in dataset:
            writer.writerow(row)

raw_data = makeListFromCSV(FILE)
segmentedData = segmentData(raw_data, 40, 10)
writeData("Squatting", segmentedData)
