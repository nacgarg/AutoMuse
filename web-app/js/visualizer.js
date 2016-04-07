var Visualizer = function(canvas) {
    this.context = canvas.getContext("2d");
    this.context.fillStyle = "#000000"
    this.rects = []
    setInterval.call(this, this.tick, 10)
}

Visualizer.prototype.noteEvent = function(n) {
    for (var i = 0; i < n.pitches.length; i++) {
        this.rects.push(new Rectangle({ pitch: n.pitches[i], duration: n.duration }, this.context))
    }
}

Visualizer.prototype.tick = function() {
    this.context.clearRect(0, 0, this.context.canvas.width, this.context.canvas.height);
    this.context.beginPath();
    for (var i = 0; i < this.rects.length; i++) {
        this.rects[i].draw()
        this.rects[i].offset -= 10
    }
}

var Rectangle = function(n, ctx) {
    this.context = ctx
    this.xunit = this.context.canvas.width / 10000
    this.offset = this.context.canvas.width * 10
    this.height = this.context.canvas.height - ((this.context.canvas.height / 87) * (n.pitch - 20))
    this.duration = this.xunit * n.duration
    this.width = this.context.canvas.height / 127
}

Rectangle.prototype.draw = function() {
	if ((this.offset * this.xunit) + this.duration > (this.context.canvas.width)) {
		this.context.fillStyle = "#F57C00"
		this.context.arc(this.context.canvas.width, this.height + (this.width/2), 10, 0, 2 * Math.PI, false);
		this.context.fill()
		this.context.fillStyle = "#000000"
	}
    x = this.offset * this.xunit
    y = this.height
    duration = this.duration
    this.context.fillRect(x, y, duration, this.width);
}
