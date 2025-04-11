document.addEventListener("DOMContentLoaded", () => {
    const characterList = document.getElementById("character-list");

    // Simulated character data
    const characters = [
        { name: "Alice", description: "A friendly character" },
        { name: "Bob", description: "A mysterious traveler" }
    ];

    // Populate the character list
    characters.forEach(character => {
        const listItem = document.createElement("li");
        listItem.textContent = `${character.name} - ${character.description}`;
        listItem.addEventListener("click", () => {
            // Navigate to the chat page with the selected character
            window.location.href = `page/chat.html?character=${character.name}`;
        });
        characterList.appendChild(listItem);
    });
});
