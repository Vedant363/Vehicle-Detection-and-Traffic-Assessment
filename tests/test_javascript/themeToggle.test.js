// themeToggle.test.js

/**
 * @jest-environment jsdom
 */

import { setupThemeToggle } from '../../views/static/js/setupThemeToggle';

describe('setupThemeToggle', () => {
  let toggleButton;
  let tooltipText;
  let body;
  let icon;

  beforeEach(() => {
    // Set up our DOM elements
    document.body.innerHTML = `
      <button class="togglebutton"></button>
      <div class="tooltip-text2"></div>
    `;

    toggleButton = document.querySelector('.togglebutton');
    tooltipText = document.querySelector('.tooltip-text2');
    body = document.body;

    // Clear localStorage before each test
    localStorage.clear();

    // Call setupThemeToggle to initialize elements
    setupThemeToggle();

    // After setup, the img tag should be appended
    icon = toggleButton.querySelector('img');
  });

  it('should set light or dark class based on localStorage theme, defaulting to light', () => {
    // Initially no theme is set in localStorage, so default is 'light'
    expect(body.classList.contains('light')).toBe(false);
    expect(body.classList.contains('dark')).toBe(true);

    // If we manually set the theme to dark in localStorage and rerun setup
    document.body.innerHTML = `
      <button class="togglebutton"></button>
      <div class="tooltip-text2"></div>
    `;
    localStorage.setItem('theme', 'dark');
    setupThemeToggle();

    expect(document.body.classList.contains('dark')).toBe(true);
    expect(document.body.classList.contains('light')).toBe(false);
  });

  it('should display the correct icon and alt text based on theme state', () => {
    // Default is light mode
    expect(icon).toBeTruthy();
    expect(icon.src).toMatch("http://localhost/static/images/moon.png");
    expect(icon.alt).toBe('Moon Icon');

    // Simulate a click to switch to dark mode
    toggleButton.click();
    expect(icon.src).toMatch("http://localhost/static/images/sun.png");
    expect(icon.alt).toBe('Sun Icon');
  });

  it('should toggle between light and dark modes when the toggle button is clicked', () => {
    // Initial check (default is light)
    expect(body.classList.contains('light')).toBe(false);
    expect(body.classList.contains('dark')).toBe(true);
    expect(tooltipText.textContent).toBe('');

    // Click to toggle
    toggleButton.click();
    expect(body.classList.contains('dark')).toBe(false);
    expect(body.classList.contains('light')).toBe(true);
    expect(tooltipText.textContent).toBe('Light Mode');
    expect(localStorage.getItem('theme')).toBe('light');

    // Click again to go back to light
    toggleButton.click();
    expect(body.classList.contains('light')).toBe(false);
    expect(body.classList.contains('dark')).toBe(true);
    expect(tooltipText.textContent).toBe('Dark Mode');
    expect(localStorage.getItem('theme')).toBe('dark');
  });
});