from flask import Flask, request, Response, jsonify
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)

# --- Your AI Intent Classifier ---
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
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        department = response.choices[0].message.content.strip()
        return department, None
    except Exception as e:
        return None, str(e)

# --- Step 1: Answer the Call and Prompt ---
@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/gather",
        method="POST",
        language="en-US",
        timeout=5,
        speechTimeout="auto"
    )
    gather.say("Thank you for calling. Please briefly tell me the reason for your call.")
    resp.append(gather)
    resp.say("Sorry, I didn't catch that. Goodbye.")
    return Response(str(resp), mimetype="text/xml")

# --- Step 2: Handle Gathered Speech, AI Routing, and Connect ---
@app.route("/gather", methods=["POST"])
def gather():
    speech_result = request.values.get("SpeechResult", "")
    department, error = classify_intent(speech_result)
    resp = VoiceResponse()

    if error or not department:
        resp.say("Sorry, there was a problem understanding your request. Goodbye.")
        return Response(str(resp), mimetype="text/xml")

    # Routing logic: set these numbers appropriately!
    department_numbers = {
        "Sales": "+19369004675",
        "Engineering": "+19369004675",
        "Lab": "+19369004675",
        "Customer Service": "+19369004675",
    }

    number = department_numbers.get(department)
    if number:
        resp.say(f"Connecting you to {department}.")
        resp.dial(number)
    else:
        resp.say("Sorry, I couldn't determine the correct department. Goodbye.")
    return Response(str(resp), mimetype="text/xml")

# --- (Optional) Step 3: Your NLP endpoint for internal testing ---
@app.route("/nlp", methods=["POST"])
def nlp_route():
    data = request.get_json(silent=True) or request.form
    text = data.get("SpeechResult", "")
    intent, error = classify_intent(text)
    if error:
        return jsonify({'error': error}), 400
    return jsonify({"intent": intent})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
