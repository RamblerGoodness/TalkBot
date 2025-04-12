document.addEventListener('DOMContentLoaded', () => {
    const characterForm = document.getElementById('character-form');
    const messageContainer = document.getElementById('message-container');

    characterForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get form values
        const name = document.getElementById('char-name').value.trim();
        const intro = document.getElementById('char-intro').value.trim();
        const background = document.getElementById('char-background').value.trim();
        const profile = document.getElementById('char-profile').value.trim();
        
        // Validate
        if (!name || !intro || !background || !profile) {
            showMessage('Please fill out all fields', 'error');
            return;
        }
        
        // Create character data
        const characterData = {
            name,
            intro,
            background,
            profile,
        };
        
        try {
            // Submit to API
            const response = await fetch('/character', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(characterData),
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showMessage(`Character "${name}" created successfully!`, 'success');
                characterForm.reset();
                
                // Redirect to home page after 2 seconds
                setTimeout(() => {
                    window.location.href = '../index.html';
                }, 2000);
            } else {
                showMessage(data.error || 'Failed to create character', 'error');
            }
        } catch (error) {
            console.error('Error creating character:', error);
            showMessage('Error connecting to server', 'error');
        }
    });
    
    function showMessage(text, type) {
        messageContainer.innerHTML = '';
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = text;
        messageContainer.appendChild(messageDiv);
    }
});