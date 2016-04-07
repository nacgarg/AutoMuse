var Loader = function(player) {
    this.playBuffer = []
    this.player = player
};

Loader.prototype.requestNotes = function(len, cb) {
    var req = new XMLHttpRequest();
    req.addEventListener("load", function() {
        cb(JSON.parse(req.responseText).map(function(e){
            e.duration = e.duration * 2;
            return e;
        }));
    });
    req.open("GET", "/note/" + len + "?temp=" + document.getElementById('temp').innerHTML || "1.0", true);
    req.send();
};

Loader.prototype.loop = function(i, that) {
	if (i == 0) {
		that = this
	}
    that.requestNotes(20, function(notes) {
        that.playBuffer = notes;
        setTimeout.call({ player: that.player, loop: that.loop, playBuffer: that.playBuffer }, function() {
            this.player.playBuffer(this.playBuffer);
            this.loop(++i, that)
        }, that.player.timeLeft(that.player.buf))
    });

};
