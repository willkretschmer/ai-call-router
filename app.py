from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

def classify_intent(caller_text):
    if not caller_text:
        return None, "No speech text provided"
    prompt = (
        "You're an AI receptionist for a company. Based on this caller message, "
        "identify the most likely department they should speak to: Sales, Engineering, "
        "Lab, or Customer Service.\n\n"
        f"Caller message: '{caller_text}'\n\nReturn just the department name."
    )
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        department = response.choices[0].message.content.strip()
        return department, None
    except Exception as e:
        return None, str(e)

@app.route("/nlp", methods=["POST"])
def nlp_route():
    # Try to get JSON, if not present, fall back to form
    data = request.get_json(silent=True) or request.form
    text = data.get("SpeechResult", "")
    intent, error = classify_intent(text)
    if error:
        return jsonify({'error': error}), 400
    return jsonify({"intent": intent})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
