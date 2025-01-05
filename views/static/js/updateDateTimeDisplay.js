// dateTime.js

export function updateDateTimeDisplay() {
    const dateElement = document.getElementById('date');
    const timeElement = document.getElementById('time');
    const now = new Date();

    // Format date
    const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    dateElement.textContent = now.toLocaleDateString(undefined, dateOptions);

    // Format time
    const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit' };
    timeElement.textContent = now.toLocaleTimeString(undefined, timeOptions);
}

export function startDateTimeUpdates() {
    // Update the date and time immediately on load
    updateDateTimeDisplay();

    // Update every second for real-time display
    setInterval(updateDateTimeDisplay, 1000);
}
