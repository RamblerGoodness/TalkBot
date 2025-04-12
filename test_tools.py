import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from character import Character

def test_tool_calling():
    """Script to test the LLM's tool calling capabilities"""
    print("==== LLM Tool Calling Test ====")
    
    # Create test character
    lyra = Character(
        name="Lyra",
        intro="*A shimmer in the air coalesces into a glowing figure. She smiles.*",
        background="Once a guardian of ancient celestial archives, now wandering worlds in search of lost stories. She has extensive knowledge about cosmic phenomena and enjoys using tools to demonstrate her abilities.",
        profile="lyra",
        db_name="lyra_memories_test",
        user_name="Tester",
        user_persona="A software developer testing Lyra's tool capabilities.",
        msgs_per_time_change=5  # Set higher to avoid automatic time changes during testing
    )
    
    # Set initial time
    lyra.set_time(day=1, time_of_day="morning")
    
    # Test prompts designed to elicit tool usage
    test_prompts = [
        "Lyra, can you tell me what time it is in the real world?",
        "I'm planning a trip to Tokyo. What's the weather like there?",
        "Let's play a game. Pick a random number between 1 and 100.",
        "Can you use multiple tools in one response? Tell me the time and the weather in New York.",
        "It's getting late. I think we should continue our conversation tomorrow morning. [This should trigger time change]",
        "Tell me about your advanced capabilities to interact with the world."
    ]
    
    print("Starting test - this may take a moment as responses are generated...")
    # Run tests with manual confirmation between each test
    for i, prompt in enumerate(test_prompts):
        input(f"\nPress Enter to run Test {i+1}: \"{prompt}\"...")
        print(f"\n--- Test {i+1}: {prompt} ---")
        try:
            response = lyra.talk(prompt, auto_advance=False)  # Disable auto time advancing
            print(f"Lyra: {response}")
            print(f"Current time: Day {lyra.current_day}, {lyra.time_of_day}")
        except Exception as e:
            print(f"Error during test: {str(e)}")
        
    print("\n==== Test completed ====")

if __name__ == "__main__":
    test_tool_calling()