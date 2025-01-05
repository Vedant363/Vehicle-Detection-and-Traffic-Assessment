// videoFeed.js

export function checkVideoFeed(videoElementId, loaderSelector, retryInterval = 1000) {
    const videoElement = document.getElementById(videoElementId);

    if (!videoElement) {
        console.error('Video element not found');
        return;
    }

    videoElement.onload = () => {
        // Hide the loader once the video feed is ready
        document.querySelector(loaderSelector).style.display = 'none';
        console.log('Video feed is ready.');
        // clearInterval(interval); // Stop the traffic light animation
    };

    videoElement.onerror = () => {
        console.error('Video feed not yet available. Retrying...');
        setTimeout(() => checkVideoFeed(videoElementId, loaderSelector, retryInterval), retryInterval);
    };
}
