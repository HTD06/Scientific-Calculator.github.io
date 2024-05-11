function backspace() {
	let display = document.getElementById("display");
	display.value = display.value.slice(0, -1);
}

function calculate() {
	let display = document.getElementById("display");
	let expression = display.value;
	let result;

	try {
		// Convert trigonometric function inputs from degrees to radians
		expression = expression.replace(/sin\(/g, 'sin(' + Math.PI / 180 + '*');
		expression = expression.replace(/cos\(/g, 'cos(' + Math.PI / 180 + '*');
		expression = expression.replace(/tan\(/g, 'tan(' + Math.PI / 180 + '*');

		result = math.evaluate(expression);
		display.value = result;
	} catch (error) {
		display.value = "Error";
	}
}

function squareRoot() {
	let display = document.getElementById("display");
	display.value += "sqrt(";
}

function base10Log() {
	let display = document.getElementById("display");
	display.value += "log(";
}

function pi() {
	let display = document.getElementById("display");
	display.value += "pi";
}

function e() {
	let display = document.getElementById("display");
	display.value += "e";
}

function power() {
	let display = document.getElementById("display");
	display.value += "^(";
}

const express = require('express');
const app = express();
const path = require('path');

app.use(express.static(path.join(__dirname, 'static')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'static', 'index.html'));
});

app.listen(3000, () => {
  console.log('Server started on port 3000');
});