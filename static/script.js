function sendMessage() {
    const userInput = document.getElementById('user-input').value.trim();

    if (userInput === '') {
        alert('Please enter a message before sending.');
        return;
    }

    fetch('https://3.27.23.141/chat?query='+userInput, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        document.getElementById('chat-output').innerHTML += '<p>' + data.response + '</p>';
        document.getElementById('user-input').value = ''; 
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while sending the message. Please try again.');
    });
}
