from mido import MidiFile, MidiTrack, Message, merge_tracks
import numpy
import os
import cPickle as pickle
from multiprocessing.dummy import Pool as ThreadPool 

''' Note class '''

class Note():
	def __init__(self, pitch, duration, timestamp):
		self.pitches = []
		if (type(pitch) is int): #only one note
			self.pitches = [pitch]
		if (type(pitch) is list):
			self.pitches = pitch
		self.duration = duration
		self.timestamp = timestamp
	def __repr__(self):
		return "<note " + str(self.pitches) + " " + str(self.duration) + ">"
	def appendPitch(self, pitch):
		self.pitches.append(pitch)
	def transpose(self, offset):
		newpitches = []
		for p in self.pitches:
			newpitches.append(p - offset)
		self.pitches = newpitches
	# def toBinary(self):
	# 	zeros = [0 for x]

''' Song class '''
''' Stores notes '''

class Song():
	def __init__(self):
		self.key = False #initialize key as false
		self.notes = [] #initialize empty note array
	def getKey(self):
		return self.key
	def setKey(self, key):
		self.key = key
		return self.key
	def addNote(self, new_note):
		self.notes.append(new_note)
	def getNotes(self):
		return self.notes
	def transpose(self, offset):
		for note in self.notes:
			note.transpose(offset)
	def toMidi(self, fname):
		with MidiFile() as outfile:
			track = MidiTrack()
			outfile.tracks.append(track)
			track.append(Message('program_change', program=12))
			for note in self.getNotes():
				for pitch in note.pitches:
					track.append(Message('note_on', note=pitch, velocity=100, time=0))
				delta = note.duration
				for pitch in note.pitches:
					track.append(Message('note_off', note=pitch, velocity=100, time=delta))
					delta = 0
			outfile.save(fname)

''' Converter class '''
''' Converts a mido Midifile to a Song class '''

class Converter():
	def __init__(self):
		pass
		self.chordThreshold = 10
	def convert(self, mido_object):
		chord = False
		songz = []
		tick_convert = 480/mido_object.ticks_per_beat
		for track_num, track in enumerate(mido_object.tracks): #For each track
			s = Song()
			currenttime = 0;
			for i in xrange(0, len(track)): #For each note in the track
				message = track[i]
				secondtime = currenttime
				if self._isNoteOn(message): #if note_on
					if not message.channel == 9 or message.channel == 15: # if it's percussion
						pitch = message.note
						for y in xrange(i+1, len(track)): # Look ahead for the note_off event
							message2 = track[y]
							secondtime += message2.time
							if (message2.type == "note_off" or message2.type == "note_on"):
								if ((message2.type == "note_off" or message2.velocity == 0) and message2.note == pitch): # Found it
									break
						if i+1 <= len(track):
							if track[i+1].time <= self.chordThreshold:
								if self._isNoteOn(track[i+1]):
									c = Note([message.note, track[i+1].note], tick_convert*currenttime, tick_convert*(secondtime-currenttime))
									for j in xrange(0, 50):
										try:
											if self._isNoteOn(track[j+i]):
												if track[i+j].time <= self.chordThreshold:
													#it's a note on event and it's at the same time
													c.appendPitch(track[j+i].note) #add it's pitch to the chord
												else:
													break
										except IndexError, e:
											break
									chord = False
									# s.addNote(c)	
									c = None
						if not chord:
							duration = secondtime - currenttime
							timeStamp = currenttime
							pitch = track[i].note
							s.addNote(Note([pitch], tick_convert*duration, tick_convert*timeStamp))
							chord = False
				currenttime += message.time
			songz.append(s)
		return songz
	def _isNoteOn(self, event):
		return (event.type == "note_on" and event.velocity != 0 and event.type != "note_off")

				

class KeyPredicter():
	def __init__(self):
		self.scales = [[] for i in xrange(1, 13)]
		self.scaledict = {0: "C", 1: "C#", 2: "D", 3: "D#", 4: "E", 5: "F", 6: "F#", 7: "G", 8: "G#", 9: "A", 10: "A#", 11: "B"}
		self.MAJOR_OCTAVE = [0, 2, 4, 5, 7, 9, 11]
		for i in xrange(0, 12):
			self.scales[i] = self._offsetScale(self.MAJOR_OCTAVE, i)
		print "KeyPredicter object initialized."
	def _offsetScale(self, scale, offset):
		newscale=[]
		for i in scale:
			newscale.append((i+offset) % 12)
		return newscale
	def _notesFromNotes(self, note_array):
		notes = []
		for n in note_array:
			for p in n.pitches:
				notes.append(p)
		return notes
	def predict(self, song):
		array = self._notesFromNotes(song.notes)
		scores = [0 for q in xrange(0, 12)]
		modarray = []
		for j in array:
			modarray.append(j % 12)
		for i in xrange(0, 12):
			s = self.scales[i]
			scores[i] = 0
			for n in s:
				scores[i] += modarray.count(n)
		return scores.index(max(scores))


class Trie():
	def __init__(self):
		self.dict = {}
		self._end = "__end__"
	def addSongs(self, songs):
		root = dict()
		for song in songs:
			current_dict = root
			for x in song.getNotes():
				current_dict = current_dict.setdefault(x, {})
			current_dict[self._end] = self._end
		self.dict = root

class SongPickler():
	def __init__(self):
		print "Pickler initialized."
	def dump(self, song, file):
		data = []
		for note in song.getNotes():
			for pitch in note.pitches:
				data.append(pitch)
			data.append(254)
			for char in str(note.duration):
				data.append(ord(char))
			data.append(254)
			for char in str(note.timestamp):
				data.append(ord(char))
			data.append(255)
		file.write(bytearray(data))
		file.close()
	def read(self, fname):
		with open(fname) as f:
			song = Song()
			notes = f.read().split(chr(255))
			del notes[-1]
   			for line in notes:
   				pitches = []
   				for p in line.split(chr(254))[0]:
   					pitches.append(ord(p))
   				duration = int(line.split(chr(254))[1])
   				timestamp = int(line.split(chr(254))[2])
   				song.addNote(Note(pitches, duration, timestamp))
   		return song

def pickleSongs(folder, out_folder):
	c = Converter()
	kp = KeyPredicter()
	files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
	for fpath in files:
		with open(os.path.join(folder, fpath)) as file:
			if not file.read() == "":
				p = SongPickler()
				songs = c.convert(MidiFile(os.path.join(folder, fpath)))
				for j in xrange(0, len(songs)):
					f = open(os.path.join(out_folder, fpath+'.pkl'), 'w')
					songs[j].transpose(kp.predict(songs[j]))
					p.dump(songs[j], f)
				print files.index(fpath)
def main():
	# pool = ThreadPool(10) 
	# a = []
	pickleSongs("mozart midi", "mzrt-pkls")
		# a.append(i)
	# results = pool.map(pickleSongs, a)


if __name__ == '__main__':
	main()

