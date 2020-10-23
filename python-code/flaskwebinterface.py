#!/usr/bin/env python
# Web/website Interface for the GPS Tag Dunker.
# Authored by TechDevTom/Tom Southworth, 2020, for The Arribada Initiative.

# LIBRARY IMPORTING
from flask import Flask, render_template
import datetime
from time import sleep
import RPi.GPIO as GPIO
import pause

# VARIABLE SETUP
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

# Create an array for all the different schduled lifts to go into.
scheduledLifts = []


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

# This is the Main Page of the GPS Tag Dunker.
@app.route('/')
def index():
	now = datetime.datetime.now()
	dateTime = now.strftime("%Y-%m-%d %H:%M")
	templateData = {
		'title' : 'GPS Tag Dunker',
		'button' : dateTime
		}
	return render_template('index.html', **templateData)

# Runs the Flask server and website.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')