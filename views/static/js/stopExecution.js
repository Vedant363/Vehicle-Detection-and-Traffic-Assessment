export function stopExecution() {
    document.addEventListener('keydown', function(event) {
        if (event.key === 'q' || event.key === 'Q') {
            window.location.href = '/final_page';
        }
    });
}
