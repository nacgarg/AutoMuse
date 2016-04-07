import keras
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM
import random
import datetime
import time
import sys
import argparse
import numpy as np
import os
from progressbar import ProgressBar
from keras.utils.visualize_util import plot
from song import *

class AutoMuse():

    def __init__(self):
        self.notes = []
        self.maxlen = 20
        self.batchlen = 1000000000
        self.step = 3
        self.segments = []
        ts = time.time()
        self.weight_save_name = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S') + ".h5"
        self.next_notes = []

        print "AutoMuse initialized."

    def load_songs(self, num_files, folder="pkls"):
        sp = SongPickler()
        pkls = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        pbar = ProgressBar()
        if num_files:
            for pkl in pbar(pkls[:num_files]):
                song = sp.read(os.path.join(folder, pkl))
                self.notes.extend(song.notes)
        else:
            for pkl in pbar(pkls):
                song = sp.read(os.path.join(folder, pkl))
                self.notes.extend(song.notes)

    def train(self, iters):
        for iteration in range(1, iters):
            print('-' * 50)
            print('Iteration', iteration)
            for i, chunk in enumerate(self.note_chunks()):
                if (i % 1 == 0):
                    print ('***  Chunk ' + str(i))
                (X, y) = self.calculate_X_y(chunk)
                X = X[:np.size(X, 0)-(np.size(X, 0)%64)] # make sure it is divisible by 64
                y = y[:np.size(y, 0)-(np.size(y, 0)%64)] # make sure it is divisible by 64

                # loss = self.model.train_on_batch(X, y)
                # if (i % 100 == 0):
                #     print "Loss: " + str(loss)
                self.model.fit(X, y, nb_epoch=2, batch_size=64, verbose=1)
            self.save_weights()

    def train_FF(self, iters):
        for iteration in range(1, iters):
            print('-' * 50)
            print('Iteration', iteration)
            for i, chunk in enumerate(self.note_chunks()):
                if (i % 1 == 0):
                    print ('***  Chunk ' + str(i))
                (X, y) = self.calculate_X_y_FF(chunk)
                # loss = self.model.train_on_batch(X, y)
                # if (i % 100 == 0):
                #     print "Loss: " + str(loss)
                self.model.fit(X, y, nb_epoch=2, batch_size=64, verbose=1)
            self.save_weights()

    def generate(self, length=100, temperature=1.0, seed=None):
        if not seed:
            generated = [Note(60, 100, 100), Note(62, 100, 100), Note(64, 100, 100)]
        else:
            generated = seed
        for i in range(length):
            x = np.zeros((64, 3, 127), dtype=np.bool)
            for j in range(3):
                x[0, j, generated[-1-j].pitches[0]] = 1
            preds = self.model.predict(x, verbose=0)[0]
            next_index = self.sample(preds, temperature)
            print next_index
            if (next_index < 127 and next_index > 0):
                generated.append(Note([next_index], 100, 100))
        return generated[3:]

    def generate_FF(self, length=100, temperature=1.0):
        generated = [Note(60, 100, 100), Note(62, 100, 100), Note(64, 100, 100)]
        for i in range(length):
            x = np.zeros((1, 127*3), dtype=np.bool)
            for j in range(3):
                x[0, generated[-1-j].pitches[0]+(j*127)] = 1
            preds = self.model.predict(x, verbose=0)[0]
            next_index = self.sample(preds, temperature)
            print next_index
            if (next_index < 127 and next_index > 0):
                generated.append(Note([next_index], 100, 100))
        return generated

    def init_model(self, net_type):
        if net_type.lower() == "lstm":
            self.model = self.create_LSTM_model()
        if net_type.lower() == "ff":
            self.model = self.create_FF_model()
        print "initialized model"
        print "compiling..."
        self.model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

    def create_LSTM_model(self):
        model = Sequential()

        model.add(LSTM(127, return_sequences=True, stateful=True, batch_input_shape=(64, 3, 127)))
        model.add(Dropout(0.2))
        model.add(LSTM(512, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(127))
        model.add(Activation('softmax'))
        return model

    def create_FF_model(self):
        model = Sequential()

        model.add(Dense(127*3, input_shape=(127*3,)))
        # model.add(Dense(512))
        # model.add(Dropout(0.2))
        model.add(Dense(127))
        model.add(Activation("softmax"))
        return model

    def load_weights(self, fpath):
        self.model.load_weights(fpath)

    def save_weights(self):
        if not os.path.exists("saved_weights"):
            os.makedirs("saved_weights")
        self.model.save_weights("saved_weights/" + self.weight_save_name, overwrite=True)

    def save_output(self, generated, fname='output.mid'):
        outputSong = Song()
        for note in generated:
            outputSong.addNote(note)
        outputSong.toMidi(fname)

    def graph_net(self):
        plot(self.create_LSTM_model(), 'model.png')

    def calculate_indices(self):
        self.note_indices = dict((c, i) for i, c in enumerate(self.notes))
        self.indices_note = dict((i, c) for i, c in enumerate(self.notes))

    def calculate_segments(self, notes=None):
        self.segments = []
        if notes is None:
            notes = self.notes
        for i in range(0, len(notes) - self.maxlen, self.step):
            tmp = []
            for n in notes[i: i+self.maxlen]:
                tmp.append(n.pitches)
            self.segments.append(tmp)
            self.next_notes.append(notes[i+self.maxlen].pitches)
        print "total notes: " + str(len(notes))
        print "total segments: " + str(len(self.segments))

    def calculate_X_y(self, notes=None):
        if notes is None:
            notes = self.notes
        X = np.zeros([len(notes), 3, 127], dtype=np.bool)
        y = np.zeros([len(notes), 127], dtype=np.bool)
        for i, note in enumerate(notes):
            if (i+1 < len(notes) and i-2 >= 0 and notes[i+1] < 127):
                for j in xrange(0, 3):
                    for p in notes[i-j].pitches:
                        X[i, j, p] = 1
                for p in notes[i+1].pitches:
                        y[i, p] = 1
        return (X, y)

    def calculate_X_y_FF(self, notes=None):
        if notes is None:
            notes = self.notes
        X = np.zeros([len(notes), 127*3], dtype=np.bool)
        y = np.zeros([len(notes), 127], dtype=np.bool)
        for i, note in enumerate(notes):
            if (i+1 < len(notes) and i-2 >= 0 and notes[i+1] < 127):
                for j in range(0, 3):
                    for p in notes[i-j].pitches:
                        X[i, p+(j*127)] = 1
                for p in notes[i+1].pitches:
                        y[i, p] = 1
        return (X, y)
    def sample(self, a, temperature=1.0): #TODO Allow for chords
        # helper function to sample an index from a probability array
        print a
        print np.sum(a)
        # return np.random.choice(range(0, 127), p=a)
        a = np.log(a) / temperature
        a = np.exp(a) / np.sum(np.exp(a))
        return np.argmax(np.random.multinomial(1, a, 1))
        print a
        return list(a).index(max(a))

    def note_chunks(self, array=None, n=None):
        if array is None:
            array = self.notes
        if n is None:
            n = self.batchlen

        for i in xrange(0, len(array), n):
            yield array[i:i+n]  

