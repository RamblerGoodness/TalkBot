import json
import os
from narrator import Narrator
from character_pool import CharacterPool

class NarratorManager:
    NARRATORS_FILE = "narrators.json"
    
    def __init__(self, character_pool: CharacterPool):
        self.narrators = {}  # Dictionary mapping narrator IDs to Narrator instances
        self.character_pool = character_pool
        self.active_narrator_id = None
        self.load_narrators()
    
    def create_narrator(self, narrator_id: str, model_name: str = "dolphin3") -> Narrator:
        """Create a new narrator instance with the given ID"""
        if narrator_id in self.narrators:
            raise ValueError(f"Narrator with ID '{narrator_id}' already exists")
        
        narrator = Narrator(model_name=model_name)
        self.narrators[narrator_id] = narrator
        self.save_narrators()
        return narrator
    
    def get_narrator(self, narrator_id: str) -> Narrator:
        """Get a narrator by ID"""
        return self.narrators.get(narrator_id)
    
    def set_active_narrator(self, narrator_id: str) -> None:
        """Set the active narrator"""
        if narrator_id not in self.narrators:
            raise ValueError(f"Narrator with ID '{narrator_id}' not found")
        self.active_narrator_id = narrator_id
        self.save_narrators()
    
    def get_active_narrator(self) -> Narrator:
        """Get the currently active narrator"""
        if not self.active_narrator_id or self.active_narrator_id not in self.narrators:
            # If no active narrator or it doesn't exist, return None
            return None
        return self.narrators[self.active_narrator_id]
    
    def delete_narrator(self, narrator_id: str) -> None:
        """Delete a narrator by ID"""
        if narrator_id in self.narrators:
            del self.narrators[narrator_id]
            if self.active_narrator_id == narrator_id:
                self.active_narrator_id = None
            self.save_narrators()
    
    def add_character_to_narrator(self, narrator_id: str, character_name: str) -> bool:
        """Add a character from the character pool to a narrator"""
        narrator = self.get_narrator(narrator_id)
        character = self.character_pool.get_character(character_name)
        
        if not narrator or not character:
            return False
        
        narrator.add_character(character)
        self.save_narrators()
        return True
    
    def save_narrators(self) -> None:
        """Save all narrators to a JSON file"""
        narrators_data = {
            "active_narrator_id": self.active_narrator_id,
            "narrators": {}
        }
        
        for narrator_id, narrator in self.narrators.items():
            # We only save the narrator state, not the character objects
            # Characters will be referenced by name and loaded from character_pool when needed
            narrator_dict = narrator.to_dict()
            narrator_dict["character_names"] = list(narrator.characters.keys())
            narrators_data["narrators"][narrator_id] = narrator_dict
        
        with open(self.NARRATORS_FILE, "w", encoding="utf-8") as f:
            json.dump(narrators_data, f, indent=2)
    
    def load_narrators(self) -> None:
        """Load narrators from the JSON file if it exists"""
        if not os.path.exists(self.NARRATORS_FILE):
            return
        
        try:
            with open(self.NARRATORS_FILE, "r", encoding="utf-8") as f:
                narrators_data = json.load(f)
            
            self.active_narrator_id = narrators_data.get("active_narrator_id")
            
            for narrator_id, narrator_dict in narrators_data.get("narrators", {}).items():
                # Create narrator from the saved data
                narrator = Narrator.from_dict(narrator_dict)
                
                # Add characters from the character pool
                character_names = narrator_dict.get("character_names", [])
                for char_name in character_names:
                    character = self.character_pool.get_character(char_name)
                    if character:
                        narrator.add_character(character)
                
                self.narrators[narrator_id] = narrator
                
        except Exception as e:
            print(f"Error loading narrators: {e}")
    
    def list_narrators(self):
        """Return a list of narrator IDs and basic info"""
        return [
            {
                "id": narrator_id,
                "scene": narrator.story_state["scene"],
                "day": narrator.story_state["day"],
                "time_of_day": narrator.story_state["time_of_day"],
                "characters": list(narrator.characters.keys()),
                "is_active": narrator_id == self.active_narrator_id
            }
            for narrator_id, narrator in self.narrators.items()
        ]