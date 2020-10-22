#!/usr/bin/env python
# Relay winch code for the Turtle GPS Tag Dunker.
# Authored by TechDevTom/Tom Southworth, 2020, for The Arribada Initiative.

# Declare Variables
# Import libraries needed to run the code.
from time import sleep
import RPi.GPIO as GPIO
import sys
import tty
import termios

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


# The getchar method can determine which key has been pressed
# by the user on the keyboard by accessing the system files
# It will then return the pressed key as a variable
def getchar():

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


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


# Testing code,  use the keyboard to control the winch in and out actions.
while(True):

	char = getchar()
	if char == 'a':
		WindIn()

	if char == 'd':
		WindOut()

	if char == 's':
		StopWind()

	if char == 'x':
		break

	char = ''

print("DONE!")
GPIO.cleanup()
