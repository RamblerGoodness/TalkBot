import random
import json
import os
import ollama
import chromadb
import re
import datetime
from memory import ShortTermMemory, LongTermMemory


class Character:
    VALID_TIMES = ["early_morning", "morning", "afternoon", "evening", "night"]

    def __init__(self, name, intro, background, profile, db_name, user_name, user_persona, msgs_per_time_change=1):
        self.name = name
        self.intro = intro
        self.background = background
        # Fix path with forward slashes instead of backslashes for web compatibility
        self.profile = f"page/image/{profile}.png"
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory(db_path=f"{db_name}_chroma")
        self.model = "dolphin3"
        self.current_day = 1
        self.time_of_day = "morning"
        self.user_name = user_name
        self.user_persona = user_persona
        self.msgs_per_time_change = msgs_per_time_change
        self.message_count = 0

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
        self.short_term_memory.add(message, time_since_last, self.current_day, self.time_of_day)

    def summarize_and_store_memory(self):
        if not self.short_term_memory.entries:
            return

        messages = [item["message"] for item in self.short_term_memory.entries]
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
            self.long_term_memory.add(memory_id, summary, self.current_day, self.time_of_day)
            self.short_term_memory.clear()

    def query_long_term_memory(self, prompt):
        return self.long_term_memory.query(prompt)

    def build_context(self, prompt):
        system_prompt = {
            "role": "system",
            "content": (
                f"You are {self.name}, an AI character in a roleplay system. "
                f"Stay in character as {self.name} at all times. "
                f"Your background: {self.background} "
                f"Respond in {self.name}'s style and voice. "
                f"The user is {self.user_name}: {self.user_persona}. "
                f"Do not break character or refer to yourself as an AI.\n\n"
                f"You can call tools by using specific syntax in your responses:\n"
                f"1. To advance time: [change_time:next_time] or [change_time:next_day]\n"
                f"2. To get current time: [tool:get_current_time]\n"
                f"3. To generate random number: [tool:random_number:min:max]\n"
                f"4. To access weather: [tool:get_weather:location]\n"
                f"Use these tools only when appropriate in conversation."
            )
        }
        short_mem = self.short_term_memory.get_recent()
        long_mem = self.query_long_term_memory(prompt)
        long_mem_messages = [{"role": "system", "content": mem} for mem in long_mem]
        context = [system_prompt] + long_mem_messages + short_mem + [
            {"role": "user", "content": f"{self.user_name}: {prompt}"}
        ]
        return context

    def talk(self, user_message, time_since_last="unknown", auto_advance=True):
        self.remember_message({"role": "user", "content": f"{self.user_name}: {user_message}"}, time_since_last)
        
        # Check for time control commands
        time_command = self.check_for_time_commands(user_message)
        if time_command:
            return time_command
            
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
        
        # Check for all tool calls in the response
        processed_reply = self.process_tool_calls(reply)
        
        self.remember_message({"role": "assistant", "content": processed_reply}, "0s")
        
        # Auto-advance time based on message count if enabled
        if auto_advance:
            self.message_count += 1
            if self.message_count >= self.msgs_per_time_change:
                self.advance_time()
                self.message_count = 0
            
        return processed_reply
        
    def process_tool_calls(self, reply):
        """Process all tool calls in the AI's reply"""
        # First check for time commands (for backward compatibility)
        time_command = self.check_for_ai_time_commands(reply)
        if time_command:
            self.execute_time_command(time_command)
            # Remove the time command from the reply
            reply = re.sub(r'\[change_time:.*?\]', '', reply).strip()
        
        # Now check for general tool calls
        tool_pattern = r'\[tool:(.*?)\]'
        tool_matches = re.finditer(tool_pattern, reply)
        
        for match in tool_matches:
            tool_call = match.group(1)
            tool_result = self.execute_tool_call(tool_call)
            
            # Replace the tool call with its result
            if tool_result is not None:
                reply = reply.replace(match.group(0), tool_result)
            else:
                # If tool execution failed, just remove the tool call
                reply = reply.replace(match.group(0), "")
                
        return reply
    
    def execute_tool_call(self, tool_call):
        """Execute a general tool call from the AI"""
        parts = tool_call.split(':')
        tool_name = parts[0].strip()
        
        try:
            if tool_name == "get_current_time":
                return self.tool_get_current_time()
                
            elif tool_name == "random_number" and len(parts) >= 3:
                try:
                    min_val = int(parts[1].strip())
                    max_val = int(parts[2].strip())
                    return self.tool_random_number(min_val, max_val)
                except ValueError:
                    return f"*Error: random_number tool requires integer values*"
                
            elif tool_name == "get_weather" and len(parts) >= 2:
                location = ':'.join(parts[1:])  # Join all remaining parts in case location contains ':'
                location = location.strip()
                return self.tool_get_weather(location)
                
            else:
                return f"*Tool '{tool_name}' not found or missing parameters*"
                
        except Exception as e:
            return f"*Error executing tool '{tool_name}': {str(e)}*"
    
    def tool_get_current_time(self):
        """Tool: Get the current real-world time"""
        now = datetime.datetime.now()
        return now.strftime("%I:%M %p on %A, %B %d, %Y")
    
    def tool_random_number(self, min_val, max_val):
        """Tool: Generate a random number between min and max"""
        if min_val > max_val:
            min_val, max_val = max_val, min_val
        result = random.randint(min_val, max_val)
        return str(result)
    
    def tool_get_weather(self, location):
        """Tool: Simulate getting weather for a location"""
        # This is a simulated weather tool (no real API call)
        weather_options = ["sunny", "cloudy", "rainy", "stormy", "windy", "snowy", "foggy"]
        temperatures = {"sunny": (75, 95), "cloudy": (60, 80), "rainy": (50, 70),
                       "stormy": (55, 75), "windy": (50, 70), "snowy": (20, 35), "foggy": (45, 65)}
        
        # Use location as seed for deterministic but varied results
        seed = sum(ord(c) for c in location) + self.current_day
        random.seed(seed)
        
        weather = random.choice(weather_options)
        temp_range = temperatures[weather]
        temp = random.randint(temp_range[0], temp_range[1])
        
        # Reset random seed
        random.seed()
        
        return f"In {location}, it's currently {weather} with a temperature of {temp}°F"

    def check_for_time_commands(self, message):
        """Check if the user message contains time control commands"""
        lower_msg = message.lower()
        
        if "/time next" in lower_msg:
            self.advance_time()
            return f"*Time advances to {self.time_of_day}, Day {self.current_day}*"
            
        elif "/time previous" in lower_msg:
            current_index = self.VALID_TIMES.index(self.time_of_day)
            if current_index > 0:
                self.time_of_day = self.VALID_TIMES[current_index - 1]
            else:
                self.time_of_day = self.VALID_TIMES[-1]
                if self.current_day > 1:
                    self.current_day -= 1
            return f"*Time rolls back to {self.time_of_day}, Day {self.current_day}*"
            
        elif "/day next" in lower_msg:
            self.current_day += 1
            self.time_of_day = self.VALID_TIMES[0]
            return f"*A new day begins. It is now {self.time_of_day}, Day {self.current_day}*"
            
        elif "/day previous" in lower_msg:
            if self.current_day > 1:
                self.current_day -= 1
                return f"*Going back to Day {self.current_day}, {self.time_of_day}*"
            return "*You can't go back before Day 1*"
            
        elif "/set messages" in lower_msg:
            try:
                # Extract number from command like "/set messages 3"
                num = int(re.search(r'/set messages (\d+)', lower_msg).group(1))
                self.msgs_per_time_change = num
                return f"*Time will now advance every {num} messages*"
            except:
                return "*Invalid format. Use '/set messages X' where X is a number*"
                
        return None
        
    def check_for_ai_time_commands(self, reply):
        """Check if the AI reply contains time control commands in format [change_time:command]"""
        match = re.search(r'\[change_time:(.*?)\]', reply)
        if match:
            return match.group(1).strip()
        return None
        
    def execute_time_command(self, command):
        """Execute a time command from the AI"""
        command = command.lower()
        
        if command == "next_time":
            self.advance_time()
        elif command == "next_day":
            self.current_day += 1
            self.time_of_day = self.VALID_TIMES[0]
        # Additional commands could be added here

    def to_dict(self):
        return {
            "name": self.name,
            "intro": self.intro,
            "background": self.background,
            "profile": self.profile,
            "shortTermMemory": self.short_term_memory.entries,
            "current_day": self.current_day,
            "time_of_day": self.time_of_day
        }

    def test_tool_calls(self):
        """Test the tool calling functionality directly"""
        print(f"\n--- Testing tool calling functionality for {self.name} ---")
        
        # Test get_current_time
        print("Testing get_current_time tool:")
        time_result = self.execute_tool_call("get_current_time")
        print(f"Result: {time_result}")
        
        # Test random_number
        print("\nTesting random_number tool:")
        random_result = self.execute_tool_call("random_number:1:100")
        print(f"Result: {random_result}")
        
        # Test get_weather
        print("\nTesting get_weather tool:")
        weather_result = self.execute_tool_call("get_weather:Tokyo")
        print(f"Result: {weather_result}")
        
        # Test error handling
        print("\nTesting invalid tool:")
        invalid_result = self.execute_tool_call("invalid_tool")
        print(f"Result: {invalid_result}")
        
        # Test parameter error handling
        print("\nTesting invalid parameters:")
        invalid_params = self.execute_tool_call("random_number:abc:def")
        print(f"Result: {invalid_params}")
        
        print("\n--- Tool testing completed ---")
        return "Tool testing completed"


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
        user_persona="A curious adventurer seeking knowledge about the universe.",
        msgs_per_time_change=3
    )
    test_character.set_time(day=3, time_of_day="evening")

    session = SingleCharacterMode(test_character)
    session.run()