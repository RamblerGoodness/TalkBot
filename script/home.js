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

    // Persona creation logic
    const personaForm = document.getElementById("persona-form");
    if (personaForm) {
        personaForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("persona-name").value.trim();
            const desc = document.getElementById("persona-desc").value.trim();
            const msgDiv = document.getElementById("persona-message");
            msgDiv.textContent = "";
            if (!name || !desc) {
                msgDiv.textContent = "Please enter both a name and description.";
                return;
            }
            try {
                const response = await fetch("/persona", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, description: desc })
                });
                if (response.ok) {
                    msgDiv.textContent = `Persona '${name}' created!`;
                    personaForm.reset();
                } else {
                    const data = await response.json();
                    msgDiv.textContent = data.error || "Failed to create persona.";
                }
            } catch (err) {
                msgDiv.textContent = "Error connecting to server.";
            }
        });
    }

    // Persona list logic
    async function loadPersonaList() {
        const list = document.getElementById("persona-list");
        list.innerHTML = '';
        try {
            const res = await fetch('/personas');
            const data = await res.json();
            if (data.personas && data.personas.length > 0) {
                data.personas.forEach(p => {
                    const li = document.createElement('li');
                    li.style.display = 'flex';
                    li.style.alignItems = 'center';
                    li.style.justifyContent = 'space-between';
                    li.style.padding = '0.5rem 0';
                    li.innerHTML = `
                        <span><strong>${p.name}</strong>: <span class="desc">${p.description}</span></span>
                        <span>
                            <button class="button persona-edit" data-name="${p.name}">Edit</button>
                            <button class="button persona-delete" data-name="${p.name}" style="background:#e53935; margin-left:0.5rem;">Delete</button>
                        </span>
                    `;
                    list.appendChild(li);
                });
            } else {
                list.innerHTML = '<li style="color:#b0b0b0;">No personas saved.</li>';
            }
        } catch (e) {
            list.innerHTML = '<li style="color:#e53935;">Error loading personas.</li>';
        }
    }

    loadPersonaList();

    // Persona edit/delete handlers
    document.getElementById("persona-list").onclick = async function(e) {
        if (e.target.classList.contains("persona-delete")) {
            const name = e.target.getAttribute("data-name");
            if (confirm(`Delete persona '${name}'?`)) {
                await fetch(`/persona/${encodeURIComponent(name)}`, { method: 'DELETE' });
                loadPersonaList();
                loadPersonas && loadPersonas(); // refresh chat persona dropdown if present
            }
        } else if (e.target.classList.contains("persona-edit")) {
            const name = e.target.getAttribute("data-name");
            const descSpan = e.target.closest('li').querySelector('.desc');
            const currentDesc = descSpan.textContent;
            const newDesc = prompt(`Edit description for '${name}':`, currentDesc);
            if (newDesc !== null && newDesc.trim() !== "") {
                await fetch(`/persona/${encodeURIComponent(name)}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ description: newDesc.trim() })
                });
                loadPersonaList();
                loadPersonas && loadPersonas();
            }
        }
    };
});
