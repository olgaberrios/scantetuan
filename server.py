import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "olgaberrios/scantetuan")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")

def upload_to_github(filename, content_base64):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/fotos/{filename}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    # Check if file already exists (to get sha for update)
    sha = None
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        sha = r.json().get("sha")

    payload = {
        "message": f"Foto: {filename}",
        "content": content_base64,
        "branch": GITHUB_BRANCH
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(url, json=payload, headers=headers)
    if r.status_code in (200, 201):
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/fotos/{filename}"
        return {"ok": True, "url": raw_url}
    else:
        return {"ok": False, "error": r.text}


@app.route("/upload-foto", methods=["POST"])
def upload_foto():
    data = request.get_json()
    if not data or "filename" not in data or "content" not in data:
        return jsonify({"ok": False, "error": "Faltan campos"}), 400

    filename = data["filename"]
    content_b64 = data["content"]

    # Strip data URL prefix if present (data:image/jpeg;base64,...)
    if "," in content_b64:
        content_b64 = content_b64.split(",", 1)[1]

    result = upload_to_github(filename, content_b64)
    if result["ok"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
