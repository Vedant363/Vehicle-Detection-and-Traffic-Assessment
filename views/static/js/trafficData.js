// trafficData.js

// Helper function to get the color for traffic lights based on the status
export function getTrafficLightColor(status) {
    status = status.toLowerCase();
    switch(status) {
        case 'red':
            return '#ff0000';  // Red
        case 'green':
            return '#00ff00';  // Green
        case 'yellow':
            return '#ffff00';  // Yellow
        default:
            return '#000000';  // Default (black if no match)
    }
}

// Function to fetch traffic data and update the UI
export function updateTrafficData() {
    fetch('/traffic_data')
        .then(response => response.json())
        .then(data => {
            // Update the text content based on the fetched data
            document.getElementById('vehicleCount').innerText = data.vehicle_count;
            document.getElementById('avgSpeed').innerText = data.avg_speed.toFixed(2) + " km/h";
            document.getElementById('trafficJam').innerText = data.is_traffic_jam ? "Yes" : "No";
            document.getElementById('heavyVehicles').innerText = data.too_many_heavy_vehicles ? "Yes" : "No";
            document.getElementById('clearanceTime').innerText = data.estimated_clearance_time.toFixed(2) + " s";
            
            // Update both traffic light text and visual indicator
            const trafficLightText = data.traffic_light_decision[0];
            const trafficLightDuration = data.traffic_light_decision[1];
            
            // Update the text display
            const trafficLightTextElements = document.querySelectorAll('#trafficLight');
            trafficLightTextElements.forEach(element => {
                element.innerText = `for ${trafficLightDuration} s`;
                element.style.color = getTrafficLightColor(trafficLightText);
            });

            // Update the visual light indicator
            const lightElement = document.querySelector('.trafficlight .light');
            if (lightElement) {
                // lightElement.classList.toggle('active');
                lightElement.style.backgroundColor = getTrafficLightColor(trafficLightText);
            }
        })
        .catch(error => {
            console.error('Error fetching traffic data:', error);
        });
}
