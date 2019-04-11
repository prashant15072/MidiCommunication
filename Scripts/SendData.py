import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import  FloatLayout
from kivy.config import Config
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from functools import wraps
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from PreProcessing import preProcess
from kivy.properties import StringProperty,ObjectProperty
import mido
import math
import csv
import time
import ConfigurationSetup
import io
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from functools import partial


Config.set('kivy', 'keyboard_mode', 'systemandmulti')
schedule_once = Clock.schedule_once
__all__ = ('yieldsleep', )

#configuration Setup
cfgFile="config.cfg"
config=ConfigurationSetup.parse_cfg(cfgFile)

#Parameters
coloumnNames=[]
coloumnNamesString=""
data=[]
port = ""
options=""
sleepTime=1                            #In seconds
type="cc"
noOfRows=1
previousValue=[]
pValue=[[-1,-1]]
isInterpolation=False
factor=1
isStop=False

def normalize(min,max,val,rowNo):
    if (min[rowNo]>=0 and max[rowNo]<=127):
        return val
    ans= (float(val)-min[rowNo])/(max[rowNo]-min[rowNo])

    return math.ceil(ans*127)

def yieldsleep(create_gen):
    @wraps(create_gen)
    def func(*args, **kwargs):
        gen = create_gen(*args, **kwargs)

        def sleep(seconds):
            schedule_once(resume_gen, seconds)

        def resume_gen(dt):
            try:
                sleep(gen.send(dt))
            except StopIteration:
                pass

        try:
            sleep(next(gen))
        except StopIteration:
            pass
        return gen
    return func


def sendCC(ccList,data,min,max):

    i=0
    messageObject = mido.Message('control_change')
    for options in ccList:
        control = options[0]
        value = int(64 if options[1] == "F" else data[int(options[1]) - 1])
        temp =messageObject.copy(control=int(control), value=int(normalize(min,max,value,int(options[1]) - 1)))
        port.send(temp)


def sendNoteOn(options,data,min,max):

    messageObject = mido.Message('note_on')
    note = int(0 if options[0] == "F" else data[int(options[0]) - 1])
    velocity = int(64 if options[1] == "F" else data[int(options[1]) - 1])
    note=int(normalize(min,max,note,int(options[0]) - 1))
    velocity=int(normalize(min,max,velocity,int(options[1]) - 1))

    messageObject = messageObject.copy(note=note, velocity=velocity)
    port.send(messageObject)



@yieldsleep
def sendMean(options,min,max):
    global coloumnNames, coloumnNamesString, port, sleepTime, type, noOfRows, previousValue, pValue,isInterpolation,isStop

    line_count = 0
    data=[]
    try:
        # Reading CSV
        file = open(config["csvFileName"])

    except:
        # TODO
        # Make a pop Up of invalid file name
        pass


    with file as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=config["csvDelimiter"])

        for row in csv_reader:
            break

        for row in csv_reader:

            if (isStop==False):


                if (noOfRows <= 1):


                    if (type == "cc"):

                        ccList=options
                        data=row

                        if (isInterpolation==True):
                            tempD=[]
                            tempValue=list(ccList)
                            changedSleepTime = float(sleepTime) / factor
                            messageObject = mido.Message('control_change')

                            j=0

                            for op in ccList:
                                control = op[0]
                                value = int(64 if op[1] == "F" else data[int(op[1]) - 1])
                                tempValue[j]=[control,value]
                                if (pValue[0][0]>=0):
                                    d = float(value-pValue[j][1]) / factor
                                    tempD.append(d)
                                j+=1


                            if (pValue[0][0]>=0):
                                for z in range(1,factor):
                                    yield changedSleepTime
                                    for k in range(0,len(ccList)):
                                        newValue=pValue[k][1]+tempD[k]
                                        pValue[k][1]=newValue
                                        temp = messageObject.copy(control=int(pValue[k][0]),
                                                                  value=int(normalize(min, max, pValue[k][1], int(ccList[k][1]) - 1)))
                                        port.send(temp)

                            pValue=list(tempValue)
                        else:
                            yield sleepTime


                        sendCC(options, row, min, max)


                    else:
                        if (isInterpolation == True):
                            data=row
                            changedSleepTime = float(sleepTime) / factor
                            messageObject = mido.Message('note_on')
                            note = int(0 if options[0] == "F" else data[int(options[0]) - 1])
                            velocity = int(64 if options[1] == "F" else data[int(options[1]) - 1])
                            note = int(normalize(min, max, note, int(options[0]) - 1))
                            velocity = int(normalize(min, max, velocity, int(options[1]) - 1))

                            # Liner Interpolation
                            anote = previousValue[0]
                            avelocity = previousValue[1]

                            if (previousValue[0] >= 0):
                                dnote = (float(note-previousValue[0])) / factor
                                dvelocity = (float(velocity-previousValue[1])) / factor
                                for j in range(0, factor):
                                    anote = anote + dnote
                                    avelocity = avelocity + dvelocity
                                    temp = messageObject.copy(note=int(anote), velocity=int(avelocity))
                                    # Make it sleep here
                                    # Clock.schedule_once(my_callback, changedSleepTime)
                                    yield changedSleepTime
                                    port.send(temp)

                            previousValue[0] = note
                            previousValue[1] = velocity

                        else:
                            yield sleepTime

                        sendNoteOn(options, row, min, max)


                    continue

                line_count += 1
                #Make sure that the modulo is greater that 1
                if line_count > 0:

                    if (line_count%noOfRows==0):

                        for i in range(0,len(row)):
                            data[i]=int(data[i])+int(row[i])

                        #averaging
                        for i in range(0,len(data)):
                            data[i]=float(data[i])/noOfRows


                        if (type == "cc"):

                            ccList = options
                            data = row

                            if (isInterpolation == True):
                                tempD = []
                                tempValue = list(ccList)
                                changedSleepTime = float(sleepTime) / factor
                                messageObject = mido.Message('control_change')

                                j = 0

                                for op in ccList:
                                    control = op[0]
                                    value = int(64 if op[1] == "F" else data[int(op[1]) - 1])
                                    tempValue[j] = [control, value]
                                    if (pValue[0][0] >= 0):
                                        d = float(value - pValue[j][1]) / factor
                                        tempD.append(d)
                                    j += 1

                                if (pValue[0][0] >= 0):
                                    for z in range(1, factor):
                                        yield changedSleepTime
                                        for k in range(0, len(ccList)):
                                            newValue = pValue[k][1] + tempD[k]
                                            pValue[k][1] = newValue
                                            temp = messageObject.copy(control=int(pValue[k][0]),
                                                                      value=int(normalize(min, max, pValue[k][1],
                                                                                          int(ccList[k][1]) - 1)))
                                            port.send(temp)

                                pValue = list(tempValue)
                            else:
                                yield sleepTime

                            sendCC(options,data,min,max)
                        else:
                            if (isInterpolation == True):
                                data = row
                                changedSleepTime = float(sleepTime) / factor
                                messageObject = mido.Message('note_on')
                                note = int(0 if options[0] == "F" else data[int(options[0]) - 1])
                                velocity = int(64 if options[1] == "F" else data[int(options[1]) - 1])
                                note = int(normalize(min, max, note, int(options[0]) - 1))
                                velocity = int(normalize(min, max, velocity, int(options[1]) - 1))

                                # Liner Interpolation
                                anote = previousValue[0]
                                avelocity = previousValue[1]

                                if (previousValue[0] >= 0):
                                    dnote = (float(note - previousValue[0])) / factor
                                    dvelocity = (float(velocity - previousValue[1])) / factor
                                    for j in range(0, factor):
                                        anote = anote + dnote
                                        avelocity = avelocity + dvelocity
                                        temp = messageObject.copy(note=int(anote), velocity=int(avelocity))
                                        # Make it sleep here
                                        # Clock.schedule_once(my_callback, changedSleepTime)
                                        yield changedSleepTime
                                        port.send(temp)

                                previousValue[0] = note
                                previousValue[1] = velocity

                            else:
                                yield sleepTime

                            sendNoteOn(options,data,min,max)


                    elif (line_count%noOfRows==1):
                        data=row

                    else:
                        for i in range(0,len(row)):
                            data[i]=int(data[i])+int(row[i])

            else:
                break

def findPortName(string):
    midiports = mido.get_output_names()
    allPorts=[]

    for i in midiports:
        if (i.find("loop") != -1):
            allPorts.append(i)

    return min(allPorts,key=len)


# UI


class MainUI(Widget):

    printColumnNames=ObjectProperty(None)
    labelDelayBtwPackets=ObjectProperty(None)
    labelAveragingRows=ObjectProperty(None)
    labelInterpolation=ObjectProperty(None)
    inputs=ObjectProperty(None)
    labelTypeChange=ObjectProperty(None)
    ccButton=ObjectProperty(None)
    noteOnButton=ObjectProperty(None)
    portname=ObjectProperty(None)
    csv_filepath=ObjectProperty(None)

    def __init__(self):
        super(MainUI, self).__init__()

    def preprocessData(self):
        config["csvFileName"] = self.csv_filepath.text
        preProcess(config["csvFileName"],config)

    def printAllColumns(self):
        config["csvFileName"]=self.csv_filepath.text

        global coloumnNamesString

        try:
            # Reading CSV
            file=open(config["csvFileName"])
            with file as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=config["csvDelimiter"])

                for row in csv_reader:
                    coloumnNames = row
                    break

                for i in range(0, len(coloumnNames)):
                    coloumnNamesString += str(i + 1) + ")   " + coloumnNames[i] + "\n"
            file.close()

        except :
            #TODO
            # Make a pop Up of invalid file name
            pass

        self.printColumnNames.text = coloumnNamesString

    def delayBtwPackets(self,*args):
        global sleepTime
        sleepTime=int(args[1])
        self.labelDelayBtwPackets.text = str(int(args[1]))

    def averagingRows(self,*args):
        global noOfRows
        noOfRows=int(args[1])
        self.labelAveragingRows.text=str(int(args[1]))

    def interpolation(self,*args):
        global factor
        factor=int(args[1])
        self.labelInterpolation.text=str(int(args[1]))

    def InterpolationSwitch(self,instance,value):
        global isInterpolation
        isInterpolation=value

    def noteOnFunction(self):
        global type
        type="note_on"
        self.noteOnButton.disabled=True
        self.ccButton.disabled=False
        self.labelTypeChange.text= "Enter the Column Number for Note and the Column Number for Value in the following format : \n3 2\nWhere 3 is for Note and 2 is for Value"
        pass

    def ccFunction(self):
        global type
        type = "cc"
        self.noteOnButton.disabled=False
        self.ccButton.disabled=True
        self.labelTypeChange.text = "Enter the Control Number and the Column Number in the following format : \n33 2\n76 9"
        pass

    def start(self):

        global coloumnNames,coloumnNamesString,data,port,options,sleepTime,type,noOfRows,previousValue,isInterpolation,isStop

        config["outPort"]=findPortName(self.portname.text)
        isStop=False
        try:
            port=mido.open_output(config["outPort"])
        except IOError:
            #TODO Add error pop up for no port found
            print "Caught"
        except :
            pass


        if (type == "cc"):
            cclist = []
            lists=self.inputs.text
            print lists
            lists=lists.split("\n")

            for i in range(0, len(lists)):
                options = lists[i].split(" ")
                options[0] = int(options[0].strip())
                options[1] = int(options[1].strip())
                cclist.append(options)

            options = cclist

            for a in range(0, len(cclist)):
                previousValue.append(-1)

        elif (type == "note_on"):

            options = self.inputs.text.strip().split(" ")
            previousValue = [-1, -1]

        # Run Everthing


        # define min and max
        preProcessedData = ConfigurationSetup.pickleloadData(config["preProcessedDataFN"])

        for i in range(0, len(preProcessedData["min"])):
            preProcessedData["min"][i] = float(preProcessedData["min"][i])
            preProcessedData["max"][i] = float(preProcessedData["max"][i])


        sendMean(options, preProcessedData["min"], preProcessedData["max"])

        print ("CSV File Parsed Successfully")

    def stop(self):
        global isStop
        isStop=True


class kivyApp(App):
    def build(self):
        return MainUI()

if __name__=="__main__":
    kivyApp().run()