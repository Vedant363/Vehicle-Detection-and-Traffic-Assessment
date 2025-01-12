// themeToggle.js

export function getCurrentLabelColor() {
    let currentLabelColor = ''; // Default to black for light mode
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        currentLabelColor = savedTheme === 'light' ? 'black' : 'white';
    }
    else{
        currentLabelColor = 'black';
    }
    return currentLabelColor;
}

export function setupThemeToggle() {
    const toggleButton = document.querySelector('.togglebutton');
    const tooltipText = document.querySelector('.tooltip-text2');
    const body = document.body;

    // URLs or paths to the sun and moon images
    // const sunImageURL = "{{ url_for('static', filename='images/sun.png') }}"; 
    // const moonImageURL = "{{ url_for('static', filename='images/moon.png') }}"; 
    const sunImageURL = '/static/images/sun.png';
    const moonImageURL = '/static/images/moon.png';

    // Check for saved theme in localStorage, default to light mode
    let isLightMode = localStorage.getItem('theme') === 'light';

    // Set the initial theme based on localStorage
    if (isLightMode) {
        body.classList.add('light');
        body.classList.remove('dark');
    } else {
        body.classList.add('dark');
        body.classList.remove('light');
    }

    // Create an image element and append it to the toggle button
    const icon = document.createElement('img');
    icon.src = isLightMode ? sunImageURL : moonImageURL; // Use the appropriate icon
    icon.alt = isLightMode ? 'Sun Icon' : 'Moon Icon';
    icon.style.width = '30px';
    icon.style.height = '30px';
    toggleButton.appendChild(icon);

    // Add click event listener to toggle between light and dark mode
    toggleButton.addEventListener('click', () => {
        if (isLightMode) {
            body.classList.remove('light');
            body.classList.add('dark');
            icon.src = moonImageURL; // Update icon to Moon
            icon.alt = 'Moon Icon';
            tooltipText.textContent = 'Dark Mode';
            localStorage.setItem('theme', 'dark'); // Save theme in localStorage
        } else {
            body.classList.remove('dark');
            body.classList.add('light');
            icon.src = sunImageURL; // Update icon to Sun
            icon.alt = 'Sun Icon';
            tooltipText.textContent = 'Light Mode';
            localStorage.setItem('theme', 'light'); // Save theme in localStorage
        }
        isLightMode = !isLightMode; // Toggle state
    });
}
