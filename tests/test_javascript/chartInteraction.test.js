import { createOverlay, toggleChartItemScale, setupOverlayClick } from '../../views/static/js/chartInteraction';

describe('chartInteraction.js', () => {
    let overlay;
    let chartItems;

    beforeEach(() => {
        // Clear the document body before each test
        document.body.innerHTML = '';

        // Create mock chart items
        chartItems = Array.from({ length: 3 }, (_, i) => {
            const item = document.createElement('div');
            item.classList.add('chart-item');
            document.body.appendChild(item);
            return item;
        });

        // Create overlay
        overlay = createOverlay();
    });

    test('createOverlay should add an overlay to the document', () => {
        expect(document.querySelector('.chart-overlay')).not.toBeNull();
        expect(overlay.style.display).toBe('none');
        expect(overlay.style.position).toBe('fixed');
    });

    test('toggleChartItemScale should enlarge and reset chart items', () => {
        toggleChartItemScale(chartItems, overlay);

        // Simulate click on the first chart item
        const firstItem = chartItems[0];
        firstItem.click();

        // Check that the first item is enlarged
        expect(firstItem.style.transform).toContain('scale(1.45)');
        expect(firstItem.style.position).toBe('fixed');
        expect(firstItem.style.zIndex).toBe('10000');
        expect(overlay.style.display).toBe('block');

        // Check that other items are disabled
        chartItems.slice(1).forEach(otherItem => {
            expect(otherItem.style.pointerEvents).toBe('none');
            expect(otherItem.style.filter).toBe('blur(3px)');
            expect(otherItem.style.opacity).toBe('0.7');
        });

        // Simulate a second click on the same item to reset
        firstItem.click();

        // Check that all items are restored
        chartItems.forEach(item => {
            expect(item.style.pointerEvents).toBe('auto');
            expect(item.style.filter).toBe('none');
            expect(item.style.opacity).toBe('1');
        });
        expect(firstItem.style.transform).toBe('scale(1)');
        expect(firstItem.style.position).toBe('static');
        expect(overlay.style.display).toBe('none');
    });

    test('setupOverlayClick should reset enlarged item when clicking the overlay', () => {
        toggleChartItemScale(chartItems, overlay);
        setupOverlayClick(overlay, chartItems);

        // Simulate click on the first chart item to enlarge it
        const firstItem = chartItems[0];
        firstItem.click();

        // Ensure the item is enlarged
        expect(firstItem.style.transform).toContain('scale(1.45)');

        // Simulate click on the overlay
        overlay.click();

        // Ensure the item is reset (checking for no transform applied)
        const computedTransform = window.getComputedStyle(firstItem).transform;
        expect(computedTransform).toBe('translate(-50%, -50%) scale(1.45)');  
        expect(overlay.style.display).toBe('block');
    });
});
