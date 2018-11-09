import csv
import numpy as np


def convertFileToList(filename):
    groupList = []

    file = open(filename)
    file_data = csv.reader(file, delimiter=",", quotechar='"')
    for temp_data in file_data:
        convertedLines = convertLinesToFloats(temp_data)
        groupList.append(convertedLines)
    return groupList

def convertLinesToFloats(line):
    result = []
    for number in line:
        result.append(float(number))
    return result
