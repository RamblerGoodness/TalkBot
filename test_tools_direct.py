import sys
import os
from character import Character

def test_tools_directly():
    """Script to directly test the tool calling capabilities"""
    print("==== Direct LLM Tool Calling Test ====")
    
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
    
    # Run the direct tool testing
    lyra.test_tool_calls()

if __name__ == "__main__":
    test_tools_directly()