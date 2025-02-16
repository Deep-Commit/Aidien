/**
 * earthOrbit.js 
 *
 * A sample JavaScript file that calculates the Earth’s position using a simplified Keplerian model.
 *
 * Orbital elements used (approximate):
 * - Semi-major axis (a): 149,597,870.7 km (1 AU)
 * - Eccentricity (e): 0.0167
 * - Orbital period (T): 365.256363004 days (sidereal year)
 *
 * The model calculates:
 *   1. The mean anomaly M = n * (t - t0)
 *   2. The eccentric anomaly E by solving Kepler’s equation: M = E - e*sin(E)
 *   3. The true anomaly ν from E
 *   4. The radial distance r = a * (1 - e*cos(E))
 *   5. The (x, y) coordinates in the orbital plane using ν and r
 *
 * Note: This is a simplified model and does not include 3D effects or lunar perturbations.
 */

// Define the Earth's orbital elements (approximate values)
const a = 149597870.7; // Semi-major axis in kilometers (1 AU)
const e = 0.0167; // Eccentricity
const T_days = 365.256363004; // Orbital period in days (sidereal year)
const T = T_days * 24 * 3600; // Orbital period in seconds
const n = 2 * Math.PI / T;    // Mean motion (radians per second)

// Define a reference date corresponding to a known perihelion (closest approach)
// (This date is chosen arbitrarily for this example.)
const referenceDate = new Date('2020-01-03T00:00:00Z');

/**
 * Solves Kepler’s equation: M = E - e*sin(E) for the eccentric anomaly E.
 * Uses the Newton–Raphson iterative method.
 *
 * @param {number} M - Mean anomaly (in radians)
 * @param {number} e - Eccentricity (0 <= e < 1)
 * @param {number} tol - Tolerance for convergence (default: 1e-6)
 * @returns {number} The eccentric anomaly E (in radians)
 */
function solveKepler(M, e, tol = 1e-6) {
  let E = M; // Initial guess: E = M (works well for small e)
  let delta = 1;
  while (Math.abs(delta) > tol) {
    delta = (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E));
    E = E - delta;
  }
  return E;
}

/** * Computes the Earth’s position in its orbit at a given date. * Returns the (x, y) coordinates in the orbital plane (in kilometers). * * @param {Date} date - The date for which to calculate the Earth's position. * @returns {object} An object containing the x and y coordinates (in km). */
function computeEarthPosition(date) {
  // Calculate time difference (in seconds) from the reference date
  const dt = (date - referenceDate) / 1000;
  
  // Compute the mean anomaly M (wrap it between 0 and 2π)
  const M = (n * dt) % (2 * Math.PI);
  
  // Solve for the eccentric anomaly E using Kepler’s equation
  const E = solveKepler(M, e);
  
  // Calculate the true anomaly ν from the eccentric anomaly E
  const nu = 2 * Math.atan2(
    Math.sqrt(1 + e) * Math.sin(E / 2),
    Math.sqrt(1 - e) * Math.cos(E / 2)
  );
  
  // Calculate the distance r from Sun to Earth at this point in the orbit
  const r = a * (1 - e * Math.cos(E));
  
  // Convert polar coordinates (r, ν) to Cartesian coordinates (x, y)
  const x = r * Math.cos(nu);
  const y = r * Math.sin(nu);
  
  return { x, y };
}

// ------------------------------
// Example usage:
// ------------------------------

// Get the current date and compute the Earth's position
const now = new Date();
const position = computeMoonPosition(now);

// Log the results
console.log("Earth position on", now.toISOString());
console.log("x (km):", position.x.toFixed(2));
console.log("y (km):", position.y.toFixed(2));
