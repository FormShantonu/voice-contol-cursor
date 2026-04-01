# Voice Control Cursor

This project currently includes:
- A speech recognition runner in app/main.py
- An LLM graph snippet in app/graph.py
- Optional MongoDB via Docker in docker-compose.yml

## Prerequisites

- Windows PowerShell
- Python 3.10+ installed
- Docker Desktop (optional, only if you need MongoDB)
- Microphone access enabled in Windows privacy settings

## Project Setup

1. Open PowerShell in the project root:
   - E:/AI Agent tutorial/voice contol cursor/voice-contol-cursor

2. Create a virtual environment (skip if .venv already exists):

   python -m venv .venv

3. Activate the virtual environment:

   .\.venv\Scripts\Activate.ps1

4. Install dependencies:

   pip install -r requireme.text

## Run The Speech Recognition Script

From the project root, with the virtual environment active:

python app/main.py

What to expect:
- The app prints: Say something!
- Speak into your microphone
- It prints recognized text or a friendly error message

## Optional: Start MongoDB With Docker

If your next features need MongoDB, start it with:

docker compose up -d mongodb

Stop it with:

docker compose down

## Optional: Use The Graph Module

app/graph.py uses LangGraph and OpenAI SDK integrations.
To use it, install missing packages if needed:

pip install langgraph langchain-openai

Then set your API key in PowerShell:

$env:OPENAI_API_KEY="your_api_key_here"

Note: graph.py currently defines graph-related components but does not include a direct executable main entry point.

## Troubleshooting

1. SpeechRecognition module missing
- Install:
  pip install SpeechRecognition

2. Microphone/backend errors on Windows
- Install PyAudio:
  pip install PyAudio
- If PyAudio install fails from source, use a compatible wheel for your Python version.

3. No speech detected
- Speak within 10 seconds because timeout and phrase time limit are set in app/main.py.

4. Could not understand audio
- Try a quieter room and speak more clearly.

5. Request error from Google Speech Recognition
- Check internet connection and retry.

## File References

- Speech entry point: app/main.py
- Graph module: app/graph.py
- Docker config: docker-compose.yml
- Dependencies file: requireme.text
