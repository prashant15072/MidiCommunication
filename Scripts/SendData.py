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
from kivy.properties import StringProperty,ObjectProperty
import mido
import math
import csv
import time
import ConfigurationSetup
import io
from kivy.core.image import Image as CoreImage



Config.set('kivy', 'keyboard_mode', 'systemandmulti')

def normalize(min,max,val,rowNo):
    if (min[rowNo]>=0 and max[rowNo]<=127):
        return val

    ans= (float(val)-min[rowNo])/(max[rowNo]-min[rowNo])

    return math.ceil(ans*127)


def sendCC(ccList,data,sleepTime,min,max,isInterpolation,factor):

    i=0
    for options in ccList:
        control = options[0]
        value = int(64 if options[1] == "F" else data[int(options[1]) - 1])
        messageObject = mido.Message('control_change', control=int(control), value=int(normalize(min,max,value,int(options[1]) - 1)))
        port.send(messageObject)
        # time.sleep(sleepTime)  #Have to change this
        changedSleepTime=float(sleepTime)/factor

        if (isInterpolation==True):

            #Liner Interpolation
            a=value
            if (previousValue[0]>=0):
                d = float(previousValue[i] - value) / factor
                for j in range(0,factor):
                    a=a+d
                    temp=messageObject.copy(control=int(control), value=int(normalize(min,max,a,int(options[1]) - 1)))
                    port.send(temp)
                    # Make it sleep here
                    time.sleep(changedSleepTime)
        previousValue[i]=value
        i+=1



def sendNoteOn(options,data,sleepTime,min,max,isInterpolation,factor):

    messageObject = mido.Message('note_on')
    note = int(0 if options[0] == "F" else data[int(options[0]) - 1])
    velocity = int(64 if options[1] == "F" else data[int(options[1]) - 1])
    note=int(normalize(min,max,note,int(options[0]) - 1))
    velocity=int(normalize(min,max,velocity,int(options[1]) - 1))
    messageObject = messageObject.copy(note=note, velocity=velocity)
    port.send(messageObject)
    changedSleepTime = float(sleepTime) / factor

    if (isInterpolation == True):

        # Liner Interpolation
        anote = note
        avelocity=velocity

        if (previousValue[0] >= 0):
            dnote = (float(previousValue[0] - note)) / factor
            dvelocity=(float(previousValue[1]-velocity))/factor
            for j in range(0, factor):
                anote = anote + dnote
                avelocity=avelocity+dvelocity
                temp = messageObject.copy(note=int(anote), velocity=int(avelocity))
                port.send(temp)
                # Make it sleep here
                time.sleep(changedSleepTime)
    previousValue[0] = note
    previousValue[1] = velocity


def sendNormally(csv_reader,options,type,min,max,isInterpolation,factor):
    line_count = -1

    for row in csv_reader:

        line_count += 1
        if line_count > 0:

            if (type == "cc"):
                sendCC(options,row,sleepTime,min,max,isInterpolation,factor)
            else:
                sendNoteOn(options,row,sleepTime,min,max,isInterpolation,factor)



def sendMean(csv_reader,options,noOfRows,type,min,max,isInterpolation,factor):
    line_count = 0
    if (noOfRows<=1):
        sendNormally(csv_reader,options,type,min,max,isInterpolation,factor)
        return

    for row in csv_reader:

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
                    sendCC(options,data,sleepTime,min,max,isInterpolation,factor)
                else:
                    sendNoteOn(options,data,sleepTime,min,max,isInterpolation,factor)

            elif (line_count%noOfRows==1):
                data=row

            else:
                for i in range(0,len(row)):
                    data[i]=int(data[i])+int(row[i])



#configuration Setup
cfgFile="config.cfg"
config=ConfigurationSetup.parse_cfg(cfgFile)

#Parameters
coloumnNames=[]
coloumnNamesString=""
data=[]
port =mido.open_output(config["outPort"])
options=""
sleepTime=1                            #In seconds
type="cc"
noOfRows=1
previousValue=[]
isInterpolation=False

#Inputs
type=raw_input("Enter the type of Midi Packets(cc/note_on)?")
sleepTime=int(raw_input("Enter the delay between each packets(in seconds)"))

#Reading CSV
with open(config["csvFileName"]) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=config["csvDelimiter"])

    for row in csv_reader:
        coloumnNames=row
        break

    for i in range(0,len(coloumnNames)):
        coloumnNamesString+= str(i+1)+")   "+coloumnNames[i] +"\n"

    print coloumnNamesString

#     if (type=="cc"):
#         cclist=[]
#
#         print "Enter the number of CC's you want to enter ?"
#         n=int(raw_input())
#         print "Give your input accordingly : control(cc value) value(column number)"
#
#
#         for i in range(0,n):
#             options = raw_input().split(" ")
#             options[0]=int(options[0])
#             options[1]=int(options[1])
#             cclist.append(options)
#
#         options=cclist
#
#         for a in range(0,len(cclist)):
#             previousValue.append(-1)
#
#     elif (type=="note_on"):
#         print "Give your input accordingly(enter column numbers) : note velocity"
#         options=raw_input().split(" ")
#
#         previousValue=[-1,-1]
#
#
#     #Run Everthing
#     print "Enter the no. of rows to do the operatios on(Mean):"
#     print "Enter 1 if you want to parse it normally"
#     noOfRows=int(input())
#
#     print "Do you want to do interpolation(Y/N) ?"
#     inter=raw_input()
#     if (inter=="Y"):
#         isInterpolation=True
#     else:
#         isInterpolation=False
#
#     print "Enter the number of packets to be send inbetween two values"
#     factor=int(input())
#
#     #define min and max
#     preProcessedData=ConfigurationSetup.pickleloadData(config["preProcessedDataFN"])
#
#     for i in range(0,len(preProcessedData["min"])):
#         preProcessedData["min"][i]=float(preProcessedData["min"][i])
#         preProcessedData["max"][i]=float(preProcessedData["max"][i])
#
#
#     sendMean(csv_reader,options,noOfRows,type,preProcessedData["min"],preProcessedData["max"],isInterpolation,factor)
#
#
#     print ("CSV File Parsed Successfully")
#
#


'''<MessageTypePage>

    messageType : MessageType

    GridLayout:
        cols:1
        size: root.width-root.width*0.1,root.height-root.height*0.1
        pos: root.width*.05 , root.height*.05


        GridLayout:
            cols:2

            Label:
                text: "Type of Midi Packets ( cc / note_on )"
                text_size: self.size
                halign: 'right'
                valign: 'middle'

            TextInput:
                id : MessageType
                multiline : False


        Button:
            text:"Next"
            on_press : root.pressed()
'''


'''
        Input Type     - Done

        Column Names

        If (CC) then 
        (number of inputs
        control and their values)

        if (note_on) then
        (Note and Velocity column numbers)

        Delay between packets
        No. of rows to do the operation on
        Interpolation(Yes/No)
        If yes then 
        (Number of packets between 2 values
        )
        '''




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

    def __init__(self):
        super(MainUI, self).__init__()

    def printAllColumns(self):
        self.printColumnNames.text = coloumnNamesString

    def delayBtwPackets(self,*args):
        self.labelDelayBtwPackets.text = str(int(args[1]))

    def averagingRows(self,*args):
        self.labelAveragingRows.text=str(int(args[1]))

    def interpolation(self,*args):
        self.labelInterpolation.text=str(int(args[1]))

    def InterpolationSwitch(self,instance,value):
        print value

    def noteOnFunction(self):
        self.noteOnButton.disabled=True
        self.ccButton.disabled=False
        self.labelTypeChange.text= "Enter the Column Number for Note and the Column Number for Value in the following format : \n3 2\nWhere 3 is for Note and 2 is for Value"
        pass

    def ccFunction(self):
        self.noteOnButton.disabled=False
        self.ccButton.disabled=True
        self.labelTypeChange.text = "Enter the Control Number and the Column Number in the following format : \n33 2\n76 9"
        pass

    def start(self):
        print self.inputs.text

class kivyApp(App):
    def build(self):
        return MainUI()

if __name__=="__main__":
    kivyApp().run()