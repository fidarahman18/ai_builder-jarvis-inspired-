import os
import json
from flask import Flask, request, jsonify, render_template, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from orchestrator import generate_app, ask_clarifying_questions
from github_handler import create_repo, push_files
from vercel_handler import deploy

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/clarify", methods=["POST"])
def clarify():
    idea = request.json.get("idea", "")
    questions = ask_clarifying_questions(idea)
    return jsonify({"questions": questions})

@app.route("/build", methods=["POST"])
def build():
    data = request.json
    idea = data.get("idea", "")
    answers = data.get("answers", "")

    def generate():
        try:
            yield f"data: {json.dumps({'step': 1, 'msg': '🤖 GPT-4o is generating your app...'})}\n\n"
            app_data = generate_app(idea, answers)
            project_name = app_data["project_name"]
            files = app_data["files"]

            yield f"data: {json.dumps({'step': 2, 'msg': '📁 Creating GitHub repository...'})}\n\n"
            repo_url = create_repo(project_name)

            yield f"data: {json.dumps({'step': 3, 'msg': '⬆️ Pushing code to GitHub...'})}\n\n"
            push_files(project_name, files)

            yield f"data: {json.dumps({'step': 4, 'msg': '🚀 Deploying to Vercel...'})}\n\n"
            live_url = deploy(project_name)

            yield f"data: {json.dumps({'step': 5, 'msg': '✅ Done!', 'github': repo_url, 'live': live_url, 'description': app_data['description']})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True, port=5000)