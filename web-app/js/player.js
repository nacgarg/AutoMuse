var Player = function(v) {
    this.context = new AudioContext;
    this.synth = new Synth(this.context);
    this.visualizer = v
    this.timeStarted = Date.now()
    this.buf = []
}

Player.prototype.playBuffer = function(buf) {
	this.timeStarted = Date.now()
	this.buf = buf;
	var that = this;
    (function nextNote(i, buffer, s, v) {
        setTimeout.call({buffer: buffer, synth: s, visualizer: v}, function() {
        	console.log(i)
        	this.visualizer.noteEvent(this.buffer[i])
            this.synth.playNote(this.buffer[i]);
            if (++i < this.buffer.length) nextNote(i, this.buffer, this.synth, this.visualizer);
        }, (buffer[i-1] || {duration: 0}).duration)
    })(0, buf, this.synth, this.visualizer);
}

Player.prototype.timeLeft = function(n) {
	return this._getBufferLength(n) - (Date.now() - this.timeStarted)
}

Player.prototype._getBufferLength = function(n) {
    var sum = 0
	n.forEach(function(e){
        sum += e.duration
    });
    return sum;
};


function Synth(context) {
    this.context = context;
}

Synth.prototype.playNote = function(n) {
    context = this.context
    n.osc = []
    n.vca = []
    for (var i = 0; i < n.pitches.length; i++) {
        n.osc.push(context.createOscillator());
        n.osc[i].type = "square"
        n.osc[i].frequency.value = this._noteToFreq(n.pitches[i] + 12);
        n.vca.push(context.createGain());
        n.vca[i].gain.value = 0.3;
        n.osc[i].connect(n.vca[i]);
        n.vca[i].connect(context.destination);
        n.osc[i].start(0);
    }

    console.log(n)


    setTimeout.call(n, function(n) {
        for (var i = 0; i < this.osc.length; i++) {
            this.vca[i].gain.value = 0;
        }
    }, n.duration)


}
Synth.prototype._noteToFreq = function(n) {
    return Math.pow(2, ((n - 69) / 12)) * 440
}
