from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    question = data.get("question")
    inventory = data.get("inventory", "")

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{
                "parts": [{
                    "text": f"You are a supply chain analyst assistant. Here is the current inventory data:\n{inventory}\n\nAnswer this question: {question}\n\nBe specific, use the data, and give actionable recommendations. Keep it concise."
                }]
            }]
        }
    )

    result = response.json()

    if "candidates" in result:
        answer = result["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"answer": answer})
    else:
        error_msg = str(result)
        return jsonify({"answer": f"Error: {error_msg}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
