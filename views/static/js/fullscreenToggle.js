// fullscreenToggle.js

export function toggleFullscreen() {
    const element = document.documentElement;  // This will toggle fullscreen for the entire page

    if (!document.fullscreenElement) {
        // Enter fullscreen mode
        if (element.requestFullscreen) {
            element.requestFullscreen();
        } else if (element.mozRequestFullScreen) { // Firefox
            element.mozRequestFullScreen();
        } else if (element.webkitRequestFullscreen) { // Chrome, Safari and Opera
            element.webkitRequestFullscreen();
        } else if (element.msRequestFullscreen) { // IE/Edge
            element.msRequestFullscreen();
        }
    } else {
        // Exit fullscreen mode
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.mozCancelFullScreen) { // Firefox
            document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) { // Chrome, Safari and Opera
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) { // IE/Edge
            document.msExitFullscreen();
        }
    }
}

export function setupFullscreenListener() {
    // Listen for the "F" key press to toggle fullscreen
    document.addEventListener('keydown', function(event) {
        if (event.key === 'f' || event.key === 'F') { // Detects 'f' or 'F' key
            toggleFullscreen();  // Toggle fullscreen mode
        }
    });
}
