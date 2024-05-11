function solveQuadratic() {
  const a = parseFloat(document.getElementById("a").value);
  const b = parseFloat(document.getElementById("b").value);
  const c = parseFloat(document.getElementById("c").value);

  if (isNaN(a) || isNaN(b) || isNaN(c)) {
      document.getElementById("result").innerText = "Please enter valid numbers.";
      return;
  }

  const discriminant = b * b - 4 * a * c;

  if (discriminant > 0) {
      const root1 = (-b + Math.sqrt(discriminant)) / (2 * a);
      const root2 = (-b - Math.sqrt(discriminant)) / (2 * a);
      document.getElementById("result").innerText = `Roots: ${root1}, ${root2}`;
  } else if (discriminant === 0) {
      const root = -b / (2 * a);
      document.getElementById("result").innerText = `Root: ${root}`;
  } else {
      const realPart = -b / (2 * a);
      const imaginaryPart = Math.sqrt(-discriminant) / (2 * a);
      document.getElementById("result").innerText = `Roots: ${realPart} ± ${imaginaryPart}i`;
  }
}

function calculate() {
  // Get the coefficients from the input field
  const coefficients = document.getElementById("coefficients").value.split(" ").
