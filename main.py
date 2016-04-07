from song import *
from nn import AutoMuse
from mido import MidiFile
import argparse
from progressbar import ProgressBar
import sys
pbar = ProgressBar()

parser = argparse.ArgumentParser(description='Train or generate songs.')
parser.add_argument("-t", "--train", help="train the net on the pkls folder", action='store_true')
parser.add_argument("-w", "--load-weights", nargs='?', help="load model weights from specified h5 file", default=None)
parser.add_argument("-l", "--length", nargs='?', help="number of notes in output", default=50)
parser.add_argument("-d", "--temp", nargs='?', help="temperature of sampling", default=1.0)
parser.add_argument("-T", "--type", nargs='?', help="LSTM vs FF, default is LSTM", default="lstm")
parser.add_argument("-n", "--num-files", nargs='?', help="Number of files to train from. default is all", default=None)
parser.add_argument("-o", "--output", nargs='?', help="output fpath", default="output.mid")
# parser.add_argument("-e", "--output", nargs='?', help="output fpath", default="output.mid")


args = parser.parse_args()

a = AutoMuse()
if args.train:
    print "Loading songs..."
    a.load_songs(int(args.num_files), "pkls")

# c = Converter()
# kp = KeyPredicter()
# for i in pbar(xrange(0, 4499)):
#     with open('./downloaded-midi/'+str(i)+'.mid') as file:
#         if file.read() != "":
#             try:
#                 midifile = MidiFile('./downloaded-midi/'+str(i)+'.mid')
#             except Exception, e:
#                continue
#             midifile = MidiFile('./downloaded-midi/'+str(i)+'.mid')
#             songs = c.convert(midifile)
#             for song in songs:
#                 song.transpose(kp.predict(song))
#                 notes.extend(song.notes)

a.init_model(args.type)



if args.train:
    print "Training net."
    if args.type == "ff":
        a.train_FF(50)
    else:
        a.train(50)

elif args.load_weights != None:
    "Loading weights from " + args.load_weights
    a.load_weights(args.load_weights)

else:
    print "Please provide the -t flag to train or load weights with the -w flag."
    sys.exit()

print "Generating."
if args.type == "ff":
    a.save_output(a.generate_FF(int(args.length), float(args.temp)), args.output)
else:
    a.save_output(a.generate(int(args.length), float(args.temp)), args.output)
