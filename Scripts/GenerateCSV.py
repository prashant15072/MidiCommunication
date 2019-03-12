import csv
import random

fileName="largeFile.csv"
csvData = []

input =int(raw_input("Enter the number of columns you want"))
columnNames=[]

print ("Enter column names:")
for i in range(0,input):
    columnNames.append(raw_input())
csvData.append(columnNames)

noOfRows=int(raw_input("Enter the number of rows"))
for i in range(0,noOfRows+1):
    values=[]
    for j in range(0,input):
        values.append(random.randint(-1000,1000))
    csvData.append(values)


with open(fileName, 'w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(csvData)

csvFile.close()