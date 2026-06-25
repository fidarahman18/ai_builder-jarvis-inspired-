import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a senior full-stack developer. 
When given an app idea, you generate a complete, working Next.js application.
You ALWAYS respond with a valid JSON object in this exact format:
{
  "project_name": "expense-tracker",
  "description": "A real-time expense tracker with charts",
  "files": {
    "package.json": "...full content...",
    "pages/index.js": "...full content...",
    "pages/api/transactions.js": "...full content...",
    "styles/globals.css": "...full content..."
  },
  "setup_commands": ["npm install", "npm run build"]
}
Only return JSON. No explanation. No markdown fences.
"""

def ask_clarifying_questions(idea: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a product manager. Ask 2-3 smart clarifying questions about this app idea to make it better. Be brief and direct."},
            {"role": "user", "content": f"App idea: {idea}"}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content

def generate_app(idea: str, answers: str = "") -> dict:
    prompt = f"""
Build a complete Next.js expense tracker app.

User idea: {idea}
Additional context: {answers}

Requirements:
- Single page app with a clean dark UI
- Add transactions (amount, category, description)
- Show a summary: total income, total expenses, balance
- List all transactions with delete button
- Use localStorage for data persistence
- Use inline styles (no external CSS libraries)
- Make it look professional and impressive
- Must work without a backend (pure frontend)
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000
    )
    import json
    raw = response.choices[0].message.content.strip()
    # Strip markdown fences if model adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())