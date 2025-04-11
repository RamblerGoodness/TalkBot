from character import Character

class CharacterPool:
    def __init__(self):
        self.characters = {}

    def add_character(self, character: Character):
        self.characters[character.name] = character

    def get_character(self, name):
        return self.characters.get(name)

    def remove_character(self, name):
        if name in self.characters:
            del self.characters[name]

    def list_characters(self):
        return list(self.characters.values())
