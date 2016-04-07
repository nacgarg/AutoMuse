from flask import Flask, render_template, send_from_directory
app = Flask(__name__, static_url_path='', template_folder="")
import random
import imp
import json
from flask import request

song = imp.load_source('song', '../song.py')

nn = imp.load_source('nn', '../nn.py')

import time

@app.route("/")
def root():
    return render_template("index.html", title = 'sdf')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/note/20')
def send_notes():
	temp = float(request.args.get('temp'))
	return generate(temp)

def notes_to_JSON(g):
	n = []
	for note in g:
		d = {}
		d["pitches"] = note.pitches
		d["duration"] = note.duration
		n.append(d)
	return json.dumps(n)

def generate(temp):
	global seed
	g = a.generate(20, temp, seed)
	seed = g[-3:]
	return notes_to_JSON(g)
if __name__ == "__main__":
	a = nn.AutoMuse()
	a.init_model("lstm")
	a.load_weights("../mzrt.h5")
	seed = None
	app.run('0.0.0.0', 8000, debug=True)