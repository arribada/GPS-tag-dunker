#!/usr/bin/env python
# Web/website Interface for the GPS Tag Dunker.
# Authored by TechDevTom/Tom Southworth, 2020, for The Arribada Initiative.

# LIBRARY IMPORTING
import os
import datetime
import pause
import json
import RPi.GPIO as GPIO
from time import sleep
from flask import Flask, render_template


# NOTES:  DateTime conversion = "date_time_obj = datetime.strptime(date_time_str, %H:%M:%S')"


# CLASSES CODE
# Define the Schedule Class
class Schedule:
    """The class which holds Schedule data"""

    def __init__(self, startTime, dunkTime, riseTime, loopEnabled, loopCount):
        """Initialise the Schedule's attributes"""
        self.startTime		= startTime
        self.dunkTime      	= dunkTime
        self.riseTime    	= riseTime
        self.loopEnabled  	= loopEnabled
        self.loopCount  	= loopCount

    def getData(self):
        """Returns this Schedule's Info"""
        return {
		'title':'GPS Tag Dunker',
		'scheduleStartTime':self.startTime,
		'scheduleDunkTime':self.dunkTime,
		'scheduleRiseTime':self.riseTime,
		'scheduleLoopEnabled':self.loopEnabled,
		'scheduleLoopCount':self.loopCount
		}

    def updateScheduleInfo(self, startTime, dunkTime, riseTime, loopEnabled, loopCount):
        """Updates this Schedule's information"""
        self.startTime		= startTime
        self.dunkTime      	= dunkTime
        self.riseTime    	= riseTime
        self.loopEnabled  	= loopEnabled
        self.loopCount  	= loopCount


# VARIABLE SETUP
# GPS TAG DUNKER SETTINGS VARIABLES
# The file path of the Settings file.
settingsFilePath = os.getcwd() + "/settings.json"

# Allows for reading whether the GPS Tag Dunker is currently dunking.
isDunking = False

# Declares an empty Schedule ready to be populated by JSON info.
currentSchedule = Schedule("", "", "", "", "")

# Variable the holds the amount of seconds that are in an hour.
secondsInHours = 3600

# Create an array for all the different schduled lifts to go into.
scheduledLifts = []

# WINCH CONTROL VARIABLES
# Clean up any errors from last execution (ensures winch not reeling).
GPIO.setwarnings(False)
GPIO.cleanup()

# Set the board to use the GPIO numbering system for its pins.
GPIO.setmode(GPIO.BCM)

# Define the relay pins, which are used to let the winch cable in or out.
winchInPin = 21
GPIO.setup(winchInPin, GPIO.OUT)
winchOutPin = 20
GPIO.setup(winchOutPin, GPIO.OUT)

# Define the delay time between winch movements (for safety).
delay = 1


# SETTINGS CODE
# Loads in the JSON settings data
def LoadSettings():

	with open(settingsFilePath, "r") as file_object:
		settings = json.load(file_object);

	# Assign GPS Tag Dunker state info.
	isDunking = settings['State']['isDunking']

	# Load in the current schedule's information.
	global currentSchedule
	currentSchedule = Schedule(settings['CurrentSchedule']['startTime'], 
		settings['CurrentSchedule']['dunkTime'], 
		settings['CurrentSchedule']['riseTime'], 
		settings['CurrentSchedule']['loopEnabled'],	
		settings['CurrentSchedule']['loopCount'])

LoadSettings();
print (currentSchedule.dunkTime);


# WINCH CONTROL CODE
# Define Winch Winding Methods
# Wind In Method
def WindIn():
	StopWind()
	GPIO.output(winchInPin, GPIO.HIGH)
	GPIO.output(winchOutPin, GPIO.LOW)

# Wind Out Method
def WindOut():
	StopWind()
	GPIO.output(winchInPin, GPIO.LOW)
	GPIO.output(winchOutPin, GPIO.HIGH)

# Stop Wind Method
def StopWind():
	GPIO.output(winchInPin, GPIO.LOW)
	GPIO.output(winchOutPin, GPIO.LOW)
	sleep(delay)


# LIFT/DUNK SCHEDULE READING
def ReadSchedule():
	with open (file_path) as file_object:
		for line in file_object:
			scheduledLifts.append(line)



# WEBSITE CREATION
# Create basic website.
app = Flask(__name__)

# This is the main/index page of the GPS Tag Dunker web interface.
@app.route('/')
def index():
	return render_template('index.html', **currentSchedule.getData())

# This is for the function that stops the Winch from winding in or out.
@app.route('/webStopWind') 
def webStopWind():
 	StopWind();
	return render_template('index.html', **currentSchedule.getData())

# This is for the function that winds the Winch out.
@app.route('/webWindOut') 
def webWindOut():
 	WindOut();
	return render_template('index.html', **currentSchedule.getData())

# This is for the function that winds the Winch in.
@app.route('/webWindIn') 
def webWindIn():
 	WindIn();
	return render_template('index.html', **currentSchedule.getData())

# Runs the Flask server and website.
if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
