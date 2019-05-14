import sys
import time
import traceback
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *
import statistics

data = 0
datalist = []
sleeptime = 2

try:
    from PhidgetHelperFunctions import *
except ImportError:
    sys.stderr.write("\nCould not find PhidgetHelperFunctions. Either add PhdiegtHelperFunctions.py to your project folder "
                      "or remove the import from your project.")
    sys.stderr.write("\nPress ENTER to end program.")
    readin = sys.stdin.readline()
    sys.exit()

"""
* Configures the device's DataInterval and ChangeTrigger.
* Displays info about the attached Phidget channel.
* Fired when a Phidget channel with onAttachHandler registered attaches
*
* @param self The Phidget channel that fired the attach event
"""
def onAttachHandler(self):
    
    ph = self
    try:
        #If you are unsure how to use more than one Phidget channel with this event, we recommend going to
        #www.phidgets.com/docs/Using_Multiple_Phidgets for information
        
        #print("\nAttach Event:")
        
        """
        * Get device information and display it.
        """
        channelClassName = ph.getChannelClassName()
        serialNumber = ph.getDeviceSerialNumber()
        channel = ph.getChannel()
        if(ph.getDeviceClass() == DeviceClass.PHIDCLASS_VINT):
            hubPort = ph.getHubPort()
#            print("\n\t-> Channel Class: " + channelClassName + "\n\t-> Serial Number: " + str(serialNumber) +
#                "\n\t-> Hub Port: " + str(hubPort) + "\n\t-> Channel:  " + str(channel) + "\n")
#        else:
#            print("\n\t-> Channel Class: " + channelClassName + "\n\t-> Serial Number: " + str(serialNumber) +
#                    "\n\t-> Channel:  " + str(channel) + "\n")
    
        """
        * Set the DataInterval inside of the attach handler to initialize the device with this value.
        * DataInterval defines the minimum time between VoltageRatioChange events.
        * DataInterval can be set to any value from MinDataInterval to MaxDataInterval.
        """
        #print("\n\tSetting DataInterval to 1000ms")
        ph.setDataInterval(10)

        """
        * Set the VoltageRatioChangeTrigger inside of the attach handler to initialize the device with this value.
        * VoltageRatioChangeTrigger will affect the frequency of VoltageRatioChange events, by limiting them to only occur when
        * the voltage ratio changes by at least the value set.
        """
        #print("\tSetting Voltage Ratio ChangeTrigger to 0.0")
        ph.setVoltageRatioChangeTrigger(0.0)
        
        """
        * Set the SensorType inside of the attach handler to initialize the device with this value.
        * You can find the appropriate SensorType for your sensor in its User Guide and the VoltageRatioInput API
        * SensorType will apply the appropriate calculations to the voltage ratio reported by the device
        * to convert it to the sensor's units.
        * SensorType can only be set for Sensor Port voltage ratio inputs (VINT Ports and Analog Input Ports)
        """
        if(ph.getChannelSubclass() == ChannelSubclass.PHIDCHSUBCLASS_VOLTAGERATIOINPUT_SENSOR_PORT):
            #print("\tSetting VoltageRatio SensorType")
            ph.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_VOLTAGERATIO)
            
        
    except PhidgetException as e:
        print("\nError in Attach Event:")
        DisplayError(e)
        traceback.print_exc()
        return

"""
* Displays info about the detached Phidget channel.
* Fired when a Phidget channel with onDetachHandler registered detaches
*
* @param self The Phidget channel that fired the attach event
"""
def onDetachHandler(self):

    ph = self

    try:
        #If you are unsure how to use more than one Phidget channel with this event, we recommend going to
        #www.phidgets.com/docs/Using_Multiple_Phidgets for information
        
        #print("\nDetach Event:")
        
        """
        * Get device information and display it.
        """
        channelClassName = ph.getChannelClassName()
        serialNumber = ph.getDeviceSerialNumber()
        channel = ph.getChannel()
        if(ph.getDeviceClass() == DeviceClass.PHIDCLASS_VINT):
            hubPort = ph.getHubPort()
#            print("\n\t-> Channel Class: " + channelClassName + "\n\t-> Serial Number: " + str(serialNumber) +
#                "\n\t-> Hub Port: " + str(hubPort) + "\n\t-> Channel:  " + str(channel) + "\n")
#        else:
#            print("\n\t-> Channel Class: " + channelClassName + "\n\t-> Serial Number: " + str(serialNumber) +
#                    "\n\t-> Channel:  " + str(channel) + "\n")
        
    except PhidgetException as e:
        print("\nError in Detach Event:")
        DisplayError(e)
        traceback.print_exc()
        return


"""
* Writes Phidget error info to stderr.
* Fired when a Phidget channel with onErrorHandler registered encounters an error in the library
*
* @param self The Phidget channel that fired the attach event
* @param errorCode the code associated with the error of enum type ph.ErrorEventCode
* @param errorString string containing the description of the error fired
"""
def onErrorHandler(self, errorCode, errorString):

    sys.stderr.write("[Phidget Error Event] -> " + errorString + " (" + str(errorCode) + ")\n")

"""
* Outputs the VoltageRatioInput's most recently reported voltage ratio.
* Fired when a VoltageRatioInput channel with onVoltageRatioChangeHandler registered meets DataInterval and ChangeTrigger criteria
*
* @param self The VoltageRatioInput channel that fired the VoltageRatioChange event
* @param voltageRatio The reported voltage ratio from the VoltageRatioInput channel
"""
def onVoltageRatioChangeHandler(self, voltageRatio):

    #If you are unsure how to use more than one Phidget channel with this event, we recommend going to
    #www.phidgets.com/docs/Using_Multiple_Phidgets for information

    #print("[VoltageRatio Event] -> Voltage Ratio: " + str(voltageRatio))
    global data
    global datalist
    datalist.append(float(voltageRatio))
    data = statistics.mean(datalist)
#    data = float(voltageRatio)
#    print(data)

"""
* Outputs the VoltageRatioInput's most recently reported sensor value.
* Fired when a VoltageRatioInput channel with onSensorChangeHandler registered meets DataInterval and ChangeTrigger criteria
*
* @param self The VoltageRatioInput channel that fired the SensorChange event
* @param sensorValue The reported sensor value from the VoltageRatioInput channel
"""
def onSensorChangeHandler(self, sensorValue, sensorUnit):

    #If you are unsure how to use more than one Phidget channel with this event, we recommend going to
    #www.phidgets.com/docs/Using_Multiple_Phidgets for information

    print("[Sensor Event] -> Sensor Value: " + str(sensorValue) + sensorUnit.symbol)


"""
* Prints descriptions of how events related to this class work
"""
def PrintEventDescriptions():

    print("\n--------------------\n"
        "\n  | Voltage Ratio change events will call their associated function every time new voltage ratio data is received from the device.\n"
        "  | The rate of these events can be set by adjusting the DataInterval for the channel.\n")
        
    print(
        "\n  | Sensor change events contain the most recent sensor value received from the device.\n"
        "  | Sensor change events will occur instead of Voltage Ratio change events if the SensorType is changed from the default.\n"
        "  | Press ENTER once you have read this message.")
    readin = sys.stdin.readline(1)
    
    print("\n--------------------")
   
"""
* Creates, configures, and opens a VoltageRatioInput channel.
* Displays Voltage Ratio events for 10 seconds
* Closes out VoltageRatioInput channel
*
* @return 0 if the program exits successfully, 1 if it exits with errors.
"""

def main0():
    global sleeptime
    try:
        """
        * Allocate a new Phidget Channel object
        """
        ch0 = VoltageRatioInput()
        
        """
        * Set matching parameters to specify which channel to open
        """
        
        #You may remove this line and hard-code the addressing parameters to fit your application
        #channelInfo = AskForDeviceParameters(ch)
        
        ch0.setDeviceSerialNumber(566690)
        ch0.setChannel(0)   
        
        
        """
        * Add event handlers before calling open so that no events are missed.
        """
        #print("\n--------------------------------------")
        #print("\nSetting OnAttachHandler...")
        ch0.setOnAttachHandler(onAttachHandler)
        
        #print("Setting OnDetachHandler...")
        ch0.setOnDetachHandler(onDetachHandler)
        
        #print("Setting OnErrorHandler...")
        ch0.setOnErrorHandler(onErrorHandler)
        
        #This call may be harmlessly removed
        #PrintEventDescriptions()
        
        #print("\nSetting OnVoltageRatioChangeHandler...")
        ch0.setOnVoltageRatioChangeHandler(onVoltageRatioChangeHandler)
        
        #print("\nSetting OnSensorChangeHandler...")
        ch0.setOnSensorChangeHandler(onSensorChangeHandler)
        
        """
        * Open the channel with a timeout
        """
        
        #print("\nOpening and Waiting for Attachment...")
        
        try:
            ch0.openWaitForAttachment(5000)
        except PhidgetException as e:
            PrintOpenErrorMessage(e, ch0)
            raise EndProgramSignal("Program Terminated: Open Failed")
        
        #print("Sampling data for 10 seconds...")
        
        #print("You can do stuff with your Phidgets here and/or in the event handlers.")
        
        time.sleep(sleeptime)
        
        """
        * Perform clean up and exit
        """
        #print("\nDone Sampling...")

        #print("Cleaning up...")
        ch0.close()
        #print("\nExiting...")
        global data
        weight0 = data
        datalist.clear()
        return weight0
        

    except PhidgetException as e:
        sys.stderr.write("\nExiting with error(s)...")
        DisplayError(e)
        traceback.print_exc()
        print("Cleaning up...")
        ch0.close()
        return 1
    except EndProgramSignal as e:
        print(e)
        print("Cleaning up...")
        ch0.close()
        return 1
    except RuntimeError as e:
         sys.stderr.write("Runtime Error: \n\t" + e)
         traceback.print_exc()
         return 1
    #finally:
        #print("Press ENTER to end program.")
        #readin = sys.stdin.readline()

def main1():
    global sleeptime
    try:
        """
        * Allocate a new Phidget Channel object
        """
        ch1 = VoltageRatioInput()
        
        """
        * Set matching parameters to specify which channel to open
        """
        
        #You may remove this line and hard-code the addressing parameters to fit your application
        #channelInfo = AskForDeviceParameters(ch)
        
        ch1.setDeviceSerialNumber(566690)
        ch1.setChannel(1)   
        
        
        """
        * Add event handlers before calling open so that no events are missed.
        """
        #print("\n--------------------------------------")
        #print("\nSetting OnAttachHandler...")
        ch1.setOnAttachHandler(onAttachHandler)
        
        #print("Setting OnDetachHandler...")
        ch1.setOnDetachHandler(onDetachHandler)
        
        #print("Setting OnErrorHandler...")
        ch1.setOnErrorHandler(onErrorHandler)
        
        #This call may be harmlessly removed
        #PrintEventDescriptions()
        
        #print("\nSetting OnVoltageRatioChangeHandler...")
        ch1.setOnVoltageRatioChangeHandler(onVoltageRatioChangeHandler)
        
        #print("\nSetting OnSensorChangeHandler...")
        ch1.setOnSensorChangeHandler(onSensorChangeHandler)
        
        """
        * Open the channel with a timeout
        """
        
        #print("\nOpening and Waiting for Attachment...")
        
        try:
            ch1.openWaitForAttachment(5000)
        except PhidgetException as e:
            PrintOpenErrorMessage(e, ch1)
            raise EndProgramSignal("Program Terminated: Open Failed")
        
        #print("Sampling data for 10 seconds...")
        
        #print("You can do stuff with your Phidgets here and/or in the event handlers.")
        
        time.sleep(sleeptime)
        
        """
        * Perform clean up and exit
        """
        #print("\nDone Sampling...")

        #print("Cleaning up...")
        ch1.close()
        #print("\nExiting...")
        global data
        weight1 = data
        datalist.clear()
        return weight1

    except PhidgetException as e:
        sys.stderr.write("\nExiting with error(s)...")
        DisplayError(e)
        traceback.print_exc()
        print("Cleaning up...")
        ch1.close()
        return 1
    except EndProgramSignal as e:
        print(e)
        print("Cleaning up...")
        ch1.close()
        return 1
    except RuntimeError as e:
         sys.stderr.write("Runtime Error: \n\t" + e)
         traceback.print_exc()
         return 1
    #finally:
        #print("Press ENTER to end program.")
        #readin = sys.stdin.readline()

def main2():
    global sleeptime
    try:
        """
        * Allocate a new Phidget Channel object
        """
        ch2 = VoltageRatioInput()
        
        """
        * Set matching parameters to specify which channel to open
        """
        
        #You may remove this line and hard-code the addressing parameters to fit your application
        #channelInfo = AskForDeviceParameters(ch)
        
        ch2.setDeviceSerialNumber(566690)
        ch2.setChannel(2)   
        
        
        """
        * Add event handlers before calling open so that no events are missed.
        """
        #print("\n--------------------------------------")
        #print("\nSetting OnAttachHandler...")
        ch2.setOnAttachHandler(onAttachHandler)
        
        #print("Setting OnDetachHandler...")
        ch2.setOnDetachHandler(onDetachHandler)
        
        #print("Setting OnErrorHandler...")
        ch2.setOnErrorHandler(onErrorHandler)
        
        #This call may be harmlessly removed
        #PrintEventDescriptions()
        
        #print("\nSetting OnVoltageRatioChangeHandler...")
        ch2.setOnVoltageRatioChangeHandler(onVoltageRatioChangeHandler)
        
        #print("\nSetting OnSensorChangeHandler...")
        ch2.setOnSensorChangeHandler(onSensorChangeHandler)
        
        """
        * Open the channel with a timeout
        """
        
        #print("\nOpening and Waiting for Attachment...")
        
        try:
            ch2.openWaitForAttachment(5000)
        except PhidgetException as e:
            PrintOpenErrorMessage(e, ch2)
            raise EndProgramSignal("Program Terminated: Open Failed")
        
        #print("Sampling data for 10 seconds...")
        
        #print("You can do stuff with your Phidgets here and/or in the event handlers.")
        
        time.sleep(sleeptime)
        
        """
        * Perform clean up and exit
        """
        #print("\nDone Sampling...")

        #print("Cleaning up...")
        ch2.close()
        #print("\nExiting...")
        global data
        weight2 = data
        datalist.clear()
        return weight2

    except PhidgetException as e:
        sys.stderr.write("\nExiting with error(s)...")
        DisplayError(e)
        traceback.print_exc()
        print("Cleaning up...")
        ch2.close()
        return 1
    except EndProgramSignal as e:
        print(e)
        print("Cleaning up...")
        ch2.close()
        return 1
    except RuntimeError as e:
         sys.stderr.write("Runtime Error: \n\t" + e)
         traceback.print_exc()
         return 1
    #finally:
        #print("Press ENTER to end program.")
        #readin = sys.stdin.readline()


#main0()
