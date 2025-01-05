// videoToggle.js

export function toggleVideoVisibility(url, eyeButton, loader, tooltipText) {
    // Show the loader while processing
    loader.style.display = "block";

    // Toggle the video visibility by making a POST request
    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.show_video) {
            // Video is visible
            // eyeButton.src = "{{ url_for('static', filename='images/eyeopen.png') }}";  
            eyeButton.src = "/static/images/eyeopen.png";  
            tooltipText.textContent = 'Detection Visibility On';
        } else {
            // Video is invisible
            // eyeButton.src = "{{ url_for('static', filename='images/eyeclose.png') }}"; 
            eyeButton.src = "/static/images/eyeclose.png"; 
            tooltipText.textContent = 'Detection Visibility Off';
        }
    })
    .catch(error => console.error("Error toggling video visibility:", error))
    .finally(() => {
        // Hide the loader after completion
        setTimeout(() => {
            loader.style.display = "none";
        }, 5000); // Adjust the timeout to match server response time
    });
}

export function setupEyeButton(eyeButtonId, videoStreamId, loaderId, tooltipSelector, toggleUrl) {
    const eyeButton = document.getElementById(eyeButtonId);
    const videoStream = document.getElementById(videoStreamId);
    const loader = document.getElementById(loaderId);
    const tooltipText = document.querySelector(tooltipSelector);

    // Add click event listener to the eye button
    eyeButton.addEventListener("click", function () {
        toggleVideoVisibility(toggleUrl, eyeButton, loader, tooltipText);
    });
}
