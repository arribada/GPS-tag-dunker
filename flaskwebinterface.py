#!/usr/bin/env python
# Web/website Interface for the GPS Tag Dunker.
# Authored by TechDevTom/Tom Southworth, 2020, for The Arribada Initiative.

# LIBRARY IMPORTING
import os
from datetime import datetime, timedelta
import pause
import json
import RPi.GPIO as GPIO
from time import sleep
from flask import Flask, render_template, request


# NOTES:  DateTime conversion: "date_time_obj = datetime.strptime(date_time_str, %H:%M:%S')"


# CLASSES CODE
# Define the Schedule Class
class Schedule:
    """The class which holds Schedule data"""

    def __init__(self, name, startTime, finishTime, dunkTime, riseTime, loopEnabled, loopCount):
        """Initialise the Schedule's attributes"""
        self.name 			= name
        self.startTime		= startTime
        self.finishTime		= finishTime
        self.dunkTime      	= dunkTime
        self.riseTime    	= riseTime
        self.loopEnabled  	= loopEnabled
        self.loopCount  	= loopCount

    def getData(self):
        """Returns this Schedule's Info"""
        return {
        'name':self.name,
		'startTime':self.startTime,
		'finishTime':self.finishTime,
		'dunkTime':self.dunkTime,
		'riseTime':self.riseTime,
		'loopEnabled':self.loopEnabled,
		'loopCount':self.loopCount
		}

    def updateScheduleInfo(self, name, startTime, finishTime, dunkTime, riseTime, loopEnabled, loopCount):
        """Updates this Schedule's information"""
        self.name 			= name
        self.startTime		= startTime
        self.startTime		= finishTime
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
currentSchedule = Schedule('', '', '', '', '', '' ,'')

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


# SETTINGS & SCHEDULE CODE
# Loads in the Settings data from the settings.json file.
def GetSettingsData():

	with open(settingsFilePath, "r") as file_object:
		settings = json.load(file_object);
		return settings;


# Returns the schedules that have been saved into the settings.json file.
def GetSavedSchedules():

	return GetSettingsData()['SavedSchedules'];


# Refreshes the dunking state and CurrentSchedule data.
def RefreshSchedule():

	# Retrieve the settings
	settings = GetSettingsData();

	# Assign GPS Tag Dunker state info.
	global isDunking
	isDunking = settings['State']['isDunking']

	# Load in the current schedule's information.
	global currentSchedule
	currentSchedule = Schedule(settings['CurrentSchedule']['name'],
		settings['CurrentSchedule']['startTime'],
		settings['CurrentSchedule']['finishTime'],
		settings['CurrentSchedule']['dunkTime'],
		settings['CurrentSchedule']['riseTime'],
		settings['CurrentSchedule']['loopEnabled'],
		settings['CurrentSchedule']['loopCount'])

# Load the Settings right at the start.
RefreshSchedule();


# Saves the given json data to the settings.json file's list of Saved Schedules.
def SaveAndStartSchedule(scheduleData):

	# Retrieve the settings
	settings = GetSettingsData()

	# Set the Current Schedule to reflect the schedule data that the user has entered.
	currentSchedule 				= settings['CurrentSchedule']
	currentSchedule['name'] 		= scheduleData['name']
	currentSchedule['startTime'] 	= scheduleData['startTime']
	currentSchedule['finishTime'] 	= scheduleData['finishTime']
	currentSchedule['dunkTime'] 	= scheduleData['dunkTime']
	currentSchedule['riseTime'] 	= scheduleData['riseTime']
	currentSchedule['loopEnabled'] 	= scheduleData['loopEnabled']
	currentSchedule['loopCount'] 	= scheduleData['loopCount']

	# Load in the SavedSchdules list and append the new Schedule
	# TODO:  Need to insert check to see if all parameters for new Schedule already exist.
	savedSchedules = settings['SavedSchedules']

	if not CheckScheduleExists(scheduleData):
		savedSchedules.append(scheduleData)

	# Set the isDunking value to true for reference.
	isDunking = True

	# Set the settings' isDunking State field to True.
	settings['State']['isDunking'] = isDunking;

	# Save new settings data into json file.
	with open(settingsFilePath, 'w') as f:
		json.dump(settings, f, indent=4);

 	# Refresh Schedule and settings JSON DATA.
	RefreshSchedule();

	# Run the Schedule
	loopCount = int(currentSchedule['loopCount'])
	print ('Scheduled dunk will end at:  ' + currentSchedule['finishTime'])

	if currentSchedule['loopEnabled'] == 'true':
		print ('Starting looped dunk:  ' + str(loopCount) + ', ' + currentSchedule['loopEnabled']);
		if loopCount > 0:
			for i in range(loopCount):
				# Wind the tag up and down until the loop count is complete
				WindInTimed (3, datetime.strptime(currentSchedule['dunkTime'], '%H:%M:%S').time());
				WindInTimed (3, datetime.strptime(currentSchedule['riseTime'], '%H:%M:%S').time());
		# 		print ('Loop ' + str(i) + ' completed.');
		# else:
		# 	# Infinitely Loop

	else:
		print ('Starting one off dunk:  ' + str(loopCount) + ', ' + currentSchedule['loopEnabled']);
		# Wind the tag up and down once.
		WindInTimed (3, datetime.strptime(currentSchedule['dunkTime'], '%H:%M:%S').time());
		print ('Loop ' + str(i) + ' completed.');
		WindInTimed (3, datetime.strptime(currentSchedule['riseTime'], '%H:%M:%S').time());

	print ('Scheduled Dunk Finished');


def CheckScheduleExists(scheduleToCheck):

	scheduleFound = False
	for schedule in GetSavedSchedules():
		print ("Schedule Name:  " + schedule['name'])
		if schedule['name'] == scheduleToCheck['name']:
			print ('A schedule with that name already exists!');
			scheduleFound = True

	if scheduleFound == False:
		print ('No schedule with a matching name has been found.  Saving new schedule...');

	return scheduleFound;


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

# Winds the Tag up for windInTime, then waits for riseTime.
def WindInTimed(windInTime, riseTime):

	# Wind the tag out of the water, and wait the required riseTime.
	WindIn()
	sleep (3) # TODO: Replace 3 with time it takes to wind tag out of water, depth dependant!
	StopWind()
	pause.seconds((riseTime.hour * 60 + riseTime.minute) * 60 + riseTime.second);


# Winds the Tag up for windOutTime, then waits for dunkTime.
def WindOutTimed(windOutTime, dunkTime):

	# Wind the tag down into the water, and wait the required dunkTime.
	WindOut();
	sleep (3); # TODO: Replace 3 with time it takes to wind tag under water, depth dependant!
	StopWind();
	pause.seconds((dunkTime.hour * 60 + dunkTime.minute) * 60 + dunkTime.second);


# WEBSITE CREATION
# Initialise the web app.
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
	scheduleString = "There is no scheduled dunk occurring.  Starting a schedule will automatically save it.";
	testingString = ('Testing is available.');
	schedules = GetSavedSchedules()
	return render_template('noschedule.html', scheduleInfo=scheduleString, testingInfo=testingString, Schedules=schedules)


# This is the page that is presented when scheduled dunk is running.
# TODO:  Sort out data string as it's a mess, need better formatting.
@app.route('/Schedule')
def schedule():

	settings = GetSettingsData();

	scheduleData 	= currentSchedule.getData()
	name 			= 'Name:  ' + scheduleData['name']
	startTime 		= 'Start Time:  ' + scheduleData['startTime']
	finishTime 		= 'Finish Time:  ' + scheduleData['finishTime']

	testingString 	= ('Testing is not available while a scheduled dunk is ongoing.  Press stop to stop current scheduled dunk and start a new one.')
	templateData 	= {'name':name, 'startTime':startTime, 'finishTime':finishTime, 'TestingString':testingString}
	return render_template('schedule.html', **templateData)


# Saves and Starts a dunk Schedule based on user input from the new Schedule web form.
@app.route('/webStartSchedule', methods=['GET'])
def webStartSchedule():

	print ('Attempting to save and start schedule!');

	# Set scheduleData fields from the retrieved form data.
	# 'startTime' and 'finishTime' are set from Python.
	startTime 	= datetime.now()

	scheduleData = {'name':str(request.args.get('scheduleName')),
		'startTime':startTime.strftime('%Y-%m-%d %H:%M:%S'),
		'dunkTime':str(request.args.get('dunkTime')),
		'riseTime':str(request.args.get('riseTime')),
		'loopEnabled':str('true' if request.args.get('loopEnabled') == 'on' else 'false'),
		'loopCount':str(request.args.get('loopCount'))
		}

	print ('Schedule Data:  ' + scheduleData['name']);

	finishTime 	= datetime.strptime(str(datetime.min), '%Y-%m-%d %H:%M:%S')
	loopCount 	= int(scheduleData['loopCount'])
	if scheduleData['loopEnabled'] == 'true':

		if loopCount < 0:
			finishTime = datetime.strptime(str(datetime.max), '%Y-%m-%d %H:%M:%S')

		elif loopCount > 0:

			# Set up initial dunkTime and riseTime values for parsing into datetime.time values.
			initialDunkTime = scheduleData['dunkTime']
			initialRiseTime = scheduleData['riseTime']

			# Check to see if any seconds exist on the time.  Add them if not present.
			if len(str(initialDunkTime)) < 6:
				initialDunkTime = initialDunkTime + ':00'

			if len(str(initialRiseTime)) < 6:
				initialRiseTime = initialRiseTime + ':00'

			# Convert stored dunkTime and riseTime to datetime values
			dunkTime = datetime.combine (datetime.min, datetime.strptime(initialDunkTime, '%H:%M:%S').time()) - datetime.min
			riseTime = datetime.combine (datetime.min, datetime.strptime(initialRiseTime, '%H:%M:%S').time()) - datetime.min

			dunkRiseTotalTime = dunkTime + riseTime
			for i in range(loopCount - 1):
				dunkRiseTotalTime = dunkRiseTotalTime + dunkTime + riseTime

			finishTime = datetime.strptime(scheduleData['startTime'], '%Y-%m-%d %H:%M:%S') + dunkRiseTotalTime

	scheduleData['finishTime'] = str(finishTime)
	SaveAndStartSchedule(scheduleData);

	# Finish by sending the user to the web page where it shows the current schedule.
	return schedule();


# This is for the function that stops a scheduled dunk and resets the current schedule.
@app.route('/webStopDunk') 
def webStopDunk():
 	StopWind();
 	WindOut();
 	sleep (0.2);
 	WindIn();
 	sleep (0.2);
	StopWind();

	isDunking = False;
	print ("STOPPED DUNK");

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
