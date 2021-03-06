#!/usr/bin/python
# Author: HARRY CHAND <hari.chand.balasubramaiam@intel.com>
# Copyright (c) 2014 Intel Corporation.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import time, sys, signal, atexit, mraa, thread
import pyupm_grove as grove
import pyupm_guvas12d as upmUV
import pyupm_grovemoisture as upmMoisture
import pyupm_stepmotor as mylib
import pyupm_servo as servo
#import pyupm_th02
#from Servo import *

# Instantiate a GP2Y0A on Analog pin 5
myIRProximity = mraa.Aio(5)
# Create the temperature sensor object using AIO pin 0
temp = grove.GroveTemp(0)
# Instantiate a Grove Moisture sensor on AIO pin 1
myMoisture = upmMoisture.GroveMoisture(1)
# Create the light sensor object using AIO pin 2
light = grove.GroveLight(2);
# Instantiate a UV sensor on analog pin A0
myUVSensor = upmUV.GUVAS12D(3);
#defined THo2 i2c address
th02 = pyupm_th02.TH02(6,0x40)
# Instantiate a StepMotorX object on pins 2 (dir) and 3 (step)
stepperX = mylib.StepMotor(2, 3)
# Instantiate a StepMotorY object on pins 4 (dir) and 5 (step)
stepperY = mylib.StepMotor(4, 5)
# Instantiate a water pump on GPIO 6
waterpump = mraa.Gpio(6)
waterpump.dir(mraa.DIR_OUT)
waterpump.write(0)
# Instantiate a Servo motor on port D6
#myServo = Servo("First Servo")
#myServo.attach(6)
# Create the servo object using D6
gServo = servo.ES08A(6)
# digital contact switch - SwitchX for GPIO 7 and SwitchY for GPIO 8
switchX = mraa.Gpio(7)    # while switchX.read() == 1:
switchX.dir(mraa.DIR_IN)
switchY = mraa.Gpio(8)
switchY.dir(mraa.DIR_IN)
# Instantiate a StepperMotor Enable on GPIO 9
EnableStepper = mraa.Gpio(9)
EnableStepper.dir(mraa.DIR_OUT)
EnableStepper.write(1)
# Create the button object using GPIO pin 0
button = grove.GroveButton(0)  # Prefer use interupt   -> ## button.value()

		
# analog voltage, usually 3.3 or 5.0 for GUVAS12D
AREF = 5.0;
SAMPLES_PER_QUERY = 1024;


## Exit handlers ##
# This function stops python from printing a stacktrace when you hit control-C
def SIGINTHandler(signum, frame):
	raise SystemExit

# This function lets you run code on exit, including functions from myUVSensor
def exitHandler():
	print "Exiting"
	sys.exit(0)

# Register exit handlers
atexit.register(exitHandler)
signal.signal(signal.SIGINT, SIGINTHandler)


# Function Display UV sensor value
def UVsensor():
	s = ("AREF:  {0}, "
	"Voltage value (higher means more UV): "
	"{1}".format(AREF,
	myUVSensor.value(AREF, SAMPLES_PER_QUERY)))
	print s
	return s

# Function Display light sensor value
def Lightsensor():
	print light.name() + " raw value is %d" % light.raw_value() + \
        ", which is roughly %d" % light.value() + " lux"
	return light.value()

# Function Display Distance sensor value
def Distancesensor():
	Vproximity = float(myIRProximity.read())*AREF/SAMPLES_PER_QUERY
	print "Distance in Voltage (higher mean closer) : " + str(Vproximity)
	return Vproximity

# Function Display Temperature value
def Temperature():
	celsius = temp.value()
        fahrenheit = celsius * 9.0/5.0 + 32.0
        print "%d degrees Celsius, or %d degrees Fahrenheit"% (celsius, fahrenheit)
	return celsius
		
# Function Display soil Moisture value
def Soilsensor():
	moisture_val = myMoisture.value()
	if (moisture_val >= 0 and moisture_val < 300):
		result = "Dry"
	elif (moisture_val >= 300 and moisture_val < 600):
		result = "Moist"
	else:
		result = "Wet"
	print "Moisture value: {0}, {1}".format(moisture_val, result)
	return moisture_val

# Function Display Temperature and humidity
def TempTH02():
	print "Temperature value is : " + str(th02.getTemperature())
	print "The value of Humidity : " + str(th02.getHumidity ())
	return th02.getTemperature()

def ServoDown():
	# From 0 to 180 degrees
	gServo.setAngle(0)
	time.sleep(1)
	gServo.setAngle(180)
	return
	
def ServoUp():
	gServo.setAngle(180)
	time.sleep(1)
	gServo.setAngle(0)
	return
	
# Read the input and print both the raw value and a rough lux value,
# waiting one second between readings
while 1:
	UVvalue = UVsensor()
	Lightvalue = Lightsensor()
	Distancevalue = Distancesensor()
	Soilvalue = Soilsensor()
	#Tempvalue = TempTH02() 
        Tempvalue = Temperature()
	
	# Moving Motor to left and right direction
	print "Rotating 1 revolution forward and back at 150 rpm."
	EnableStepper.write(0)
	stepperX.setSpeed(150)
        stepperY.setSpeed(150)
	stepperX.stepForward(200)
	time.sleep(1)
        stepperY.stepForward(200)
        time.sleep(1)
	stepperX.stepBackward(200)
        time.sleep(1)
        stepperY.stepBackward(200)
	print "End Stepper Motor"
	time.sleep(2)
	EnableStepper.write(1)
	
	# activate waterpump
	print "activate water pump"
	waterpump.write(1)
	time.sleep(1)
	waterpump.write(0)
	
	# Servo Z-axis down and up
	print "Servo z-axis should be down"
	ServoDown()
	time.sleep(2)
	print "Servo z-axis should be up"
	ServoUp()
	
	print "Display Sensor :"+str(UVvalue)+" , "+str(Lightvalue)+" , "+str(Distancevalue)+" , "+str(Soilvalue)+" , "+str(Tempvalue)+" ."
	print "\n"
	print "Reading input value ; SwitchX: %d ; SwitchY: %d ; RestartButton: %d ."% (switchX.read(), switchY.read(), button.value()) 


del light  # Delete the light sensor object
del temp   # Delete the temperature sensor object
del th02   # Delete the tho2 sensor object
del button # Delete the button object
del gServo # Delete the servo motor object


# Information:
## Soil moisture Values (approximate):
# 0-300,   sensor in air or dry soil
# 300-600, sensor in humid soil
# 600+,    sensor in wet soil or submerged in water

## Infrared Proximity Sensor 
# The higher the voltage (closer to AREF) the closer the object is.
# NOTE: The measured voltage will probably not exceed 3.3 volts.
# Every second, print the averaged voltage value
# (averaged over 20 samples).
