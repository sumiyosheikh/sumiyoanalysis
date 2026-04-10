from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    question = data.get("question")
    inventory = data.get("inventory", "")

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-70b-8192",
            "messages": [
                {
                    "role": "user",
                    "content": f"You are a supply chain analyst assistant. Here is the current inventory data:\n{inventory}\n\nAnswer this question: {question}\n\nBe specific, use the data, and give actionable recommendations. Keep it concise."
                }
            ]
        }
    )

    result = response.json()
    answer = result["choices"][0]["message"]["content"]
    return jsonify({"answer": answer})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
