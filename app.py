from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("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")

app = Flask(__name__)

@app.route("/nlp", methods=["POST"])
def nlp_route():
    data = request.get_json()
    text = data.get("SpeechResult", "")
    intent = classify_intent(text)  # Your NLP logic
    return jsonify({"intent": intent})

    if not caller_text:
        return jsonify({'error': 'No speech text provided'}), 400

    prompt = (
        "You're an AI receptionist for a company. Based on this caller message, "
        "identify the most likely department they should speak to: Sales, Engineering, "
        "Lab, or Customer Service.\n\n"
        f"Caller message: '{caller_text}'\n\nReturn just the department name."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        department = response['choices'][0]['message']['content'].strip()
        return jsonify({"intent": department})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

