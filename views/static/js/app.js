import { updateTrafficData } from './trafficData.js'; 
import { setupThemeToggle } from './setupThemeToggle.js';  
import { setupFullscreenListener } from './fullscreenToggle.js';  
import { startDateTimeUpdates } from './updateDateTimeDisplay.js';  
import { createOverlay, toggleChartItemScale, setupOverlayClick } from './chartInteraction.js';  
import { startTrafficLightCycle } from './trafficLight.js';  
import { checkVideoFeed } from './videoFeed.js';  
import { setupEyeButton } from './videoToggle.js'; 
import { stopExecution } from './stopExecution.js';

startTrafficLightCycle();

updateTrafficData();

setupThemeToggle();

setupFullscreenListener();

startDateTimeUpdates();

stopExecution();

// Chart interactions (overlay, chart scaling)
// const chartContainer = document.querySelector('.container');
const chartItems = document.querySelectorAll('.chart-item, .chart-item1, .traffic-video');
const overlay = createOverlay();  // Create overlay element
toggleChartItemScale(chartItems, overlay);  // Set up chart item scaling
setupOverlayClick(overlay, chartItems);  // Set up overlay click functionality

checkVideoFeed('videoStream', '.loader');

setupEyeButton("eyebutton", "videoStream", "videoloader", ".tooltip-text1", toggleVideoUrl);
setInterval(updateTrafficData, 2000);  // Refresh every 2 seconds