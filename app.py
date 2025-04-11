from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from character import Character
import os

app = Flask(__name__, static_folder=os.path.abspath('.'))
CORS(app)  # Enable CORS for all routes

# Initialize characters
characters = {
    "Lyra": Character(
        name="Lyra",
        intro="*A shimmer in the air coalesces into a glowing figure. She smiles.*",
        background="Once a guardian of ancient celestial archives, now wandering worlds in search of lost stories.",
        profile="lyra",
        db_name="lyra_memories",
        user_name="Guest",
        user_persona="A curious visitor to the website."
    ),
    # Add more characters here as needed
}

# Initialize character states
for character in characters.values():
    character.set_time(day=1, time_of_day="morning")

# Route for serving the homepage
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Route for serving static files from the current directory
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# Route for serving files from the "page" directory
@app.route('/page/<path:path>')
def serve_page(path):
    return send_from_directory('page', path)

# Route for serving files from the "script" directory
@app.route('/script/<path:path>')
def serve_script(path):
    return send_from_directory('script', path)

# Route for serving files from the "style" directory
@app.route('/style/<path:path>')
def serve_style(path):
    return send_from_directory('style', path)

# Route for serving files from the "page/image" directory
@app.route('/page/image/<path:path>')
def serve_image(path):
    return send_from_directory('page/image', path)

@app.route('/characters', methods=['GET'])
def get_characters():
    """Get the list of available characters"""
    character_list = []
    for name, char in characters.items():
        character_list.append({
            "name": name,
            "intro": char.intro,
            "profile": char.profile
        })
    return jsonify({"characters": character_list})

@app.route('/chat', methods=['POST'])
def chat():
    """Process a chat message and get a response"""
    data = request.json
    if not data or 'message' not in data or 'character' not in data:
        return jsonify({"error": "Missing message or character parameter"}), 400
    
    character_name = data['character']
    if character_name not in characters:
        return jsonify({"error": f"Character {character_name} not found"}), 404
    
    character = characters[character_name]
    message = data['message']
    
    try:
        response = character.talk(message)
        character.advance_time()
        return jsonify({
            "response": response,
            "day": character.current_day,
            "time_of_day": character.time_of_day
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/character/time', methods=['POST'])
def update_time():
    """Update a character's time of day"""
    data = request.json
    if not data or 'character' not in data or 'action' not in data:
        return jsonify({"error": "Missing character or action parameter"}), 400
    
    character_name = data['character']
    if character_name not in characters:
        return jsonify({"error": f"Character {character_name} not found"}), 404
    
    character = characters[character_name]
    action = data['action']
    
    try:
        if action == 'next_time':
            character.advance_time()
        elif action == 'prev_time':
            # Find previous time
            current_index = character.VALID_TIMES.index(character.time_of_day)
            if current_index > 0:
                character.time_of_day = character.VALID_TIMES[current_index - 1]
            else:
                character.time_of_day = character.VALID_TIMES[-1]
                if character.current_day > 1:
                    character.current_day -= 1
        elif action == 'next_day':
            character.current_day += 1
            character.time_of_day = character.VALID_TIMES[0]  # Reset to early morning
        elif action == 'prev_day':
            if character.current_day > 1:
                character.current_day -= 1
                character.time_of_day = character.VALID_TIMES[0]  # Reset to early morning
        else:
            return jsonify({"error": f"Invalid action: {action}"}), 400
        
        return jsonify({
            "day": character.current_day,
            "time_of_day": character.time_of_day
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)