document.getElementById('scanButton').addEventListener('click', function() {
    fetch('/scan', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').innerText = data.message;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result').innerText = 'An error occurred. Please try again.';
    });
});
