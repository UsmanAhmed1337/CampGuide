function sendMessage() {
    const userInput = document.getElementById('user-input').value.trim();

    if (userInput === '') {
        alert('Please enter a message before sending.');
        return;
    }

    fetch('http://3.25.58.26/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userInput }),
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
