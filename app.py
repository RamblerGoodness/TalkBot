from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from character import Character
from character_pool import CharacterPool
from persona import Persona
import os
import json

app = Flask(__name__, static_folder=os.path.abspath('.'))
CORS(app)

# Initialize character pool
character_pool = CharacterPool()

# Add initial characters
character_pool.add_character(Character(
    name="Lyra",
    intro="*A shimmer in the air coalesces into a glowing figure. She smiles.*",
    background="Once a guardian of ancient celestial archives, now wandering worlds in search of lost stories.",
    profile="lyra",
    db_name="lyra_memories",
    user_name="Guest",
    user_persona="A curious visitor to the website.",
    msgs_per_time_change=1  # Default: advance time every message
))
# Add more characters as needed

# Set initial time for all characters
for character in character_pool.list_characters():
    character.set_time(day=1, time_of_day="morning")

PERSONA_FILE = "personas.json"

def load_personas():
    if os.path.exists(PERSONA_FILE):
        with open(PERSONA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {p['name']: Persona(p['name'], p['description']) for p in data}
    return {}

def save_personas():
    with open(PERSONA_FILE, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in personas.values()], f, indent=2)

# In-memory persona store for prototype
personas = load_personas()

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
    for char in character_pool.list_characters():
        character_list.append({
            "name": char.name,
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
    character = character_pool.get_character(data['character'])
    if not character:
        return jsonify({"error": f"Character {data['character']} not found"}), 404
    message = data['message']
    # Persona support
    persona_name = data.get('persona')
    if persona_name and persona_name in personas:
        persona = personas[persona_name]
        character.user_name = persona.name
        character.user_persona = persona.description
    else:
        character.user_name = "Guest"
        character.user_persona = "A curious visitor to the website."
    # Custom time mechanic: set day/time_of_day from frontend if provided
    if 'day' in data and isinstance(data['day'], int):
        character.current_day = data['day']
    if 'time_of_day' in data and isinstance(data['time_of_day'], str):
        if data['time_of_day'] in character.VALID_TIMES:
            character.time_of_day = data['time_of_day']
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
    character = character_pool.get_character(data['character'])
    if not character:
        return jsonify({"error": f"Character {data['character']} not found"}), 404
    action = data['action']
    try:
        if action == 'next_time':
            character.advance_time()
        elif action == 'prev_time':
            current_index = character.VALID_TIMES.index(character.time_of_day)
            if current_index > 0:
                character.time_of_day = character.VALID_TIMES[current_index - 1]
            else:
                character.time_of_day = character.VALID_TIMES[-1]
                if character.current_day > 1:
                    character.current_day -= 1
        elif action == 'next_day':
            character.current_day += 1
            character.time_of_day = character.VALID_TIMES[0]
        elif action == 'prev_day':
            if character.current_day > 1:
                character.current_day -= 1
                character.time_of_day = character.VALID_TIMES[0]
        else:
            return jsonify({"error": f"Invalid action: {action}"}), 400
        return jsonify({
            "day": character.current_day,
            "time_of_day": character.time_of_day
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/personas', methods=['GET'])
def get_personas():
    return jsonify({"personas": [p.to_dict() for p in personas.values()]})

@app.route('/persona', methods=['POST'])
def create_persona():
    data = request.json
    if not data or 'name' not in data or 'description' not in data:
        return jsonify({"error": "Missing name or description"}), 400
    persona = Persona(data['name'], data['description'])
    personas[data['name']] = persona
    save_personas()
    return jsonify(persona.to_dict()), 201

@app.route('/persona/<name>', methods=['PUT'])
def edit_persona(name):
    data = request.json
    if name not in personas:
        return jsonify({"error": "Persona not found"}), 404
    if not data or 'description' not in data:
        return jsonify({"error": "Missing description"}), 400
    personas[name].description = data['description']
    save_personas()
    return jsonify(personas[name].to_dict())

@app.route('/persona/<name>', methods=['DELETE'])
def delete_persona(name):
    if name not in personas:
        return jsonify({"error": "Persona not found"}), 404
    del personas[name]
    save_personas()
    return '', 204

@app.route('/character', methods=['POST'])
def create_character():
    """Create a new character"""
    data = request.json
    if not data or 'name' not in data or 'intro' not in data or 'background' not in data or 'profile' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if character already exists
    if character_pool.get_character(data['name']):
        return jsonify({"error": f"Character '{data['name']}' already exists"}), 400
    
    try:
        # Create a new character
        new_character = Character(
            name=data['name'],
            intro=data['intro'],
            background=data['background'],
            profile=data['profile'],
            db_name=f"{data['name'].lower()}_memories",
            user_name="Guest",
            user_persona="A curious visitor to the website.",
            msgs_per_time_change=1
        )
        
        # Add to character pool
        character_pool.add_character(new_character)
        
        # Set initial time
        new_character.set_time(day=1, time_of_day="morning")
        
        return jsonify({"success": True, "name": data['name']}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)