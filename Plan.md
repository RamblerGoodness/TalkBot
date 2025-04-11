# 🌌 AI Roleplay System: Project Goals & Milestones

This project aims to create a rich, interactive storytelling platform powered by artificial intelligence. The system will support dynamic roleplay through two primary modes of engagement, AI characters with memory and personality, and customizable user personas for immersive participation.

---

## 🧭 Core Objectives

1. **AI-Powered Roleplay Characters**
   - Each character maintains a consistent personality, background, and conversational style.
   - Characters use short-term memory (recent dialogue) and long-term memory (persistent knowledge base) to inform behavior.

2. **Single Character Interaction Mode**
   - Users engage one-on-one with a chosen AI character.
   - The character evolves over time, influenced by memory updates and contextual history.

3. **Narrator-Controlled Mode**
   - A specialized Narrator AI manages the overarching story, selects responding characters, and steers the narrative.
   - The Narrator can generate new characters—with user approval—and oversee a cast of supporting NPCs.

4. **User Persona Framework**
   - Users can create custom personas for roleplay.
   - User personas do not require memory, as users can refer to previous chat history.

5. **Memory System Architecture**
   - Short-term memory stores the 20 most recent conversational entries.
   - Long-term memory captures ongoing knowledge for context retention and character development.

6. **Character Visual Identity**
   - Each character includes a profile image to enhance visual immersion.

---

## 📅 Development Milestones

| ID   | Milestone                            | Description                                                                 | Status         |
|------|--------------------------------------|-----------------------------------------------------------------------------|----------------|
| M1   | Character Core Class (MVP)           | Foundational character class with memory and profile functionality          | ✅ In Progress  |
| M2   | Single Character Mode                | Enable direct interaction with an individual AI character                   | ⏳ Planned      |
| M3   | Narrator AI Class                    | Create narrative director for story flow and character coordination         | ⏳ Planned      |
| M4   | Character Pool Management            | System for managing and accessing a collection of characters                | ⏳ Planned      |
| M5   | Dynamic Character Generation         | Allow Narrator to create new characters with user input                     | ⏳ Planned      |
| M6   | Memory Update Mechanism              | Automate updates to character memory over time and conversation             | ⏳ Planned      |
| M7   | Mode Switching System                | Enable smooth transition between Character and Narrator modes               | ⏳ Planned      |
| M8   | User Persona Integration             | Support for user-created personas with editable profiles                    | ⏳ Planned      |
| M9   | Persona Interaction Layer            | Allow personas to function across both interaction modes                    | ⏳ Planned      |

---

## 🧩 Secondary Objectives

- Provide quick-start character templates and archetypes
- Enable developer-facing tools for memory visualization and editing
- Integrate optional voice output (TTS)
- Prepare for future multiplayer or shared sessions
- Add features for saving, exporting, or logging conversations

---

## 🚀 Stretch Goals: Advanced & Immersive Features

- 🎨 **AI Image Generation**: Create visuals for characters, items, or scenes using generative models
- 🗺️ **Interactive World Maps**: Visualize locations and explore environments dynamically
- 🎲 **Dice & Random Events**: Implement systems for chance-based actions and outcomes
- 📘 **User Character Sheets**: Attach inventory, abilities, and stats to user personas
- 😄 **Emotion-Based Dialogue**: Enable characters to respond with dynamic tone or mood
- 📜 **Memory Journal / Narrative Timeline**: Track key story moments, decisions, and dialogue
- 🧪 **Prompt Playground / Scenario Builder**: Build and test story scenes interactively
- 🎙️ **Voice Output (TTS)**: Speak character dialogue for greater immersion

---

## 🏗️ System Architecture Overview

- **Character Module**: Python-based class containing character traits, memory, and visual identity.
- **User Personas**: Custom avatars defined by the user, without internal memory tracking.
- **Narrator AI**: Central storytelling agent that controls scene flow, character engagement, and story direction.

---

This document will continue to evolve in parallel with system development, supporting design decisions and progress tracking.
