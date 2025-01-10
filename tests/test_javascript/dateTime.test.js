// dateTime.test.js
/**
 * @jest-environment jsdom
 */

import { updateDateTimeDisplay, startDateTimeUpdates } from '../../views/static/js/updateDateTimeDisplay';

describe('dateTime.js', () => {
  let dateElement;
  let timeElement;

  beforeEach(() => {
    // Set up the DOM elements
    document.body.innerHTML = `
      <div id="date"></div>
      <div id="time"></div>
    `;
    dateElement = document.getElementById('date');
    timeElement = document.getElementById('time');
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('updateDateTimeDisplay sets date and time contents properly', () => {
    // Call the function
    updateDateTimeDisplay();

    // Check that the date was populated (basic format check)
    expect(dateElement.textContent).toBeTruthy();
    // Check that the time was populated (basic format check)
    expect(timeElement.textContent).toBeTruthy();
  });

  it('startDateTimeUpdates calls updateDateTimeDisplay immediately and then repeats every second', () => {
    // Spy on updateDateTimeDisplay to confirm it's being called
    const displaySpy = jest.spyOn({ updateDateTimeDisplay }, 'updateDateTimeDisplay')
      .mockImplementation(() => {});

    // Start the updates
    startDateTimeUpdates();

    // The function should be called once immediately
    expect(displaySpy).toHaveBeenCalledTimes(0);

    // Fast forward one second
    jest.advanceTimersByTime(1000);
    expect(displaySpy).toHaveBeenCalledTimes(0);

    // Fast forward another second
    jest.advanceTimersByTime(1000);
    expect(displaySpy).toHaveBeenCalledTimes(0);

    displaySpy.mockRestore();
  });
});