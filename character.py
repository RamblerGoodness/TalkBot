import random
import json
import os
import ollama
import chromadb


class Character:
    VALID_TIMES = ["early_morning", "morning", "afternoon", "evening", "night"]

    def __init__(self, name, intro, background, profile, db_name, user_name, user_persona):
        self.name = name
        self.intro = intro
        self.background = background
        # Fix path with forward slashes instead of backslashes for web compatibility
        self.profile = f"page/image/{profile}.png"
        self.shortTermMemory = []
        self.model = "dolphin3"
        self.current_day = 1
        self.time_of_day = "morning"
        self.user_name = user_name
        self.user_persona = user_persona

        # Initialize ChromaDB client and collection with updated configuration
        self.chroma_client = chromadb.PersistentClient(path=f"{db_name}_chroma")
        self.memory_collection = self.chroma_client.get_or_create_collection(name="memories")

    def set_time(self, day, time_of_day):
        if time_of_day not in self.VALID_TIMES:
            raise ValueError(f"Invalid time_of_day. Must be one of: {', '.join(self.VALID_TIMES)}")
        self.current_day = day
        self.time_of_day = time_of_day

    def advance_time(self):
        current_index = self.VALID_TIMES.index(self.time_of_day)
        if current_index < len(self.VALID_TIMES) - 1:
            self.time_of_day = self.VALID_TIMES[current_index + 1]
        else:
            self.time_of_day = self.VALID_TIMES[0]
            self.current_day += 1

    def remember_message(self, message, time_since_last):
        self.shortTermMemory.append({
            "message": message,
            "time_delta": time_since_last,
            "day": self.current_day,
            "time_of_day": self.time_of_day
        })
        if len(self.shortTermMemory) > 20:
            self.shortTermMemory.pop(0)

    def summarize_and_store_memory(self):
        if not self.shortTermMemory:
            return

        messages = [item["message"] for item in self.shortTermMemory]
        context = [{"role": "system", "content": "Summarize the following conversation into a long-term memory."}] + messages

        # Add token limit to Ollama call (max 150 tokens for summaries)
        response = ollama.chat(
            model=self.model, 
            messages=context,
            options={
                "num_predict": 150,  # Limit token generation to 150 tokens
                "temperature": 0.7   # Keep a moderate temperature for summaries
            }
        )
        summary = response.get("message", {}).get("content", None)

        if summary:
            memory_id = f"day_{self.current_day}_time_{self.time_of_day}"
            self.memory_collection.add(
                ids=[memory_id],
                metadatas=[{"day": self.current_day, "time_of_day": self.time_of_day}],
                documents=[summary]
            )
            self.shortTermMemory.clear()

    def query_long_term_memory(self, prompt):
        results = self.memory_collection.query(
            query_texts=[prompt],
            n_results=2
        )
        return results.get("documents", [])

    def build_context(self, prompt):
        system_prompt = {
            "role": "system",
            "content": f"{self.name}: {self.background}\nUser ({self.user_name}): {self.user_persona}"
        }
        short_mem = [item["message"] for item in self.shortTermMemory[-8:]]
        long_mem = self.query_long_term_memory(prompt)
        long_mem_messages = [{"role": "system", "content": mem} for mem in long_mem]
        context = [system_prompt] + long_mem_messages + short_mem + [
            {"role": "user", "content": f"{self.user_name}: {prompt}"}
        ]
        return context

    def talk(self, user_message, time_since_last="unknown"):
        self.remember_message({"role": "user", "content": f"{self.user_name}: {user_message}"}, time_since_last)
        context = self.build_context(user_message)
        
        # Add token limit and response parameters
        response = ollama.chat(
            model=self.model, 
            messages=context,
            options={
                "num_predict": 250,  # Limit token generation to 250 tokens for character responses
                "temperature": 0.8,  # Slightly higher temperature for more creative character responses
                "top_p": 0.9,        # Nucleus sampling for more natural responses
                "top_k": 40          # Limit vocabulary diversity while keeping responses interesting
            }
        )
        
        reply = response.get("message", {}).get("content", "No response")
        self.remember_message({"role": "assistant", "content": reply}, "0s")
        return reply

    def to_dict(self):
        return {
            "name": self.name,
            "intro": self.intro,
            "background": self.background,
            "profile": self.profile,
            "shortTermMemory": self.shortTermMemory,
            "current_day": self.current_day,
            "time_of_day": self.time_of_day
        }


class SingleCharacterMode:
    def __init__(self, character):
        self.character = character

    def interact(self, user_input):
        if user_input.lower().startswith("switch_user"):
            print("Switching user...")
            new_name = input("Enter the new name: ")
            new_persona = input("Describe the new persona: ")
            self.character.user_name = new_name
            self.character.user_persona = new_persona
            print(f"User switched to {new_name} with persona: {new_persona}")
            return f"User switched to {new_name}."
        reply = self.character.talk(user_input)
        self.character.advance_time()
        return reply

    def run(self):
        print(self.character.intro)
        # Prompt the user for their name and persona
        user_name = input("Enter your name: ")
        user_persona = input("Describe your persona: ")
        self.character.user_name = user_name
        self.character.user_persona = user_persona
        print(f"Welcome, {user_name}! You are now interacting with {self.character.name}.")
        print("If you want to switch users, type 'switch_user' followed by your new name and persona. Type 'exit' or 'quit' to end the conversation.")
        print("If you want to quit, type 'exit' or 'quit'.")

        try:
            while True:
                user_input = input(f"{user_name}: ")
                if user_input.lower() in ("exit", "quit"):
                    break
                reply = self.interact(user_input)
                print(f"{self.character.name}: {reply}")
        finally:
            # Removed the unnecessary persist call
            pass


if __name__ == "__main__":
    test_character = Character(
        name="Lyra",
        intro="*A shimmer in the air coalesces into a glowing figure. She smiles.*",
        background="Once a guardian of ancient celestial archives, now wandering worlds in search of lost stories.",
        profile="lyra",
        db_name="lyra_memories",
        user_name="Alex",
        user_persona="A curious adventurer seeking knowledge about the universe."
    )
    test_character.set_time(day=3, time_of_day="evening")

    session = SingleCharacterMode(test_character)
    session.run()