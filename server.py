from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_sheet(sheet_name="Sheet1"):
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)
    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    spreadsheet = client.open("Sumiyo Analysis Data")
    return spreadsheet.worksheet(sheet_name)

@app.route("/sheets/read", methods=["GET"])
def read_sheet():
    try:
        sheet_name = request.args.get("sheet", "Sheet1")
        sheet = get_sheet(sheet_name)
        data = sheet.get_all_records()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    question = data.get("question")
    inventory = data.get("inventory", "")

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
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
        return jsonify({"answer": f"Error: {str(result)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
