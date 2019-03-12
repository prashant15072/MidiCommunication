import csv
import ConfigurationSetup

#configuration Setup
cfgFile="config.cfg"
config=ConfigurationSetup.parse_cfg(cfgFile)

#Parameters
preProcessedData={"min":[],"max":[]}

#Reading CSV File
with open(config["csvFileName"]) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=config["csvDelimiter"])
    line_count = 0
    for row in csv_reader:

        if (line_count==1):
            preProcessedData["min"]=list(row)
            preProcessedData["max"]=list(row)

        elif(line_count>1):
            for i in range(0,len(row)):
                if (float(row[i])>float(preProcessedData["max"][i])):
                    preProcessedData["max"][i]=float(row[i])
                elif (float(row[i])<float(preProcessedData["min"][i])):
                    preProcessedData["min"][i]=float(row[i])

        line_count+=1


print preProcessedData
#write object
ConfigurationSetup.picklestoreData(config["preProcessedDataFN"],preProcessedData)
