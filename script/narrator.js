document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const storyTitle = document.getElementById('story-title');
    const storyTime = document.getElementById('story-time');
    const sceneName = document.getElementById('scene-name');
    const sceneTime = document.getElementById('scene-time');
    const charactersPresent = document.getElementById('characters-present');
    const charactersAvailable = document.getElementById('characters-available');
    const personaSelect = document.getElementById('persona-select');
    const chatHistory = document.getElementById('chat-history');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-message');
    
    // Modals
    const storyModal = document.getElementById('story-modal');
    const sceneModal = document.getElementById('scene-modal');
    const directionModal = document.getElementById('direction-modal');
    const commandsModal = document.getElementById('commands-modal');
    const suggestionModal = document.getElementById('suggestion-modal');
    
    // Buttons
    const changeStoryButton = document.getElementById('change-story');
    const sceneSetupButton = document.getElementById('scene-setup');
    const narratorDirectButton = document.getElementById('narrator-direct');
    const advanceTimeButton = document.getElementById('advance-time');
    const showCommandsButton = document.getElementById('show-commands');
    const suggestCharacterButton = document.getElementById('suggest-character');
    
    // State
    let activeNarrator = null;
    let allCharacters = [];
    let currentPersona = null;
    
    // Initialize
    loadNarratorData();
    loadPersonas();
    
    // Event Listeners
    changeStoryButton.addEventListener('click', showStoryModal);
    sceneSetupButton.addEventListener('click', showSceneModal);
    narratorDirectButton.addEventListener('click', showDirectionModal);
    advanceTimeButton.addEventListener('click', advanceTime);
    showCommandsButton.addEventListener('click', () => showModal(commandsModal));
    suggestCharacterButton.addEventListener('click', showSuggestionModal);
    
    // Message handling
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', e => {
        if (e.key === 'Enter') sendMessage();
    });
    
    // Close buttons for modals
    document.getElementById('close-story-modal').addEventListener('click', () => hideModal(storyModal));
    document.getElementById('close-scene-modal').addEventListener('click', () => hideModal(sceneModal));
    document.getElementById('close-direction-modal').addEventListener('click', () => hideModal(directionModal));
    document.getElementById('close-commands-modal').addEventListener('click', () => hideModal(commandsModal));
    document.getElementById('close-suggestion-modal').addEventListener('click', () => hideModal(suggestionModal));
    document.getElementById('close-commands').addEventListener('click', () => hideModal(commandsModal));
    
    // Story modal buttons
    document.getElementById('select-story').addEventListener('click', selectStory);
    document.getElementById('create-story').addEventListener('click', createNewStory);
    document.getElementById('delete-story').addEventListener('click', deleteStory);
    
    // Scene modal buttons
    document.getElementById('save-scene').addEventListener('click', saveScene);
    document.getElementById('cancel-scene').addEventListener('click', () => hideModal(sceneModal));
    
    // Direction modal buttons
    document.getElementById('get-direction').addEventListener('click', getDirection);
    document.getElementById('cancel-direction').addEventListener('click', () => hideModal(directionModal));
    
    // Suggestion modal buttons
    document.getElementById('get-suggestion').addEventListener('click', getCharacterSuggestion);
    document.getElementById('cancel-suggestion').addEventListener('click', () => hideModal(suggestionModal));
    
    // Persona selector
    personaSelect.addEventListener('change', function() {
        currentPersona = this.value;
    });
    
    // Functions
    
    // Load the active narrator and update UI
    async function loadNarratorData() {
        try {
            // Get all available characters
            const charactersResponse = await fetch('/characters');
            const charactersData = await charactersResponse.json();
            allCharacters = charactersData.characters;
            
            // Get active narrator
            const narratorResponse = await fetch('/narrator/active');
            
            if (!narratorResponse.ok) {
                showErrorMessage("No active story found. Please create or select a story.");
                return;
            }
            
            activeNarrator = await narratorResponse.json();
            
            // Update UI with narrator data
            updateNarratorUI();
            
            // Get initial scene narration
            getInitialNarration();
        } catch (error) {
            console.error('Error loading narrator data:', error);
            showErrorMessage("Error connecting to server. Please refresh the page.");
        }
    }
    
    // Load available personas
    async function loadPersonas() {
        try {
            const response = await fetch('/personas');
            const data = await response.json();
            
            // Clear existing options except the default
            personaSelect.innerHTML = '<option value="">Select Persona</option>';
            
            // Add personas to dropdown
            if (data.personas && data.personas.length > 0) {
                data.personas.forEach(persona => {
                    const option = document.createElement('option');
                    option.value = persona.name;
                    option.textContent = persona.name;
                    personaSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading personas:', error);
        }
    }
    
    // Update the UI with narrator data
    function updateNarratorUI() {
        if (!activeNarrator) return;
        
        // Update story info
        storyTitle.textContent = activeNarrator.id || "Story";
        storyTime.textContent = `Day ${activeNarrator.day}, ${formatTimeOfDay(activeNarrator.time_of_day)`;
        
        // Update scene info
        sceneName.textContent = activeNarrator.scene || "Scene";
        sceneTime.textContent = `Day ${activeNarrator.day}, ${formatTimeOfDay(activeNarrator.time_of_day)`;
        
        // Update characters present
        charactersPresent.innerHTML = '';
        if (activeNarrator.characters_present && activeNarrator.characters_present.length > 0) {
            activeNarrator.characters_present.forEach(char => {
                const charItem = createCharacterItem(char, true);
                charactersPresent.appendChild(charItem);
            });
        } else {
            charactersPresent.innerHTML = '<div class="empty-message">No characters in scene</div>';
        }
        
        // Update available characters (not in scene)
        charactersAvailable.innerHTML = '';
        const presentCharNames = activeNarrator.characters_present.map(c => c.name);
        const availableChars = allCharacters.filter(c => !presentCharNames.includes(c.name));
        
        if (availableChars.length > 0) {
            availableChars.forEach(char => {
                const charItem = createCharacterItem(char, false);
                charactersAvailable.appendChild(charItem);
            });
        } else {
            charactersAvailable.innerHTML = '<div class="empty-message">No additional characters</div>';
        }
    }
    
    // Format time of day for display
    function formatTimeOfDay(timeString) {
        return timeString
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    // Create a character list item
    function createCharacterItem(character, isInScene) {
        const item = document.createElement('div');
        item.className = `character-item ${isInScene ? 'in-scene' : 'available'}`;
        
        const img = document.createElement('img');
        // Fix image path if needed
        let imgSrc = character.profile;
        if (!imgSrc.includes('.png') && !imgSrc.includes('.jpg') && !imgSrc.includes('.jpeg')) {
            imgSrc = `/page/image/${character.profile}.png`;
        }
        img.src = imgSrc;
        img.alt = character.name;
        img.onerror = function() {
            // Instead of using a placeholder that doesn't exist, create a text-based avatar
            this.style.display = 'none'; // Hide the broken image
            const initials = document.createElement('div');
            initials.className = 'character-initials';
            initials.textContent = character.name.charAt(0).toUpperCase();
            item.insertBefore(initials, this.nextSibling);
            console.error(`Failed to load image for ${character.name}: ${imgSrc}`);
        };
        
        const name = document.createElement('span');
        name.textContent = character.name;
        
        item.appendChild(img);
        item.appendChild(name);
        
        // Add click handler for character actions
        item.addEventListener('click', () => {
            if (isInScene) {
                // Show confirmation for removing a character
                if (confirm(`Remove ${character.name} from the scene?`)) {
                    removeCharacterFromScene(character.name);
                }
            } else {
                // Add to scene
                addCharacterToScene(character.name);
            }
        });
        
        return item;
    }
    
    // Add a character to the scene with proper error handling
    async function addCharacterToScene(characterName) {
        try {
            // Show loading message
            addNarratorMessage(`*Attempting to add ${characterName} to the scene...*`);
            
            // Use active narrator as target
            const response = await fetch('/narrator/character', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    narrator_id: activeNarrator.id,
                    character_name: characterName
                })
            });
            
            if (response.ok) {
                // Successful response - Now use the command to add to scene
                const chatResponse = await fetch('/narrator/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: `/add ${characterName}`
                    })
                });
                
                if (chatResponse.ok) {
                    const result = await chatResponse.json();
                    // Add system message to chat
                    addNarratorMessage(result.response);
                    // Refresh the narrator data
                    await loadNarratorData();
                } else {
                    throw new Error(`Failed to add character to scene: ${(await chatResponse.json()).error}`);
                }
            } else {
                throw new Error(`Failed to add character to narrator: ${(await response.json()).error}`);
            }
        } catch (error) {
            console.error('Error adding character to scene:', error);
            addSystemMessage(`Error: ${error.message || 'Could not add character to scene'}`);
        }
    }
    
    // Remove a character from the scene
    async function removeCharacterFromScene(characterName) {
        try {
            const response = await fetch('/narrator/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: `/remove ${characterName}`
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                // Add system message to chat
                addNarratorMessage(result.response);
                // Refresh the narrator data
                loadNarratorData();
            } else {
                console.error('Error removing character from scene:', await response.json());
            }
        } catch (error) {
            console.error('Error removing character from scene:', error);
        }
    }
    
    // Get initial narration for the scene
    async function getInitialNarration() {
        try {
            const response = await fetch('/narrator/direct', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: "Describe the opening of this scene in detail."
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                // Clear any existing welcome message
                chatHistory.innerHTML = '';
                // Add narration to chat
                addNarratorMessage(result.response);
            }
        } catch (error) {
            console.error('Error getting initial narration:', error);
        }
    }
    
    // Send a message from the user
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Disable input while processing
        messageInput.disabled = true;
        sendButton.disabled = true;
        
        // Add user message to chat
        addUserMessage(message);
        
        // Clear input
        messageInput.value = '';
        
        try {
            // Send to server
            const response = await fetch('/narrator/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    persona: currentPersona
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                
                // Update story state if it changed
                if (result.day && result.time_of_day) {
                    activeNarrator.day = result.day;
                    activeNarrator.time_of_day = result.time_of_day;
                    updateTimeDisplay();
                }
                
                // Handle different types of responses
                if (result.is_narrator) {
                    // Narrator message
                    addNarratorMessage(result.response);
                } else {
                    // Character message
                    const character = activeNarrator.characters_present.find(c => c.name === result.character);
                    if (character) {
                        addCharacterMessage(character, result.response);
                    } else {
                        addNarratorMessage("*A mysterious voice responds: " + result.response + "*");
                    }
                }
                
                // Reload narrator data in case characters changed
                loadNarratorData();
            } else {
                console.error('Error sending message:', await response.json());
                addSystemMessage("Error: Could not process your message.");
            }
        } catch (error) {
            console.error('Error sending message:', error);
            addSystemMessage("Error: Connection problem. Please try again.");
        } finally {
            // Re-enable input
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();
        }
    }
    
    // Add a message from the user to the chat
    function addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message user-message';
        messageDiv.textContent = message;
        chatHistory.appendChild(messageDiv);
        scrollChatToBottom();
    }
    
    // Add a message from a character to the chat
    function addCharacterMessage(character, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message character-message';
        
        const header = document.createElement('div');
        header.className = 'message-header';
        
        const img = document.createElement('img');
        // Fix image path if needed
        let imgSrc = character.profile;
        if (!imgSrc.includes('.png') && !imgSrc.includes('.jpg') && !imgSrc.includes('.jpeg')) {
            imgSrc = `/page/image/${character.profile}.png`;
        }
        img.src = imgSrc;
        img.alt = character.name;
        img.onerror = function() {
            // Instead of using a placeholder that doesn't exist, create a text-based avatar
            this.style.display = 'none'; // Hide the broken image
            const initials = document.createElement('div');
            initials.className = 'character-initials';
            initials.textContent = character.name.charAt(0).toUpperCase();
            header.insertBefore(initials, this.nextSibling);
            console.error(`Failed to load image for ${character.name}: ${imgSrc}`);
        };
        
        const name = document.createElement('span');
        name.textContent = character.name;
        
        header.appendChild(img);
        header.appendChild(name);
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = message;
        
        messageDiv.appendChild(header);
        messageDiv.appendChild(content);
        
        chatHistory.appendChild(messageDiv);
        scrollChatToBottom();
    }
    
    // Add a narrator message to the chat
    function addNarratorMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message narrator-message';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = message;
        
        messageDiv.appendChild(content);
        chatHistory.appendChild(messageDiv);
        scrollChatToBottom();
    }
    
    // Add a system message to the chat (for errors, etc.)
    function addSystemMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message narrator-message';
        messageDiv.style.backgroundColor = 'rgba(255, 59, 48, 0.2)';
        messageDiv.textContent = message;
        chatHistory.appendChild(messageDiv);
        scrollChatToBottom();
    }
    
    // Show an error message in the chat
    function showErrorMessage(message) {
        chatHistory.innerHTML = '';
        const errorDiv = document.createElement('div');
        errorDiv.className = 'chat-message narrator-message';
        errorDiv.style.backgroundColor = 'rgba(255, 59, 48, 0.2)';
        errorDiv.style.color = '#ff3b30';
        errorDiv.textContent = message;
        chatHistory.appendChild(errorDiv);
    }
    
    // Scroll chat to the bottom
    function scrollChatToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
    
    // Update time display
    function updateTimeDisplay() {
        storyTime.textContent = `Day ${activeNarrator.day}, ${formatTimeOfDay(activeNarrator.time_of_day)}`;
        sceneTime.textContent = `Day ${activeNarrator.day}, ${formatTimeOfDay(activeNarrator.time_of_day)}`;
    }
    
    // Advance time to next period
    async function advanceTime() {
        try {
            const response = await fetch('/narrator/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: '/time next'
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                
                // Add system message to chat
                addNarratorMessage(result.response);
                
                // Update time in UI if returned
                if (result.day && result.time_of_day) {
                    activeNarrator.day = result.day;
                    activeNarrator.time_of_day = result.time_of_day;
                    updateTimeDisplay();
                }
            } else {
                console.error('Error advancing time:', await response.json());
                addSystemMessage("Error: Could not advance time.");
            }
        } catch (error) {
            console.error('Error advancing time:', error);
            addSystemMessage("Error: Connection problem when advancing time.");
        }
    }
    
    // Show story selection/creation modal
    async function showStoryModal() {
        // Get all narrators from server
        try {
            const response = await fetch('/narrators');
            const data = await response.json();
            
            // Populate the story select dropdown
            const storySelect = document.getElementById('story-select');
            storySelect.innerHTML = '';
            
            if (data.narrators && data.narrators.length > 0) {
                data.narrators.forEach(narrator => {
                    const option = document.createElement('option');
                    option.value = narrator.id;
                    option.textContent = `${narrator.id} (${narrator.characters.length} characters)`;
                    if (narrator.is_active) {
                        option.selected = true;
                    }
                    storySelect.appendChild(option);
                });
            } else {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No stories found';
                storySelect.appendChild(option);
            }
            
            showModal(storyModal);
        } catch (error) {
            console.error('Error loading narrators:', error);
            addSystemMessage("Error: Could not load story list.");
        }
    }
    
    // Show the scene setup modal
    function showSceneModal() {
        // Populate the scene description with current scene
        const sceneDescription = document.getElementById('scene-description');
        sceneDescription.value = activeNarrator.scene || '';
        
        // Get all available characters for checkboxes
        const charactersList = document.getElementById('scene-characters-list');
        charactersList.innerHTML = '';
        
        allCharacters.forEach(character => {
            const isPresent = activeNarrator.characters_present.some(c => c.name === character.name);
            
            const item = document.createElement('div');
            item.className = 'checkbox-item';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `char-${character.name}`;
            checkbox.value = character.name;
            checkbox.checked = isPresent;
            
            const label = document.createElement('label');
            label.htmlFor = `char-${character.name}`;
            label.textContent = character.name;
            
            item.appendChild(checkbox);
            item.appendChild(label);
            charactersList.appendChild(item);
        });
        
        showModal(sceneModal);
    }
    
    // Show the narrator direction modal
    function showDirectionModal() {
        // Clear any previous value
        document.getElementById('direction-prompt').value = '';
        showModal(directionModal);
    }
    
    // Show the character suggestion modal
    function showSuggestionModal() {
        // Clear any previous value
        document.getElementById('suggestion-prompt').value = '';
        showModal(suggestionModal);
    }
    
    // Select an existing story
    async function selectStory() {
        const storySelect = document.getElementById('story-select');
        const narratorId = storySelect.value;
        
        if (!narratorId) {
            alert('Please select a story or create a new one.');
            return;
        }
        
        try {
            const response = await fetch('/narrator/active', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: narratorId
                })
            });
            
            if (response.ok) {
                hideModal(storyModal);
                
                // Reload narrator data
                loadNarratorData();
                
                // Add a message to chat
                addNarratorMessage(`*Switched to story: ${narratorId}*`);
            } else {
                console.error('Error selecting story:', await response.json());
                alert('Could not select story. Please try again.');
            }
        } catch (error) {
            console.error('Error selecting story:', error);
            alert('Connection error. Please try again.');
        }
    }
    
    // Create a new story
    async function createNewStory() {
        const newStoryName = document.getElementById('new-story-name').value.trim();
        
        if (!newStoryName) {
            alert('Please enter a name for the new story.');
            return;
        }
        
        try {
            const response = await fetch('/narrator', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: newStoryName,
                    model: 'dolphin3'
                })
            });
            
            if (response.ok) {
                // Set as active
                await fetch('/narrator/active', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        id: newStoryName
                    })
                });
                
                hideModal(storyModal);
                
                // Reload narrator data
                loadNarratorData();
                
                // Add a message to chat
                addNarratorMessage(`*Created new story: ${newStoryName}*`);
            } else {
                console.error('Error creating story:', await response.json());
                alert('Could not create story. Please try again.');
            }
        } catch (error) {
            console.error('Error creating story:', error);
            alert('Connection error. Please try again.');
        }
    }
    
    // Delete a story
    async function deleteStory() {
        const storySelect = document.getElementById('story-select');
        const narratorId = storySelect.value;
        
        if (!narratorId) {
            alert('Please select a story to delete.');
            return;
        }
        
        if (!confirm(`Are you sure you want to delete the story "${narratorId}"? This cannot be undone.`)) {
            return;
        }
        
        try {
            const response = await fetch(`/narrator/${narratorId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                alert(`Story "${narratorId}" deleted.`);
                hideModal(storyModal);
                
                // Check if we deleted the active story
                if (activeNarrator && activeNarrator.id === narratorId) {
                    // Reload page to get a new active story
                    window.location.reload();
                } else {
                    // Just refresh the story list
                    showStoryModal();
                }
            } else {
                console.error('Error deleting story:', await response.json());
                alert('Could not delete story. Please try again.');
            }
        } catch (error) {
            console.error('Error deleting story:', error);
            alert('Connection error. Please try again.');
        }
    }
    
    // Save scene changes
    async function saveScene() {
        const sceneDescription = document.getElementById('scene-description').value.trim();
        
        if (!sceneDescription) {
            alert('Please enter a scene description.');
            return;
        }
        
        // Get selected characters
        const charactersSelected = [];
        const checkboxes = document.querySelectorAll('#scene-characters-list input[type="checkbox"]');
        
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                charactersSelected.push(checkbox.value);
            }
        });
        
        try {
            const response = await fetch('/narrator/scene', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scene: sceneDescription,
                    characters_present: charactersSelected
                })
            });
            
            if (response.ok) {
                hideModal(sceneModal);
                
                // Reload narrator data
                loadNarratorData();
                
                // Add a message to chat
                addNarratorMessage(`*The scene changes to: ${sceneDescription}*`);
                
                // Get narration for the new scene
                getInitialNarration();
            } else {
                console.error('Error saving scene:', await response.json());
                alert('Could not save scene. Please try again.');
            }
        } catch (error) {
            console.error('Error saving scene:', error);
            alert('Connection error. Please try again.');
        }
    }
    
    // Get narrator direction
    async function getDirection() {
        const promptText = document.getElementById('direction-prompt').value.trim();
        
        if (!promptText) {
            alert('Please enter a direction prompt.');
            return;
        }
        
        hideModal(directionModal);
        
        try {
            const response = await fetch('/narrator/direct', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: promptText
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                
                // Add narration to chat
                addNarratorMessage(result.response);
                
                // Update time if returned
                if (result.day && result.time_of_day) {
                    activeNarrator.day = result.day;
                    activeNarrator.time_of_day = result.time_of_day;
                    updateTimeDisplay();
                }
            } else {
                console.error('Error getting direction:', await response.json());
                addSystemMessage("Error: Could not get narrator direction.");
            }
        } catch (error) {
            console.error('Error getting direction:', error);
            addSystemMessage("Error: Connection problem when getting narrator direction.");
        }
    }
    
    // Get character suggestion
    async function getCharacterSuggestion() {
        const promptText = document.getElementById('suggestion-prompt').value.trim();
        
        if (!promptText) {
            alert('Please enter a suggestion prompt.');
            return;
        }
        
        hideModal(suggestionModal);
        
        // Show loading message
        addNarratorMessage("*The narrator is considering a new character...*");
        
        try {
            const response = await fetch('/narrator/suggest-character', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: promptText
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                
                // Add suggestion to chat
                addNarratorMessage("*The narrator suggests a new character:*");
                addNarratorMessage(result.response);
                
                // Optionally, you could add a button to automatically create this character
                // or just let the user copy the details to create it manually
            } else {
                console.error('Error getting character suggestion:', await response.json());
                addSystemMessage("Error: Could not get character suggestion.");
            }
        } catch (error) {
            console.error('Error getting character suggestion:', error);
            addSystemMessage("Error: Connection problem when getting character suggestion.");
        }
    }
    
    // Utility: Show a modal
    function showModal(modal) {
        modal.style.display = 'flex';
    }
    
    // Utility: Hide a modal
    function hideModal(modal) {
        modal.style.display = 'none';
    }
});