#!/usr/bin/env python
# Web/website Interface for the GPS Tag Dunker.
# Authored by TechDevTom/Tom Southworth, 2020, for The Arribada Initiative.

# Import libraries needed to run the code.
from flask import Flask, render_template
import datetime

# Create basic website.
app = Flask(__name__)

# This is the Main Page of the GPS Tag Dunker.
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
    app.run(debug=True, host='0.0.0.0')