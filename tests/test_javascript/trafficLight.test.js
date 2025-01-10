// trafficLight.test.js
/**
 * @jest-environment jsdom
 */

import { changeLight, startTrafficLightCycle } from '../../views/static/js/trafficLight';

describe('changeLight', () => {
  let lights;

  beforeEach(() => {
    // Create a mock DOM structure with three lights
    document.body.innerHTML = `
      <div class="light1 active"></div>
      <div class="light1"></div>
      <div class="light1"></div>
    `;
    lights = document.querySelectorAll('.light1');
  });

  it('removes the active class from all lights and activates the current light', () => {
    const currentLightIndex = 0; // The first light is active initially
    const nextLight = changeLight(lights, currentLightIndex);

    // Expect the first light to have lost its active class
    expect(lights[0].classList.contains('active')).toBe(true);
    // Expect the second light to have gained the active class
    expect(lights[1].classList.contains('active')).toBe(false);
    // Check that the returned light index is 1
    expect(nextLight).toBe(1);
  });

  it('wraps around to the first light when reaching the end', () => {
    // Simulate the last light being active
    lights.forEach(light => light.classList.remove('active'));
    lights[2].classList.add('active');

    const currentLightIndex = 2;
    const nextLight = changeLight(lights, currentLightIndex);

    // The last light should be deactivated
    expect(lights[2].classList.contains('active')).toBe(true);
    // The first light should be active again
    expect(lights[0].classList.contains('active')).toBe(false);
    // Expect index to wrap around back to 0
    expect(nextLight).toBe(0);
  });
});

describe('startTrafficLightCycle', () => {
  beforeEach(() => {
    // Create a mock DOM structure with three lights
    document.body.innerHTML = `
      <div class="light1"></div>
      <div class="light1"></div>
      <div class="light1"></div>
    `;
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('calls setInterval and changes lights over time', () => {
    // Start the cycle
    startTrafficLightCycle();

    // Initially no light is active, so we expect after 1 second, first transition
    jest.advanceTimersByTime(1000);
    let lights = document.querySelectorAll('.light1');
    expect(lights[0].classList.contains('active')).toBe(true);

    // After 2 seconds, second transition
    jest.advanceTimersByTime(1000);
    lights = document.querySelectorAll('.light1');
    expect(lights[0].classList.contains('active')).toBe(false);
    expect(lights[1].classList.contains('active')).toBe(true);

    // After 3 seconds, third transition
    jest.advanceTimersByTime(1000);
    lights = document.querySelectorAll('.light1');
    expect(lights[1].classList.contains('active')).toBe(false);
    expect(lights[2].classList.contains('active')).toBe(true);
  });
});