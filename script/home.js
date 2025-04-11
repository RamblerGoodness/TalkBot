document.addEventListener("DOMContentLoaded", () => {
    const characterList = document.getElementById("character-list");
    
    // Fetch characters from the API
    fetch('/characters')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Clear any existing list items
            characterList.innerHTML = '';
            
            // Populate the character list with data from the API
            data.characters.forEach(character => {
                const listItem = document.createElement("li");
                listItem.className = "character-item";
                
                // Create character card
                const card = document.createElement("div");
                card.className = "character-card";
                
                // Create character content wrapper
                const cardContent = document.createElement("div");
                cardContent.className = "character-card-content";
                
                // Create character image if available
                if (character.profile) {
                    const img = document.createElement("img");
                    
                    // Fix image path - extract just the filename from the profile path
                    const profilePath = character.profile;
                    const filename = profilePath.split('/').pop().split('.')[0];
                    img.src = `page/image/${filename}.png`;
                    
                    img.alt = character.name;
                    img.className = "character-image";
                    card.appendChild(img);
                }
                
                // Create character name
                const nameEl = document.createElement("h3");
                nameEl.textContent = character.name;
                cardContent.appendChild(nameEl);
                
                // Create character intro
                const introEl = document.createElement("p");
                introEl.textContent = character.intro;
                cardContent.appendChild(introEl);
                
                // Add chat button
                const chatBtn = document.createElement("button");
                chatBtn.className = "button";
                chatBtn.textContent = "Chat Now";
                cardContent.appendChild(chatBtn);
                
                // Add content to card
                card.appendChild(cardContent);
                
                // Add click event to navigate to chat
                card.addEventListener("click", () => {
                    window.location.href = `page/chat.html?character=${encodeURIComponent(character.name)}`;
                });
                
                listItem.appendChild(card);
                characterList.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error('Error fetching characters:', error);
            characterList.innerHTML = '<li class="error">Failed to load characters. Please make sure the server is running.</li>';
        });
});
