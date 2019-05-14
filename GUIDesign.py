#!/usr/bin/env python


#IMPORT these things to make it work. You need to import each new module class you want to use (buttons, displays, etc)
from PyQt5.QtWidgets import QWidget, QApplication, QProgressBar, QPushButton, QStatusBar, QLCDNumber, QDesktopWidget, QLabel,QLineEdit
from PyQt5.QtCore import Qt, QRect, QCoreApplication, QPointF, QThread
import sys # need this to run the Qwidget application
import time #need this for counting (well not really but makes syntax cleaner)
import statistics

#Imports and setup for reading from weight scale
import WeightData as wd


#required for Temperature sensor (From TempInput.py)
import os   # import os module
import glob  # import glob module
from ds18b20 import DS18B20 

os.system('modprobe w1-gpio')                              # load one wire communication device kernel modules
os.system('modprobe w1-therm')                                                 
base_dir = '/sys/bus/w1/devices/'                          # point to the address
device_folder = glob.glob(base_dir + '28*')[0]             # find device with address starting from 28*
device_file = device_folder + '/w1_slave'                  # store the details


#required for Servo control (from ServoTest.py)
#To do: move to another script that is usually off by default
#only call servo movement script when needed, and kill after movement
#import RPi.GPIO as GPIO
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(18, GPIO.OUT)
#p = GPIO.PWM(18, 50)
#p.start(2.5)

#Emergency Shutoff Imports
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)  #set GPIO labeling to breakout board
GPIO.setup(6, GPIO.OUT)

#Defining globabl variables for moisture content calculations
initialMoistTop = 1
initialMoistMid = 1
initialMoistBot = 1
initialWeightTop = 0.01
initialWeightMid = 0.01
initialWeightBot = 0.01
weightTop = 0.01
weightMid = 0.01
weightBot = 0.01
zeroTop = 0.01
zeroMid = 0.01
zeroBot = 0.01
dryMatterTemp = 1
initialSampleWeightTemp = 1
targetPercentTemp = 8
dryMatter = 1
initialSampleWeight = 1
targetPercent = 8
started = False
listTop = []
listMid = []
listBot = []
EStopTemp = 140
EStopTempTemp = 140

#Emergency Shutoff method
def shutoff():
    #global started
    #started = False
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(6, GPIO.OUT)
    GPIO.output(6, GPIO.LOW)
    
def Eshutoff():
    global started
    started = False
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(6, GPIO.OUT)
    GPIO.output(6, GPIO.LOW)
    #print("triggered")
        
def startup():
    global started
    started = True
    #GPIO.output(6, GPIO.HIGH)


#Weight scale methods defined





#Create a new window by inheriting from the QWidget class. You get all the functions defined in the QWidget class
class ControlWindow(QWidget):
    
    #Initialize the class (actually creating a initUI method and calling that, or just put all that code in here)
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        #Primary screen - Control Window Screen (laptop) - Screen0 will always be primary screen (only screen on RPi)
        self.sizeScreen0 = QDesktopWidget().screenGeometry(0)   #use this function to get the screen geometry
        print('  Screen 0 size : ' + str(self.sizeScreen0.height()) + 'x' + str(self.sizeScreen0.width()))
        #Print out the screen size for debugging issues, will display in terminal

        self.setGeometry(0, 0, self.sizeScreen0.width(), self.sizeScreen0.height())  #set window screen dimensions
        self.setWindowTitle('Control Panel')  #name window screen (displayed at top of window)

        #Create a button - same format for any button you want to make
        self.Zero_button = QPushButton(self) #declare the button instance from the QPushbutton class
        # set the button position and size .setgeometry(Qrect(X position, Y position, button width, button height)) position is from upper left of button
        # The button position and dimensions are relative to the screen size. You can type in absolute numbers instead if you want and are sure of screensize
        self.Zero_button.setGeometry(QRect(self.sizeScreen0.width() * 0.015, self.sizeScreen0.height() * 0.02, self.sizeScreen0.width() * 0.165, self.sizeScreen0.height() * 0.12))
        self.Zero_button.setObjectName("Zero_button")  #name the button
        self.Zero_button.setStyleSheet("font: bold 14px; background-color: rgb(5,176,36);")

        self.Weight_button = QPushButton(self)
        self.Weight_button.setGeometry(QRect(self.sizeScreen0.width() * 0.2, self.sizeScreen0.height() * 0.02, self.sizeScreen0.width() * 0.165, self.sizeScreen0.height() * 0.12))
        self.Weight_button.setObjectName("Weight_button")
        self.Weight_button.setStyleSheet("font: bold 14px; background-color: rgb(5,176,36);")
            
        self.Estop_button = QPushButton(self)
        self.Estop_button.setGeometry(QRect(self.sizeScreen0.width() * 0.74, self.sizeScreen0.height() * 0.02, self.sizeScreen0.width() * 0.2, self.sizeScreen0.height() * 0.12))
        self.Estop_button.setObjectName("Estop_button")
        self.Estop_button.setStyleSheet("font: bold 14px; background-color: red;")
        
        self.Start_button = QPushButton(self)
        self.Start_button.setGeometry(QRect(self.sizeScreen0.width() * 0.825, self.sizeScreen0.height() * 0.61, self.sizeScreen0.width() * 0.15, self.sizeScreen0.height() * 0.15))
        self.Start_button.setObjectName("Start_button")
        self.Start_button.setStyleSheet("font: bold 14px; background-color: rgb(5,176,36);")
        
        #Create another button (same process as before)
        self.Close_button = QPushButton(self)
        self.Close_button.setGeometry(QRect(self.sizeScreen0.width() * 0.95, self.sizeScreen0.height() * 0.01, self.sizeScreen0.width() * 0.04, self.sizeScreen0.height() * 0.06))
        self.Close_button.setObjectName("X_button")
        self.Close_button.setStyleSheet("font: bold 18px; background-color: rgb(5,176,36);")

        #Creates GUI user inputs
        self.InitialSampleWeight = QLineEdit(self)
        self.InitialSampleWeight.setGeometry(QRect(self.sizeScreen0.width() * 0.2, self.sizeScreen0.height() * 0.8, self.sizeScreen0.width() * 0.09, self.sizeScreen0.height() * 0.1))
        self.InitialSampleWeight.setStyleSheet("font: bold 20px;")
        self.InitialSampleWeight.setMaxLength(5)
     
        self.DryMatterWeight = QLineEdit(self)
        self.DryMatterWeight.setGeometry(QRect(self.sizeScreen0.width() * 0.5, self.sizeScreen0.height() * 0.8, self.sizeScreen0.width() * 0.09, self.sizeScreen0.height() * 0.1))
        self.DryMatterWeight.setStyleSheet("font: bold 20px;")
        self.DryMatterWeight.setMaxLength(5)
        
        self.TargetWeightPercent = QLineEdit(self)
        self.TargetWeightPercent.setGeometry(QRect(self.sizeScreen0.width() * 0.8, self.sizeScreen0.height() * 0.8, self.sizeScreen0.width() * 0.09, self.sizeScreen0.height() * 0.1))
        self.TargetWeightPercent.setStyleSheet("font: bold 20px;")
        self.TargetWeightPercent.setMaxLength(5)
        
        self.EStopTemp = QLineEdit(self)
        self.EStopTemp.setGeometry(QRect(self.sizeScreen0.width() * 0.86, self.sizeScreen0.height() * 0.3, self.sizeScreen0.width() * 0.09, self.sizeScreen0.height() * 0.1))
        self.EStopTemp.setStyleSheet("font: bold 20px;")
        self.EStopTemp.setMaxLength(5)
        
        self.EStopTemp_label = QLabel(self)
        self.EStopTemp_label.setGeometry(QRect(self.sizeScreen0.width() * 0.815, self.sizeScreen0.height() * 0.20, self.sizeScreen0.width() * 0.3, self.sizeScreen0.height() * 0.1))
        self.EStopTemp_label.setStyleSheet("font: bold 15px;")
        
        self.SampleWeight_label = QLabel(self)
        self.SampleWeight_label.setGeometry(QRect(self.sizeScreen0.width() * 0.05, self.sizeScreen0.height() * 0.8, self.sizeScreen0.width() * 0.15, self.sizeScreen0.height() * 0.1))
        self.SampleWeight_label.setStyleSheet("font: bold 15px;")
        
        self.DryMatter_label = QLabel(self)
        self.DryMatter_label.setGeometry(QRect(self.sizeScreen0.width() * 0.37, self.sizeScreen0.height() * 0.8, self.sizeScreen0.width() * 0.13, self.sizeScreen0.height() * 0.1))
        self.DryMatter_label.setStyleSheet("font: bold 15px;")
        
        self.TargetPercent_label = QLabel(self)
        self.TargetPercent_label.setGeometry(QRect(self.sizeScreen0.width() * 0.63, self.sizeScreen0.height() * 0.8, self.sizeScreen0.width() * 0.165, self.sizeScreen0.height() * 0.1))
        self.TargetPercent_label.setStyleSheet("font: bold 15px;")       

        self.Top_label = QLabel(self)
        self.Top_label.setGeometry(QRect(self.sizeScreen0.width() * 0.1, self.sizeScreen0.height() * 0.125, self.sizeScreen0.width() * 0.3, self.sizeScreen0.height() * 0.3))
        self.Top_label.setStyleSheet("font: bold 20px;")

        self.Middle_label = QLabel(self)
        self.Middle_label.setGeometry(QRect(self.sizeScreen0.width() * 0.1, self.sizeScreen0.height() * 0.325, self.sizeScreen0.width() * 0.3, self.sizeScreen0.height() * 0.3))
        self.Middle_label.setStyleSheet("font: bold 20px;")

        self.Bottom_label = QLabel(self)
        self.Bottom_label.setGeometry(QRect(self.sizeScreen0.width() * 0.1, self.sizeScreen0.height() * 0.525, self.sizeScreen0.width() * 0.3, self.sizeScreen0.height() * 0.3))
        self.Bottom_label.setStyleSheet("font: bold 20px;")

#        self.Progress_label = QLabel(self)
#        self.Progress_label.setGeometry(QRect(self.sizeScreen0.width() * 0.1, self.sizeScreen0.height() * 0.65, self.sizeScreen0.width() * 0.3, self.sizeScreen0.height() * 0.3))
#        self.Progress_label.setStyleSheet("font: bold 15px;")

        self.Weight_label = QLabel(self)
        self.Weight_label.setGeometry(QRect(self.sizeScreen0.width() * 0.34, self.sizeScreen0.height() * 0.05, self.sizeScreen0.width() * 0.3, self.sizeScreen0.height() * 0.3))
        self.Weight_label.setStyleSheet("font: bold 15px;")

        self.Moisture_label = QLabel(self)
        self.Moisture_label.setGeometry(QRect(self.sizeScreen0.width() * 0.59, self.sizeScreen0.height() * 0.125, self.sizeScreen0.width() * 0.23, self.sizeScreen0.height() * 0.15))
        self.Moisture_label.setStyleSheet("font: bold 15px;")

        self.TopTemp_label = QLabel(self)
        self.TopTemp_label.setGeometry(QRect(self.sizeScreen0.width() * 0.41, self.sizeScreen0.height() * 0.03, self.sizeScreen0.width() * 0.22, self.sizeScreen0.height() * 0.05))
        self.TopTemp_label.setStyleSheet("font: bold 15px;")

        self.BottomTemp_label = QLabel(self)
        self.BottomTemp_label.setGeometry(QRect(self.sizeScreen0.width() * 0.41, self.sizeScreen0.height() * 0.105, self.sizeScreen0.width() * 0.25, self.sizeScreen0.height() * 0.05))
        self.BottomTemp_label.setStyleSheet("font: bold 15px;")

        #Create an LCD display widget to show numbers
        self.LCDdisplay = QLCDNumber(self)  #Create the instance from the QLCDNumber class
        #Set the position and dimensions just like was done for the buttons
        self.LCDdisplay.setGeometry(QRect(self.sizeScreen0.width() * 0.935, self.sizeScreen0.height() * 0.8, self.sizeScreen0.width() * 0.06, self.sizeScreen0.height() * 0.12))
        self.LCDdisplay.setObjectName("Counter")  #Name it
        self.LCDdisplay.setStyleSheet("background-color:white;")

        self.TopTempdisplay = QLCDNumber(self)
        self.TopTempdisplay.setGeometry(QRect(self.sizeScreen0.width() * 0.62, self.sizeScreen0.height() * 0.025, self.sizeScreen0.width() * 0.1, self.sizeScreen0.height() * 0.06))
        self.TopTempdisplay.setObjectName("Top Temperature")
        self.TopTempdisplay.setStyleSheet("background-color:white;")

        self.BottomTempdisplay = QLCDNumber(self)
        self.BottomTempdisplay.setGeometry(QRect(self.sizeScreen0.width() * 0.62, self.sizeScreen0.height() * 0.1, self.sizeScreen0.width() * 0.1, self.sizeScreen0.height() * 0.06))
        self.BottomTempdisplay.setObjectName("Bottom Temperature")
        self.BottomTempdisplay.setStyleSheet("background-color:white;")

        self.TopWeightdisplay = QLCDNumber(self)
        self.TopWeightdisplay.setGeometry(QRect(self.sizeScreen0.width() * 0.3, self.sizeScreen0.height() * 0.22, self.sizeScreen0.width() * 0.2, self.sizeScreen0.height() * 0.12))
        self.TopWeightdisplay.setObjectName("Top Weight")
        self.TopWeightdisplay.setStyleSheet("background-color:white;")

        self.TopMoisturedisplay = QLCDNumber(self)
        self.TopMoisturedisplay.setGeometry(QRect(self.sizeScreen0.width() * 0.6, self.sizeScreen0.height() * 0.22, self.sizeScreen0.width() * 0.2, self.sizeScreen0.height() * 0.12))
        self.TopMoisturedisplay.setObjectName("Top Moisture")
        self.TopMoisturedisplay.setStyleSheet("background-color:white;")

        self.MiddleWeightdisplay = QLCDNumber(self)
        self.MiddleWeightdisplay.setGeometry(QRect(self.sizeScreen0.width() * 0.3, self.sizeScreen0.height() * 0.42, self.sizeScreen0.width() * 0.2, self.sizeScreen0.height() * 0.12))
        self.MiddleWeightdisplay.setObjectName("Middle Weight")
        self.MiddleWeightdisplay.setStyleSheet("background-color:white;")

        self.MiddleMoisturedisplay = QLCDNumber(self)
        self.MiddleMoisturedisplay.setGeometry(QRect(self.sizeScreen0.width() * 0.6, self.sizeScreen0.height() * 0.42, self.sizeScreen0.width() * 0.2, self.sizeScreen0.height() * 0.12))
        self.MiddleMoisturedisplay.setObjectName("Middle Moisture")
        self.MiddleMoisturedisplay.setStyleSheet("background-color:white;")

        self.BottomWeightdisplay = QLCDNumber(self)
        self.BottomWeightdisplay.setGeometry(QRect(self.sizeScreen0.width() * 0.3, self.sizeScreen0.height() * 0.62, self.sizeScreen0.width() * 0.2, self.sizeScreen0.height() * 0.12))
        self.BottomWeightdisplay.setObjectName("Bottom Weight")
        self.BottomWeightdisplay.setStyleSheet("background-color:white;")

        self.BottomMoisturedisplay = QLCDNumber(self)
        self.BottomMoisturedisplay.setGeometry(QRect(self.sizeScreen0.width() * 0.6, self.sizeScreen0.height() * 0.62, self.sizeScreen0.width() * 0.2, self.sizeScreen0.height() * 0.12))
        self.BottomMoisturedisplay.setObjectName("Bottom Moisture")
        self.BottomMoisturedisplay.setStyleSheet("background-color:white;")

#        self.Progress_bar = QProgressBar(self)
#        self.Progress_bar.setGeometry(QRect(self.sizeScreen0.width() * 0.1, self.sizeScreen0.height() * 0.83, self.sizeScreen0.width() * 0.7, self.sizeScreen0.height() * 0.04))
#        self.Progress_bar.setRange(0,100)
#        #loop = 60
#        #self.Progress_bar.setValue(loop)
#        self.Progress_bar.setStyleSheet("font: bold 15px; text-align: center; border: 1px solid grey;")

        #Not exactly sure what this does, but it is needed to put a name label on the buttons
        _translate = QCoreApplication.translate

        #Name the Close Button label
        self.Close_button.setText(_translate("ControlWindow", "X"))
        #Name the calibrate button label
        self.Zero_button.setText(_translate("ControlWindow", "Zero All Scales"))

        self.Weight_button.setText(_translate("ControlWindow", "Set Initial"+ "\n" +"Weights"))

        self.Estop_button.setText(_translate("ControlWindow", "Emergency" + "\n" + "Shutoff"))
        
        self.Start_button.setText(_translate("ControlWindow", "Start/Resume"))
        
        self.Top_label.setText(_translate("ControlWindow", "Top Shelf:"))

        self.Middle_label.setText(_translate("ControlWindow", "Middle Shelf:"))

        self.Bottom_label.setText(_translate("ControlWindow", "Bottom Shelf:"))

        #self.Progress_label.setText(_translate("ControlWindow", "Drying Progress:"))

        self.Weight_label.setText(_translate("ControlWindow", "Weight (lbs):"))

        self.Moisture_label.setText(_translate("ControlWindow", "Moisture Percent (%):"))

        self.TopTemp_label.setText(_translate("ControlWindow", "Temperature 1 (F):"))

        self.BottomTemp_label.setText(_translate("ControlWindow", "Temperature 2 (F):"))
        
        self.SampleWeight_label.setText(_translate("ControlWindow", "Initial Sample"+ "\n" +"  Weight (g):"))
        
        self.DryMatter_label.setText(_translate("ControlWindow", "Dry Matter"+ "\n" +"Weight (g):"))
        
        self.TargetPercent_label.setText(_translate("ControlWindow", "Target Moisture"+ "\n" +"   Percent (%):"))
        
        self.EStopTemp_label.setText(_translate("ControlWindow", "         E-Stop"+ "\n" +"Temperature (F):"))

        #This sets the Close button's action when you click on it, in this case it will run the method "CloseUp" which is below
        self.Close_button.clicked.connect(self.CloseUp)
        #self.Close_button.clicked.connect(GPIOcleanup)
        
        #This activates E-stop when E-stop is pressed
        self.Estop_button.clicked.connect(Eshutoff)

        #This activates method "startup" when Start/Resume button is pressed
        self.Start_button.clicked.connect(startup)
        
        #Saves input values when start button pressed
        self.Start_button.clicked.connect(self.getInitialSampleWeight)
        self.Start_button.clicked.connect(self.getDryMatterWeight)
        self.Start_button.clicked.connect(self.getTargetWeightPercent)
        self.Start_button.clicked.connect(self.getEStopTemp)

        #This activates zeroing of the scales when "Zero" butotn is clicked
        self.Zero_button.clicked.connect(self.ZeroAllScales)
        
        #Records initial values when clicked
        self.Weight_button.clicked.connect(self.SetInitialWeights)

        #Show the screen, not sure it is really needed though
        self.show


    #Like before, not exactly sure what it is doing, but needed to create and show the button naming labels
    def retranslateUi(self, TestDisplay):
        _translate = QCoreApplication.translate
        TestDisplay.setWindowTitle(_translate("MainGroWin", "MainWindow"))
        self.Disconnect_button.setText(_translate("MainGroWin", "Disconnect"))

    #The function that will close the window and program when you click on the "Close" button
    def CloseUp(self):  #create method inside the ControlWindow Class (belongs to the ControlWindow class)
        # print('Closed')  #Used for debugging in terminal
        # Maximize the window, you can use the windowstate function to minimize, maximize and manipulate the window
        self.setWindowState(Qt.WindowMaximized)
        # Close up the window and shut it down
        self.close()
        GPIO.cleanup()
        Eshutoff()

    def ZeroAllScales(self): #setting offset of scales to current value so that scales are zeroed
        #REWRITE to create a list that updates every time button is pressed, so that offset is cumulative
        global zeroTop
        global zeroMid
        global zeroBot
        global listTop
        global listMid
        global listBot
        listTop.append(weightTop)
        listMid.append(weightMid)
        listBot.append(weightBot)
        zeroTop = sum(listTop)
        zeroMid = sum(listMid)
        zeroBot = sum(listBot)

    def SetInitialWeights(self): #saving current weights as "initial weights" when button is pressed
        global initialWeightTop

        global initialWeightMid
        global initialWeightBot
        initialWeightTop = weightTop
        initialWeightMid = weightMid
        initialWeightBot = weightBot

    #Function to update the LED value inside the counting display
    def updateLED(self, LEDnum):
        #update the LED value
        self.LEDvalue = LEDnum  #rename the variable for clarity
        self.LCDdisplay.display(self.LEDvalue) #use the display method of the LCDdisplay inhereited class to update the LED
            
#    def updateProgressBar (self, ProgressNum):
#        self.ProgressValue = ProgressNum
#        self.Progress_bar.setValue(self.ProgressValue)

    def updateTopTemp(self, TopTemp):  #method for updating temperature display
        self.TopTempValue = TopTemp
        self.TopTempdisplay.display(self.TopTempValue)
       
    def updateBotTemp(self, BotTemp):  #method for updating temperature display
        self.BotTempValue = BotTemp
        self.BottomTempdisplay.display(self.BotTempValue)

    def updateTopWeight(self, TopWeight):  #method for updating weight display
        self.TopWeightValue = TopWeight
        self.TopWeightdisplay.display(self.TopWeightValue)
                
    def updateMiddleWeight(self, MiddleWeight):  #method for updating weight display
        self.MiddleWeightValue = MiddleWeight
        self.MiddleWeightdisplay.display(self.MiddleWeightValue)
        
    def updateBottomWeight(self, BottomWeight):  #method for updating weight display
        self.BottomWeightValue = BottomWeight
        self.BottomWeightdisplay.display(self.BottomWeightValue)
        
    def updateTopMoistureDisplay(self, TopMoisture):  #method for updating moisture display
        self.TopMoistureValue = TopMoisture
        self.TopMoisturedisplay.display(self.TopMoistureValue)
                        
    def updateMiddleMoistureDisplay(self, MiddleMoisture):  #method for updating moisture display
        self.MiddleMoistureValue = MiddleMoisture
        self.MiddleMoisturedisplay.display(self.MiddleMoistureValue)
        
    def updateBottomMoistureDisplay(self, BottomMoisture):  #method for updating moisture display
        self.BottomMoistureValue = BottomMoisture
        self.BottomMoisturedisplay.display(self.BottomMoistureValue)
        
    def getInitialSampleWeight(self): #method for saving the values input in the boxes - made an attempt to convert to int or float as appropriate
        global initialSampleWeightTemp
        global initialSampleWeight
        if self.InitialSampleWeight.text() != "":
            initialSampleWeightTemp = self.InitialSampleWeight.text()
        try:
            initialSampleWeight = float(initialSampleWeightTemp)
        except:
            initialSampleWeight = int(initialSampleWeightTemp)
    
    def getEStopTemp(self):
        global EStopTemp
        global EStopTempTemp                
        if self.EStopTemp.text() != "":
            EStopTempTemp = self.EStopTemp.text()
        try:
            EStopTemp = float(EStopTempTemp)
        except:
            EStopTemp = int(EStopTempTemp)
        
    def getDryMatterWeight(self):   #method for saving the values input in the boxes - made an attempt to convert to int or float as appropriate
        global dryMatterTemp
        global dryMatter
        if self.DryMatterWeight.text() != "":
            dryMatterTemp = self.DryMatterWeight.text()
        try:
            dryMatter = float(dryMatterTemp)
        except:
            dryMatter = int(dryMatterTemp)
            
    def getTargetWeightPercent(self):   #method for saving the values input in the boxes - made an attempt to convert to int or float as appropriate
        global targetPercentTemp
        global targetPercent
        if self.TargetWeightPercent.text() != "":
            targetPercentTemp = self.TargetWeightPercent.text()
        try:
            targetPercent = float(targetPercentTemp)
        except:
            targetPercent = int(targetPercentTemp)         
         
        
#Running 2 things at once: You need this AThread (inherited from the QThread class) to run your main program at the same time as the GUI
class AThread(QThread):
    
    def run(self):  #Create this function to run
        #bring in global variables
        global weightTop
        global weightMid
        global weightBot
        global dryMatter
        global initialSampleWeight
        global targetWeight
        
        dryMatterPercent = dryMatter/initialSampleWeight
        initialMoisturePercent = 1-dryMatterPercent
        
        #ui2.show()
        
        count = 0  #In this case creating a counter
        while True:   #While counter is less than 100 (edited to While True, from count < 100)
            #time.sleep(.5)  #Wait half a second
            #print("Increasing") #Print this for debugging
            count += 1  #increment count
            ui2.updateLED(count)  #Update the LED by calling this method of the ControlWindow Class
            x = DS18B20()
            counter=x.device_count()              #count number of temperature sensors
            i = 0
            templist = []                       #create list to save temp data
            while i < counter:
                temp_temp = x.tempC(i)          #read temp data of first sensor
                templist.append(temp_temp)
                i += 1
            top_temp_f = (templist[0] * 9.0 / 5.0 + 32.0) * 0.98945
            bot_temp_f = (templist[1] * 9.0 / 5.0 + 32.0) * 0.96945
            ui2.updateTopTemp(top_temp_f)  #updates temperature sensor display
            ui2.updateBotTemp(bot_temp_f)
            
            vRatioTop = wd.main0()  #calls main0 of other script, to import voltage ratio reading
            #print(vRatioTop)
            weightTop = -5.10209e5*vRatioTop-zeroTop  #calculates weight based on calibration
 
            
            vRatioMid = wd.main1()  #calls main1 of other script, to import voltage ratio reading
            #print(vRatioMid)
            weightMid = -5.002223e5*vRatioMid-zeroMid  #calculates weight based on calibration
            
            
            vRatioBot = wd.main2()  #calls main0 of other script, to import voltage ratio reading
            #print(vRatioBot)
            weightBot = -4.9078e5*vRatioBot-zeroBot  #calculates weight based on calibration

            ui2.updateTopWeight(weightTop)  #updates weight display box
            ui2.updateMiddleWeight(weightMid)  #updates weight display box
            ui2.updateBottomWeight(weightBot)  #updates weight display box
            
            moistureTop = -100*(((dryMatter*initialWeightTop)/(weightTop*initialSampleWeight))-1)    #DO MOISTURE CALC HERE
            moistureMid = -100*(((dryMatter*initialWeightMid)/(weightMid*initialSampleWeight))-1)     #DO MOISTURE CALC HERE
            moistureBot = -100*(((dryMatter*initialWeightBot)/(weightBot*initialSampleWeight))-1)        #DO MOISTURE CALC HERE
            ui2.updateTopMoistureDisplay(moistureTop) #updates moisture display box
            ui2.updateMiddleMoistureDisplay(moistureMid)  #updates moisture display box
            ui2.updateBottomMoistureDisplay(moistureBot)  #updates moisture display box

#            print(EStopTemp)
            ui2.show()
            app.processEvents()
            
            
            #print(started)
            if started == True:
                GPIO.output(6, GPIO.HIGH)

            #else:
                #GPIO.output(6, GPIO.LOW)
                #if moistureTop < 8:
                #    shutoff()
            
                if moistureTop < targetPercent or moistureMid < targetPercent or moistureBot < targetPercent:
                    shutoff()
            
                      
            #Test of controlling power relay based on temperature
            if top_temp_f > EStopTemp or bot_temp_f > EStopTemp:
                shutoff()
#            else:
#                startup()
            
            #ui2.updateProgressBar(count)  #progress bar test
            
            #Test of controlling servo. Results: lots of noise, but it works. Kind of scary
#            if temp_f_top > 90:
#                p.ChangeDutyCycle(7.5)

#Main program - the IF statement means it will only run if you call this program (won't run if you only include this program in another python code)
if __name__ == '__main__':
    app = QApplication(sys.argv)  #Needed to start the GUI program
    
    ui2 = ControlWindow()  #Name a new instance of ControlWindow. Named it ui2 but you can do whatever
    ui2.show()  #show ui2

    Threado = AThread() #Create an instance of the AThread class
    Threado.start()  #sStart the AThread class and function (run your code inside AThread)
    
    app.exec_()
    GPIO.output(6, GPIO.LOW)
    sys.exit()
    #sys.exit(app.exec_()) #If you close a window, or get to this point in the main, it kills the program
    #This will close if your AThread loop ends (although you may have to write in there a code to close the window)