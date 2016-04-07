var app = new App()

app.start()

var slider = document.getElementById('slider');

noUiSlider.create(slider, {
	start: [1],
	range: {
		'min': 0,
		'max': 2
	}
})

slider.noUiSlider.on('update', function( values, handle ) {
	document.getElementById('temp').innerHTML = values;
});
// var visualizer = new Visualizer(document.getElementById("canvas"))

// p = new Player(visualizer)

// console.log(p.synth)

// p.playBuffer([
//     { pitches: [60], duration: 300 },
//     { pitches: [64], duration: 300 },
//     { pitches: [67], duration: 300 },
//     { pitches: [71], duration: 300 },
//     { pitches: [69], duration: 300 },
//     { pitches: [67], duration: 300 },
//     { pitches: [64], duration: 300 },
//     { pitches: [60], duration: 300 },
//     { pitches: [62], duration: 300 },
//     { pitches: [65], duration: 300 },
//     { pitches: [69], duration: 300 },
//     { pitches: [72], duration: 300 },
//     { pitches: [71], duration: 1200 },
//     { pitches: [60], duration: 300 },
//     { pitches: [64], duration: 300 },
//     { pitches: [67], duration: 300 },
//     { pitches: [71], duration: 300 },
//     { pitches: [69], duration: 300 },
//     { pitches: [67], duration: 300 },
//     { pitches: [64], duration: 300 },
//     { pitches: [60], duration: 300 },
//     { pitches: [62], duration: 300 },
//     { pitches: [65], duration: 300 },
//     { pitches: [69], duration: 300 },
//     { pitches: [72], duration: 300 },
//     { pitches: [71], duration: 1200 }
// ])

// p.playBuffer([
//     { pitches: [], duration: 9000 },
//     { pitches: [79], duration: 300 },
//     { pitches: [81], duration: 300 },
//     { pitches: [83], duration: 300 },
//     { pitches: [81], duration: 2100 },
//     { pitches: [83], duration: 300 },
//     { pitches: [83], duration: 300 },
//     { pitches: [81], duration: 300 },
//     { pitches: [83], duration: 1300 },
// ])

