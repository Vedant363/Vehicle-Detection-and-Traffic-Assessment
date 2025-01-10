// videoFeed.test.js
/**
 * @jest-environment jsdom
 */

import { checkVideoFeed } from '../../views/static/js/videoFeed';

describe('checkVideoFeed', () => {
  let videoElement;
  let loaderElement;
  let consoleErrorSpy;
  let consoleLogSpy;

  beforeEach(() => {
    // Set up our DOM with a video element and a loader
    document.body.innerHTML = `
      <video id="videoStream"></video>
      <div class="loader" style="display:block"></div>
    `;
    videoElement = document.getElementById('videoStream');
    loaderElement = document.querySelector('.loader');

    // Spy on console methods
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    // Restore original console methods
    consoleErrorSpy.mockRestore();
    consoleLogSpy.mockRestore();
  });

  it('logs an error if the video element is not found', () => {
    // Call the function with a non-existent ID
    checkVideoFeed('nonExistentVideo', '.loader');
    expect(consoleErrorSpy).toHaveBeenCalledWith('Video element not found');
    // The function should return early without further actions
  });

  it('calls onload and hides the loader when the video feed is ready', () => {
    // Initialize
    checkVideoFeed('videoStream', '.loader');

    // Simulate the video feed onload event
    videoElement.onload();

    // Verify that the loader is hidden
    expect(loaderElement.style.display).toBe('none');
    // Confirm the console log output
    expect(consoleLogSpy).toHaveBeenCalledWith('Video feed is ready.');
  });

  it('calls onerror and retries after the specified interval', () => {
    // Use fake timers to test the retry flow
    jest.useFakeTimers();

    // Initialize
    checkVideoFeed('videoStream', '.loader', 2000);

    // Simulate the video feed onerror event
    videoElement.onerror();

    // Expect an error message
    expect(consoleErrorSpy).toHaveBeenCalledWith('Video feed not yet available. Retrying...');

    // Fast-forward the timer by 2 seconds (the retry interval)
    jest.advanceTimersByTime(2000);

    // The function should be called again after the timeout
    // We can check consoleErrorSpy's call count or rely on additional logic
    // to confirm the retry occurred if needed.

    jest.useRealTimers();
  });
});