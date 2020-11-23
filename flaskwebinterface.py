#!/usr/bin/env python
# Web/website Interface for the GPS Tag Dunker.
# Authored by TechDevTom/Tom Southworth, 2020, for The Arribada Initiative.

# LIBRARY IMPORTING
import os
from datetime import datetime, timedelta
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
isActive = False

# The five states that the tag dunker can be in.
dunkStates = ('dunking', 'dunked', 'rising', 'risen', 'idle')

# The state that the tag dunker is currently in.
dunkState = ''

# Declares an empty Schedule ready to be populated by JSON info.
currentSchedule = Schedule('', '', '', '', '', '' ,'')

# The time it takes to dunk a tag
tagDunkWindTime = datetime.strptime ('03.00', '%S.%f')

#The time it takes to raise a tag
tagRiseWindTime = datetime.strptime ('03.25', '%S.%f')

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
	global isActive
	isActive = settings['State']['isActive']

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
def SaveSchedule(scheduleData):

	global isActive
	global currentSchedule

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
	# savedSchedules = settings['SavedSchedules']

	# if not CheckScheduleExists(scheduleData):
	# 	savedSchedules.append(scheduleData)

	# Set the isActive value to true for reference.
	isActive = True

	# Set the settings' isActive State field to True.
	settings['State']['isActive'] = isActive;

	# Save new settings data into json file.
	with open(settingsFilePath, 'w') as f:
		json.dump(settings, f, indent=4);

 	# Refresh Schedule and settings JSON DATA.
	RefreshSchedule();

	# # Run the Schedule
	# loopCount = int(currentSchedule['loopCount'])
	# print ('Scheduled dunk will end at:  ' + currentSchedule['finishTime'])

	# if currentSchedule['loopEnabled'] == 'on':
	# 	print ('Starting looped dunk:  ' + str(loopCount) + ', ' + currentSchedule['loopEnabled']);
	# 	if loopCount > 0:
	# 		for i in range(loopCount):
	# 			# Wind the tag up and down until the loop count is complete
	# 			WindOutTimed (3, datetime.strptime(currentSchedule['dunkTime'], '%H:%M:%S').time());
	# 			WindInTimed (3.5, datetime.strptime(currentSchedule['riseTime'], '%H:%M:%S').time());
	# 	 		print ('Loop ' + str(i+1) + ' completed.');
	# 	# else:
	# 	# 	# Infinitely Loop

	# else:
	# 	print ('Starting one off dunk:  ' + str(loopCount) + ', ' + currentSchedule['loopEnabled']);
	# 	# Wind the tag up and down once.
	# 	WindOutTimed (3, datetime.strptime(currentSchedule['dunkTime'], '%H:%M:%S').time());
	# 	WindInTimed (3, datetime.strptime(currentSchedule['riseTime'], '%H:%M:%S').time());

	# print ('Scheduled Dunk Finished');


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


# Retrieves and saves the FinishTime for the currentSchedule.
def RefreshStartFinishTimes():

	finishTime 	= datetime.strptime(str(datetime.min), '%Y-%m-%d %H:%M:%S')
	loopCount 	= int(currentSchedule.loopCount)

	# Set up initial dunkTime and riseTime values for parsing into datetime.time values.
	initialDunkTime = currentSchedule.dunkTime
	initialRiseTime = currentSchedule.riseTime

	# Check to see if any seconds exist on the time.  Add them if not present.
	if len(str(initialDunkTime)) < 6:
		initialDunkTime = initialDunkTime + ':00'

	if len(str(initialRiseTime)) < 6:
		initialRiseTime = initialRiseTime + ':00'

	# Convert stored dunkTime and riseTime to datetime values
	dunkTime 	= datetime.combine (datetime.min, datetime.strptime(initialDunkTime, '%H:%M:%S').time()) - datetime.min
	riseTime 	= datetime.combine (datetime.min, datetime.strptime(initialRiseTime, '%H:%M:%S').time()) - datetime.min
	tagDWT 		= datetime.combine (datetime.min, tagDunkWindTime.time()) - datetime.min
	tagRWT 		= datetime.combine (datetime.min, tagRiseWindTime.time()) - datetime.min

	# Set the new start time for the currentSchedule.
	currentSchedule.startTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	# Calculate the total time that the tag spends dunked and raised.
	dunkRiseTotalTime = dunkTime + riseTime + tagDWT + tagRWT

	# Calculate overall finish time based on whether the schedule loops or not.
	if currentSchedule.loopEnabled == 'true':

		# Infinitely loops, no finish time.
		if loopCount < 0:
			finishTime = datetime.strptime(str(datetime.max), '%Y-%m-%d %H:%M:%S')

		# Has a set loop count.
		elif loopCount > 0:
			for i in range(loopCount - 1):
				dunkRiseTotalTime = dunkRiseTotalTime + dunkTime + riseTime + tagDWT + tagRWT

			finishTime = datetime.strptime(currentSchedule.startTime, '%Y-%m-%d %H:%M:%S') + dunkRiseTotalTime

	# No loops involved.
	else:
		finishTime = datetime.strptime(currentSchedule.startTime, '%Y-%m-%d %H:%M:%S') + dunkRiseTotalTime

	# Set the new finish time for the currentSchedule.
	currentSchedule.finishTime = str(finishTime)

	# Retrieve the settings and save the new finish time for the currentSchedule.
	settings = GetSettingsData()
	settings['CurrentSchedule']['startTime'] 	= currentSchedule.startTime;
	settings['CurrentSchedule']['finishTime'] 	= currentSchedule.finishTime;

	# Save new settings data into json file.
	with open(settingsFilePath, 'w') as f:
		json.dump(settings, f, indent=4);

	print (currentSchedule.finishTime);


# Returns the time that is now with the given plusTime added to it.
def GetTimeNowPlus (plusTime, hasDate):

	finalDateTime 	= datetime.now()
	timeToAdd 		= datetime.combine (datetime.min, datetime.strptime(plusTime, '%H:%M:%S').time()) - datetime.min
	finalDateTime = datetime.strptime(originalTime, '%Y-%m-%d %H:%M:%S.%f')

	return finalDateTime + timeToAdd;



# Carries out the Dunk Schedule
def DunkRoutine():

	print ('Starting Routine');

	RefreshStartFinishTimes();
	finishTime 	= datetime.strptime(currentSchedule.finishTime, '%Y-%m-%d %H:%M:%S.%f')
	riseTime 	= datetime.strptime(currentSchedule.riseTime, '%H:%M:%S')
	dunkTime 	= datetime.strptime(currentSchedule.dunkTime, '%H:%M:%S')
	loopCount 	= int(currentSchedule.loopCount)

	print ('Finish Time:  ' + str(finishTime))
	loopCounter = 0

	while (datetime.now() < finishTime and isActive):

		print ('Starting Loop ' + str(loopCounter+1));

		# Wind Out Section, cannot be interrupted.
		dunkState = dunkStates[0]
		waitTime = GetTimeNowPlus(tagDunkWindTime)
		WindOut();
		sleep (tagDunkWindTime.second);
		StopWind();
		dunkState = dunkStates[1]

		# Check to see if user has cancelled schedule.
		if !isActive:
			continue;

		# Dunking Section, can be interrupted for cancellation/new schedule.
		waitTime = GetTimeNowPlus(dunkTime)
		while (datetime.now() < waitTime and isActive):
			print ('Is Active:  ' + str(isActive))
			sleep(1)

		# Check to see if user has cancelled schedule.
		if !isActive:
			continue;
		#sleep((dunkTime.hour * 60 + dunkTime.minute) * 60 + dunkTime.second)

		# Wind In Section, cannot be interrupted.
		dunkState = dunkStates[2]
		waitTime = GetTimeNowPlus(tagRiseWindTime)
		WindIn()
		sleep (tagRiseWindTime.second);
		StopWind()
		dunkState = dunkStates[3]

		# Check to see if user has cancelled schedule.
		if !isActive:
			continue;

		# Raised Section, can be interrupted for cancellation/new schedule.
		waitTime = GetTimeNowPlus(riseTime)
		while (datetime.now() < waitTime and isActive):
			print ('Is Active:  ' + str(isActive))
			sleep(1)

		# Check to see if user has cancelled schedule.
		if !isActive:
			continue;
		#sleep((riseTime.hour * 60 + riseTime.minute) * 60 + riseTime.second)

		# Add a new loop to the loopCounter.
		loopCounter += 1

		# Set the Dunk State to idle.
		dunkState = dunkStates[4]
		if isActive:
			print ('Schedule Finished Automatically, ready for new schedule.')

		else:
			print ('Schedule was cancelled by the user, ready for new schedule.')
			
			# Wind Tag Up after cancelled operation.
			if dunkState == dunkStates[1]:
				waitTime = GetTimeNowPlus(tagDunkWindTime)
				WindIn();
				sleep (tagRiseWindTime.second);
				StopWind();

	return noSchedule();


# WEBSITE CREATION
# Initialise the web app.
app = Flask(__name__)

# The index method determines which page to load based on whether the tag dunker is dunking or not.
@app.route('/')
def index():

	print ('Index Triggered, isActive:  ' + str(isActive));


# This is the page that is presented when a schedule is not running.
@app.route('/NoSchedule')
def noSchedule():

	return render_template('noschedule.html', Schedules=GetSavedSchedules())


# This is the page that is presented when scheduled dunk is running.
# TODO:  Sort out data string as it's a mess, need better formatting.
@app.route('/Schedule')
def schedule():

	return render_template('schedule.html', Schedule=currentSchedule.getData())


# Saves and Starts a dunk Schedule based on user input from the new Schedule web form.
@app.route('/webViewSchedule', methods=['GET'])
def webViewSchedule():

	print ('Attempting to save and start schedule!');

	# Set scheduleData fields from the retrieved form data.
	# 'startTime' and 'finishTime' are set from Python.
	startTime 	= datetime.now()

	scheduleData = {'name':str(request.args.get('scheduleName')),
		'startTime':startTime.strftime('%Y-%m-%d %H:%M:%S'),
		'dunkTime':str(request.args.get('dunkTime')),
		'riseTime':str(request.args.get('riseTime')),
		'loopEnabled':str(request.args.get('loopEnabled')),
		'loopCount':str(request.args.get('loopCount'))
		}

	print ('Schedule Data:  ' + scheduleData['name']);

	finishTime 	= datetime.strptime(str(datetime.min), '%Y-%m-%d %H:%M:%S')
	scheduleData['finishTime'] = str(finishTime)
	SaveSchedule(scheduleData);

	return schedule();


@app.route('/webStartDunk')
def webStartDunk():

	global isActive
	isActive = True;
	dunkingRoutine.__next__()

	return schedule();


# This is for the function that stops a scheduled dunk and resets the current schedule.
@app.route('/webStopDunk') 
def webStopDunk():

	global isActive

	StopWind();
	WindOut();
	sleep (0.2);
	WindIn();
	sleep (0.2);
	StopWind();

	isActive = False;
	print ("STOPPED DUNK");

	dunkingRoutine.close();

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

	if not isActive:
		print ("OUT");
		WindOut();
	else:
		print ("NOT AVAILABLE, DUNKING IN PROGRESS");
	return noSchedule()

# This is for the function that winds the Winch in.
@app.route('/webWindIn') 
def webWindIn():

	if not isActive:
		print ("IN");
		WindIn();
	else:
		print ("NOT AVAILABLE, DUNKING IN PROGRESS");
	return noSchedule()
	#render_template('index.html', **currentSchedule.getData())


# Runs the Flask server and website.
if __name__ == '__main__':
	app.run(debug=True, port=80, host='0.0.0.0')
