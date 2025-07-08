from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route('/nlp', methods=['POST'])
def nlp():
    data = request.get_json()
    caller_text = data.get('SpeechResult', '')

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

