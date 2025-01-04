// chartInteraction.js

export function createOverlay() {
    // Create an overlay to prevent interactions
    const overlay = document.createElement('div');
    overlay.classList.add('chart-overlay');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.5);
        z-index: 999;
        display: none;
        cursor: pointer;
    `;
    document.body.appendChild(overlay);
    return overlay;
}

export function toggleChartItemScale(chartItems, overlay) {
    chartItems.forEach(item => {
        // Track the current scale state for each item
        let isEnlarged = false;

        item.addEventListener('click', () => {
            if (!isEnlarged) {
                // First, disable all other items
                chartItems.forEach(otherItem => {
                    if (otherItem !== item) {
                        otherItem.style.pointerEvents = 'none';
                        otherItem.style.filter = 'blur(3px)';
                        otherItem.style.opacity = '0.7';
                    }
                });

                // Enlarge the clicked item
                item.style.transform = 'scale(1.45)';
                item.style.zIndex = '10000';  // Ensure it's above the overlay
                item.style.position = 'fixed';  // Position relative to the viewport
                item.style.top = '50%';
                item.style.left = '50%';
                item.style.transform = 'translate(-50%, -50%) scale(1.45)';

                // Show overlay to prevent any other interactions
                overlay.style.display = 'block';
            } else {
                // Return to original state
                chartItems.forEach(otherItem => {
                    otherItem.style.pointerEvents = 'auto';
                    otherItem.style.filter = 'none';
                    otherItem.style.opacity = '1';
                });

                // Reset the clicked item
                item.style.transform = 'scale(1)';
                item.style.zIndex = '1';
                item.style.position = 'static';

                // Hide the overlay
                overlay.style.display = 'none';
            }

            // Toggle the scale state
            isEnlarged = !isEnlarged;
        });
    });
}

export function setupOverlayClick(overlay, chartItems) {
    // Close enlarged view if clicking the overlay
    overlay.addEventListener('click', () => {
        const enlargedItem = document.querySelector('.chart-item[style*="scale(2)"], .chart-item1[style*="scale(2)"]');
        if (enlargedItem) {
            enlargedItem.click(); // Trigger the existing click handler to reset
        }
    });
}
