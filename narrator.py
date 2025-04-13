import random
import ollama
import threading
import time
from character import Character
from typing import List, Dict, Any, Tuple, Optional, Callable

class Narrator:
    def __init__(self, model_name="dolphin3"):
        self.characters = {}  # Dictionary mapping character names to Character instances
        self.story_state = {
            "plot_points": [],  # Key plot points that have occurred
            "scene": "start",   # Current scene identifier
            "characters_present": [],  # Characters in the current scene
            "themes": [],       # Ongoing themes in the story
            "day": 1,           # Story timeline day
            "time_of_day": "morning"  # Current time of day
        }
        self.last_speaking_character = None  # Keep track of who spoke last
        self.model = model_name  # LLM to use
        self.user_name = "Guest"
        self.user_persona = "A curious visitor to the story."
        self.is_processing = False  # Flag to prevent multiple simultaneous LLM calls
    
    def add_character(self, character: Character) -> None:
        """Add a character to the pool of available characters"""
        self.characters[character.name] = character
        
        # Sync character time with narrator time
        character.current_day = self.story_state["day"]
        character.time_of_day = self.story_state["time_of_day"]
        
        # If not already present, add to the scene
        if character.name not in self.story_state["characters_present"]:
            self.story_state["characters_present"].append(character.name)
    
    def remove_character(self, character_name: str) -> None:
        """Remove a character from the narrator's pool"""
        if character_name in self.characters:
            del self.characters[character_name]
            
        # Also remove from current scene if present
        if character_name in self.story_state["characters_present"]:
            self.story_state["characters_present"].remove(character_name)
    
    def set_scene(self, scene_name: str, characters_present: List[str]) -> None:
        """Set the current scene and characters present"""
        self.story_state["scene"] = scene_name
        self.story_state["characters_present"] = [
            char for char in characters_present if char in self.characters
        ]
    
    def add_plot_point(self, plot_point: str) -> None:
        """Add a significant plot point to the story state"""
        self.story_state["plot_points"].append(plot_point)
    
    def advance_time(self) -> None:
        """Advance time for the narrator and all characters"""
        # Use Character's time constants for consistency
        valid_times = Character.VALID_TIMES
        current_index = valid_times.index(self.story_state["time_of_day"])
        
        if current_index < len(valid_times) - 1:
            self.story_state["time_of_day"] = valid_times[current_index + 1]
        else:
            self.story_state["time_of_day"] = valid_times[0]
            self.story_state["day"] += 1
        
        # Sync all characters to the new time
        for character in self.characters.values():
            character.current_day = self.story_state["day"]
            character.time_of_day = self.story_state["time_of_day"]
    
    def set_user_persona(self, name: str, persona: str) -> None:
        """Set the user's persona for all character interactions"""
        self.user_name = name
        self.user_persona = persona
        
        # Update all characters with this information
        for character in self.characters.values():
            character.user_name = name
            character.user_persona = persona
    
    def select_responding_character(self, user_message: str) -> Tuple[str, float]:
        """
        Select which character should respond to the user message
        Returns character name and confidence score
        """
        # If no characters present, can't select any
        if not self.story_state["characters_present"]:
            return None, 0.0
            
        # If only one character, that character responds
        if len(self.story_state["characters_present"]) == 1:
            return self.story_state["characters_present"][0], 1.0
            
        # If user addresses a specific character by name
        for char_name in self.story_state["characters_present"]:
            if char_name.lower() in user_message.lower():
                return char_name, 0.9
        
        # Without LLM, use a simplified approach if we're waiting for LLM
        if self.is_processing:
            # Choose randomly, but avoid the last speaking character if possible
            available_chars = [c for c in self.story_state["characters_present"] 
                             if c != self.last_speaking_character or len(self.story_state["characters_present"]) == 1]
            return random.choice(available_chars), 0.5
            
        # Use the LLM to decide which character should respond
        try:
            self.is_processing = True
            
            context = [
                {"role": "system", "content": f"""You are a narrative director deciding which character should respond next in this scene.
Characters present: {', '.join(self.story_state["characters_present"])}
Current scene: {self.story_state["scene"]}
Last speaking character: {self.last_speaking_character if self.last_speaking_character else 'None'}
Current time: Day {self.story_state["day"]}, {self.story_state["time_of_day"]}

Consider the following when making your decision:
1. Which character would most naturally respond to this message?
2. Who has expertise or interest in what the user is talking about?
3. Try to balance dialogue between characters
4. Avoid having the same character respond too many times in a row unless it makes narrative sense

Return ONLY the name of the character who should respond next, no other text."""},
                {"role": "user", "content": f"Based on this user message, which character should respond next? Message: '{user_message}'"}
            ]

            response = ollama.chat(
                model=self.model,
                messages=context,
                options={"temperature": 0.3, "num_predict": 30}  # Low temperature for more deterministic output
            )
            
            response_text = response.get("message", {}).get("content", "").strip()
            
            # Find which character name appears in the response
            for char_name in self.story_state["characters_present"]:
                if char_name.lower() in response_text.lower():
                    self.is_processing = False
                    return char_name, 0.8
                    
            # Fallback to random selection from characters in scene with lower confidence
            self.is_processing = False
            return random.choice(self.story_state["characters_present"]), 0.6
            
        except Exception as e:
            print(f"Error in character selection: {e}")
            # Fallback to random if LLM fails
            self.is_processing = False
            return random.choice(self.story_state["characters_present"]), 0.4
    
    def process_user_message(self, user_message: str) -> Dict[str, Any]:
        """Process a user message and get a character response"""
        if not self.characters or not self.story_state["characters_present"]:
            return {
                "response": "There are no characters in the current scene. Please add characters first.",
                "character": None,
                "confidence": 0,
                "is_narrator": True
            }
            
        # Process special commands
        if user_message.startswith("/"):
            return self._handle_command(user_message)
            
        # Select which character should respond
        char_name, confidence = self.select_responding_character(user_message)
        
        if not char_name or char_name not in self.characters:
            return {
                "response": f"No character selected to respond. Available characters: {', '.join(self.story_state['characters_present'])}",
                "character": None,
                "confidence": 0,
                "is_narrator": True
            }
            
        character = self.characters[char_name]
        
        # Set user info on character before responding
        character.user_name = self.user_name
        character.user_persona = self.user_persona
        
        # Get response from the selected character
        response = character.talk(user_message, auto_advance=False)
        
        # Remember who spoke last
        self.last_speaking_character = char_name
        
        return {
            "response": response,
            "character": char_name,
            "confidence": confidence,
            "is_narrator": False,
            "day": self.story_state["day"],
            "time_of_day": self.story_state["time_of_day"]
        }
    
    def _handle_command(self, command: str) -> Dict[str, Any]:
        """Handle special narrator commands"""
        command = command.lower()
        
        if command.startswith("/scene "):
            # Set a new scene
            scene_desc = command[7:].strip()
            self.story_state["scene"] = scene_desc
            return {
                "response": f"*The scene changes to: {scene_desc}*",
                "is_narrator": True
            }
            
        elif command.startswith("/add "):
            # Add a character to the scene
            char_name = command[5:].strip()
            if char_name in self.characters:
                if char_name not in self.story_state["characters_present"]:
                    self.story_state["characters_present"].append(char_name)
                    return {
                        "response": f"*{char_name} enters the scene*",
                        "is_narrator": True
                    }
                else:
                    return {
                        "response": f"*{char_name} is already in the scene*",
                        "is_narrator": True
                    }
            else:
                return {
                    "response": f"*Character '{char_name}' not found. Available characters: {', '.join(self.characters.keys())}*",
                    "is_narrator": True
                }
                
        elif command.startswith("/remove "):
            # Remove a character from the scene
            char_name = command[8:].strip()
            if char_name in self.story_state["characters_present"]:
                self.story_state["characters_present"].remove(char_name)
                return {
                    "response": f"*{char_name} leaves the scene*",
                    "is_narrator": True
                }
            else:
                return {
                    "response": f"*{char_name} is not in the current scene*",
                    "is_narrator": True
                }
                
        elif command == "/time next":
            # Advance time
            self.advance_time()
            return {
                "response": f"*Time advances to {self.story_state['time_of_day']}, Day {self.story_state['day']}*",
                "is_narrator": True,
                "day": self.story_state["day"],
                "time_of_day": self.story_state["time_of_day"]
            }
            
        elif command == "/characters":
            # List available characters
            all_chars = list(self.characters.keys())
            present_chars = self.story_state["characters_present"]
            return {
                "response": f"*Characters in scene: {', '.join(present_chars)}\nAll available characters: {', '.join(all_chars)}*",
                "is_narrator": True
            }
            
        elif command == "/help":
            # Show available commands
            return {
                "response": """*Available narrator commands:*
/scene [description] - Set a new scene
/add [character] - Add a character to the scene
/remove [character] - Remove a character from the scene
/time next - Advance to the next time of day
/characters - List all available characters
/help - Show this help message""",
                "is_narrator": True
            }
            
        else:
            return {
                "response": "*Unknown command. Type /help for available commands.*",
                "is_narrator": True
            }
    
    def direct_scene(self, prompt: str = None) -> Dict[str, Any]:
        """Generate a narrative direction or scene description"""
        # If already processing a request, return a placeholder
        if self.is_processing:
            return {
                "response": "*The narrator is still contemplating the scene...*",
                "is_narrator": True,
                "day": self.story_state["day"],
                "time_of_day": self.story_state["time_of_day"]
            }
            
        context = [
            {"role": "system", "content": f"""You are a skilled narrative director providing storytelling direction.
Current scene: {self.story_state["scene"]}
Characters present: {', '.join(self.story_state["characters_present"])}
Current time: Day {self.story_state["day"]}, {self.story_state["time_of_day"]}
Plot points: {', '.join(self.story_state["plot_points"]) if self.story_state["plot_points"] else "None yet"}

Write a brief but evocative narrative description that:
1. Sets the scene and atmosphere
2. Mentions the characters present and what they're doing
3. Suggests possible directions for the story
4. Respects the established tone and timeline

Your narration should encourage further interaction while providing structure to the roleplay."""},
            {"role": "user", "content": prompt if prompt else "Provide a narrative direction for the current scene."}
        ]

        try:
            self.is_processing = True
            response = ollama.chat(
                model=self.model,
                messages=context,
                options={"temperature": 0.7, "num_predict": 300}
            )
            
            narration = response.get("message", {}).get("content", "")
            self.is_processing = False
            
            return {
                "response": narration,
                "is_narrator": True,
                "day": self.story_state["day"],
                "time_of_day": self.story_state["time_of_day"]
            }
            
        except Exception as e:
            print(f"Error generating narration: {e}")
            self.is_processing = False
            return {
                "response": "*The narrator pauses, contemplating the scene...*",
                "is_narrator": True,
                "day": self.story_state["day"],
                "time_of_day": self.story_state["time_of_day"]
            }
    
    def suggest_new_character(self, context_prompt: str) -> Dict[str, Any]:
        """Suggest a new character based on the story context"""
        # If already processing a request, return a placeholder
        if self.is_processing:
            return {
                "response": "*The narrator is still considering potential characters...*",
                "is_narrator": True
            }
        
        self.is_processing = True
        
        system_prompt = f"""Based on the current story context, suggest a new character who would fit well in this narrative world.
Current scene: {self.story_state["scene"]}
Characters present: {', '.join(self.story_state["characters_present"])}
Plot points: {', '.join(self.story_state["plot_points"]) if self.story_state["plot_points"] else "None yet"}

Generate a complete character profile with:
1. Name
2. Introduction (how they first appear)
3. Background/personality
4. Appearance description

Format your response as a structured character profile ONLY - no explanations or additional text."""

        try:
            context = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context_prompt if context_prompt else "Suggest a new character who would complement the current story."}
            ]
            
            # Start in a non-blocking thread
            def get_suggestion_async(callback):
                try:
                    response = ollama.chat(
                        model=self.model,
                        messages=context,
                        options={"temperature": 0.8, "num_predict": 500}
                    )
                    
                    character_suggestion = response.get("message", {}).get("content", "")
                    callback(character_suggestion)
                except Exception as e:
                    print(f"Error in async character suggestion: {e}")
                    callback(None)
                finally:
                    self.is_processing = False
            
            # Start process in background
            threading.Thread(target=get_suggestion_async, args=(lambda x: None,)).start()
            
            # Return immediately with a processing message
            return {
                "response": "*The narrator is considering what new character might fit in this story...*",
                "is_narrator": True,
                "processing": True
            }
            
        except Exception as e:
            print(f"Error suggesting character: {e}")
            self.is_processing = False
            return {
                "response": "*Unable to generate character suggestion at this time.*",
                "is_narrator": True
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert narrator state to dictionary for storage"""
        return {
            "story_state": self.story_state,
            "last_speaking_character": self.last_speaking_character,
            "user_name": self.user_name,
            "user_persona": self.user_persona,
            "model": self.model
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Narrator':
        """Create a narrator from a dictionary"""
        narrator = Narrator(model_name=data.get("model", "dolphin3"))
        narrator.story_state = data.get("story_state", narrator.story_state)
        narrator.last_speaking_character = data.get("last_speaking_character")
        narrator.user_name = data.get("user_name", "Guest")
        narrator.user_persona = data.get("user_persona", "A curious visitor to the story.")
        return narrator
