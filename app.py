from flask import Flask, request, render_template, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
EMBEDDING_MODEL_DEPLOYMENT = os.getenv("EMBEDDING_MODEL_DEPLOYMENT")
CHAT_MODEL_DEPLOYMENT = os.getenv("CHAT_MODEL_DEPLOYMENT")
AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
AZURE_AI_SEARCH_KEY = os.getenv("AZURE_AI_SEARCH_KEY")
AZURE_AI_SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    headers = {
        "api-key": AZURE_OPENAI_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "dataSources": [
            {
                "type": "AzureCognitiveSearch",
                "parameters": {
                    "endpoint": AZURE_AI_SEARCH_ENDPOINT,
                    "key": AZURE_AI_SEARCH_KEY,
                    "indexName": AZURE_AI_SEARCH_INDEX_NAME,
                    "fieldsMapping": {},
                    "inScope": True
                }
            }
        ],
        "messages": [
            {"role": "system", "content": "You are an assistant answering based on company documents."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.2,
        "top_p": 1
    }
    endpoint = AZURE_OPENAI_ENDPOINT.rstrip("/")
    url = f"{endpoint}/openai/deployments/{CHAT_MODEL_DEPLOYMENT}/extensions/chat/completions?api-version=2023-08-01-preview"

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )
    try:
        response.raise_for_status()
        print(response.json())  # Debug output
        answer = response.json()["choices"][0]["message"]["content"]
        return jsonify({"answer": answer})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)