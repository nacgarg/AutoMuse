var App = function() {
    this.visualizer = new Visualizer(document.getElementById("canvas"))
    this.player = new Player(this.visualizer)
    this.loader = new Loader(this.player)
}

App.prototype.start = function() {
    var that = this
	this.loader.requestNotes(20, function(notes) {
		that.loader.playBuffer = notes;
		that.loader.loop(0)
	}) //initial notes
}


// Enable the passage of the 'this' object through the JavaScript timers

var __nativeST__ = window.setTimeout,
    __nativeSI__ = window.setInterval;

window.setTimeout = function(vCallback, nDelay /*, argumentToPass1, argumentToPass2, etc. */ ) {
    var oThis = this,
        aArgs = Array.prototype.slice.call(arguments, 2);
    return __nativeST__(vCallback instanceof Function ? function() {
        vCallback.apply(oThis, aArgs);
    } : vCallback, nDelay);
};


window.setInterval = function(vCallback, nDelay /*, argumentToPass1, argumentToPass2, etc. */ ) {
    var oThis = this,
        aArgs = Array.prototype.slice.call(arguments, 2);
    return __nativeSI__(vCallback instanceof Function ? function() {
        vCallback.apply(oThis, aArgs);
    } : vCallback, nDelay);
};
