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
from flask import Flask, render_template, request, url_for


# NOTES:  DateTime conversion = "date_time_obj = datetime.strptime(date_time_str, %H:%M:%S')"


# CLASSES CODE
# Define the Schedule Class
class Schedule:
    """The class which holds Schedule data"""

    def __init__(self, name, startTime, dunkTime, riseTime, loopEnabled, loopCount):
        """Initialise the Schedule's attributes"""
        self.name 			= name
        self.startTime		= startTime
        self.dunkTime      	= dunkTime
        self.riseTime    	= riseTime
        self.loopEnabled  	= loopEnabled
        self.loopCount  	= loopCount

    def getData(self):
        """Returns this Schedule's Info"""
        return {
        'name':self.name,
		'startTime':self.startTime,
		'dunkTime':self.dunkTime,
		'riseTime':self.riseTime,
		'loopEnabled':self.loopEnabled,
		'loopCount':self.loopCount
		}

    def updateScheduleInfo(self, name, startTime, dunkTime, riseTime, loopEnabled, loopCount):
        """Updates this Schedule's information"""
        self.name 			= name
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
currentSchedule = Schedule("", "", "", "", "", "")

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
# Loads in the Settings data from the settings.json file.
def GetSettingsData():

	with open(settingsFilePath, "r") as file_object:
		settings = json.load(file_object);
		return settings;


# Loads in the JSON settings and Schedule data.
def LoadSettings():

	# Retrieve the settings
	settings = GetSettingsData();

	# Assign GPS Tag Dunker state info.
	global isDunking
	isDunking = settings['State']['isDunking']

	# Load in the current schedule's information.
	global currentSchedule
	currentSchedule = Schedule(settings['CurrentSchedule']['name'],
		settings['CurrentSchedule']['startTime'],
		settings['CurrentSchedule']['dunkTime'],
		settings['CurrentSchedule']['riseTime'],
		settings['CurrentSchedule']['loopEnabled'],
		settings['CurrentSchedule']['loopCount'])

LoadSettings();


# Saves the given json data to the settings.json file's list of Saved Schedules.
def SaveSchedule(scheduleData):

	# Retrieve the settings
	settings = GetSettingsData()

	# Load in the SavedSchdules list and append the new Schedule
	# TODO:  Need to insert check to see if all parameters for new Schedule already exist.
	savedSchedules = settings['SavedSchedules']
	savedSchedules.append(scheduleData)

	# Save new settings data into json file.
	with open(settingsFilePath, 'w') as f: 
		json.dump(settings, f, indent=4);


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


# WEBSITE CREATION
# Create basic website.
app = Flask(__name__)


# The index method determines which page to load based on whether the tag dunker is dunking or not.
@app.route('/')
def index():

	if isDunking:
		return schedule();
	else:
		return noSchedule();


# This is the page that is presented when a schedule is not running.
@app.route('/NoSchedule')
def noSchedule():

	dunkData = currentSchedule.getData()
	scheduleString = "There is no scheduled dunk occurring.";
	testingString = ('Testing is available.');
	templateData = {'ScheduleString':scheduleString, 'TestingString':testingString}
	return render_template('noschedule.html', **templateData)


# This is the page that is presented when scheduled dunk is running.
# TODO:  Sort out data string as it's a mess, need better formatting.
@app.route('/Schedule')
def schedule():

	dunkData = currentSchedule.getData()
	scheduleString = ('Start time: ', {dunkData['startTime']}, ' Dunk time: ', {dunkData['dunkTime']} , 'Rise time: ', {dunkData['riseTime']}, ' Loop enabled: ', {dunkData['loopEnabled']} , 'Loop count: ', {dunkData['loopCount']});
	testingString = ('Testing is not available while a dunk is ongoing.');
	templateData = {'ScheduleString':scheduleString, 'TestingString':testingString}
	return render_template('schedule.html', **templateData)


# Method for loading in HTML form data from the noSchedule page.
# TODO:  Actually get this to load data so I can append it to settings.json file.
@app.route('/webSaveSchedule', methods=['GET', 'POST'])
def webSaveSchedule():

	print ("Attempting to Save Schedule");

	print ('Request Method:  ' + request.method)
	if request.method == 'GET':
		scheduleName = request.args.get('scheduleName', 'N/A')

		print ('Args:  ' + str(len(request.args.keys())))
		print ('Schedule:  ' + scheduleName);

	return noSchedule();


	# scheduleData = {'name':str(request.form.get('scheduleName')),
	# 	'startTime':'',
	# 	'dunkTime':request.form.get('dunkTime'),
	# 	'riseTime':request.form.get('riseTime'),
	# 	'loopEnabled':request.form.get('loopEnabled'),
	# 	'loopCount':request.form.get('loopCount')
	# 	}


# Starts the selected dunk schedule.
# TODO:  Make this work after the webSaveSchedule method is up and running, for now it is a placeholder/test.
@app.route('/webStartSchedule')
def webStartSchedule():

	print ("Starting Schedule!");
	WindOut();
	sleep (1);
	WindIn();
	sleep (1);
	StopWind();

	isDunking = True;
	settings = GetSettingsData()
	state = settings['State']['isDunking']
	state['isDunking'] = isDunking;

	with open(settingsFilePath, 'w') as f:
		json.dump(settings, f, indent=3);

	return schedule();


# This is for the function that stops a scheduled dunk and resets the current schedule.
@app.route('/webStopDunk') 
def webStopDunk():
	print ("STOPPED DUNK");
 	StopWind();
 	WindOut();
 	sleep (1);
 	WindIn();
 	sleep (1);
	StopWind();

	isDunking = False;

	return noSchedule()

# This is for the function that stops the Winch from winding in or out.
@app.route('/webStopWind') 
def webStopWind():
	print ("STOP");
 	StopWind();
	return noSchedule()

# This is for the function that winds the Winch out.
@app.route('/webWindOut') 
def webWindOut():
	if not isDunking:
		print ("OUT");
 		WindOut();
	else:
		print ("NOT AVAILABLE, DUNKING IN PROGRESS");
	return noSchedule()

# This is for the function that winds the Winch in.
@app.route('/webWindIn') 
def webWindIn():
	if not isDunking:
		print ("IN");
	 	WindIn();
	else:
		print ("NOT AVAILABLE, DUNKING IN PROGRESS");
	return noSchedule()
	#render_template('index.html', **currentSchedule.getData())


# Runs the Flask server and website.
if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
