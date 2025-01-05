// trafficLight.js

export function changeLight(lights, currentLight) {
    // Remove 'active' class from all lights
    lights.forEach(light => light.classList.remove('active'));
    
    // Add 'active' class to the current light
    lights[currentLight].classList.add('active');
    
    // Move to the next light
    return (currentLight + 1) % lights.length;
}

export function startTrafficLightCycle() {
    const lights = document.querySelectorAll('.light1');
    let currentLight = 0;
    
    // Start changing lights every second
    setInterval(() => {
        currentLight = changeLight(lights, currentLight);
    }, 1000);
    
    // return interval;
}

// startTrafficLightCycle();
// export function stopTrafficLightCycle(interval) {
//     clearInterval(interval);
// }

// startTrafficLightCycle();
