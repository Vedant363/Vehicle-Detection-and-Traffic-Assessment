export function stopExecution() {
    document.addEventListener('keydown', function(event) {
        if (event.key === 'q' || event.key === 'Q') {
            window.location.href = '/stop';
            fetch('/complete_stop', {
                method: 'GET', 
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    });    
}