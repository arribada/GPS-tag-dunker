#!/usr/bin/env python
# Web/website Interface for the GPS Tag Dunker.
# Authored by TechDevTom/Tom Southworth, 2020, for The Arribada Initiative.

# LIBRARY IMPORTING
import os;
import datetime
import pause
import json;
import RPi.GPIO as GPIO
from time import sleep
from flask import Flask, render_template


# CLASSES CODE
# Define the Schedule Class
class Schedule:
    """The class which holds Schedule data"""

    def __init__(startTime, dunkTime, RiseTime, loopEnabled, loopCount):
        """Initialise the Schedule's attributes"""
        self.startTime		= startTime
        self.dunkTime      	= dunkTime
        self.RiseTime    	= RiseTime
        self.loopEnabled  	= loopEnabled
        self.loopCount  	= loopCount

    def getTimeRemaining(self):
        """Returns this Schedule's Info"""
        return (f"")

    def updateScheduleInfo(startTime, dunkTime, RiseTime, loopEnabled, loopCount):
        """Updates this Schedule's information"""
        self.startTime		= startTime
        self.dunkTime      	= dunkTime
        self.RiseTime    	= RiseTime
        self.loopEnabled  	= loopEnabled
        self.loopCount  	= loopCount
        

# VARIABLE SETUP
# GPS TAG DUNKER SETTINGS VARIABLES
# The file path of the Settings file.
settingsFilePath = os.getcwd() + "/settings.json";

# Allows for reading whether the GPS Tag Dunker is currently dunking.
isDunking = False;

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

	with open(settingsFilePath) as file_object:
		settings = json.load(file_object);

	isDunking = settings["State"][0]["isDunked"];

LoadSettings();


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
	now = datetime.datetime.now()
	dateTime = now.strftime("%Y-%m-%d %H:%M")
	templateData = {
		'title' : 'GPS Tag Dunker',
		'time' : dateTime
		}
	return render_template('index.html', **templateData)

# Runs the Flask server and website.
if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')