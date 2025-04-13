from character import Character
import json
import os

class CharacterPool:
    CHARACTERS_FILE = "characters.json"
    
    def __init__(self):
        self.characters = {}
        self.load_characters()

    def add_character(self, character: Character):
        self.characters[character.name] = character
        self.save_characters()

    def get_character(self, name):
        return self.characters.get(name)

    def remove_character(self, name):
        if name in self.characters:
            del self.characters[name]
            self.save_characters()

    def list_characters(self):
        return list(self.characters.values())
        
    def save_characters(self):
        """Save all characters to a JSON file"""
        characters_data = []
        for char in self.characters.values():
            characters_data.append(char.to_dict())
        
        with open(self.CHARACTERS_FILE, "w", encoding="utf-8") as f:
            json.dump(characters_data, f, indent=2)
            
    def load_characters(self):
        """Load characters from the JSON file if it exists"""
        if not os.path.exists(self.CHARACTERS_FILE):
            return
            
        try:
            with open(self.CHARACTERS_FILE, "r", encoding="utf-8") as f:
                characters_data = json.load(f)
                
            for char_data in characters_data:
                char = Character(
                    name=char_data["name"],
                    intro=char_data["intro"],
                    background=char_data["background"],
                    profile=char_data["profile"].replace("page/image/", "").replace(".png", ""),
                    db_name=char_data.get("db_name", f"{char_data['name'].lower()}_memories"),
                    user_name=char_data.get("user_name", "Guest"),
                    user_persona=char_data.get("user_persona", "A curious visitor to the website."),
                    msgs_per_time_change=char_data.get("msgs_per_time_change", 1)
                )
                
                # Set time and other state properties if they exist
                if "current_day" in char_data:
                    char.current_day = char_data["current_day"]
                if "time_of_day" in char_data:
                    char.time_of_day = char_data["time_of_day"]
                if "message_count" in char_data:
                    char.message_count = char_data["message_count"]
                
                self.characters[char.name] = char
        except Exception as e:
            print(f"Error loading characters: {e}")
