import os
import re
from flask import Flask, request, jsonify, make_response
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

# Import your hardcoded data
from mappings import LAW_MAP

load_dotenv()
app = Flask(__name__)

# 1. Robust CORS Setup
# We allow the specific Vercel origin and the necessary headers/methods
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://ipc-to-bns-mauve.vercel.app",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize Groq
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def clean_section_input(raw_input):
    """Cleans input like 'IPC 376' or 'section 302' to just '376' or '302'"""
    if not raw_input:
        return ""
    return re.sub(r'[^0-9A-Z]', '', str(raw_input).upper().replace("IPC", "")).strip()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint for Cron-job.org to keep the server awake."""
    return jsonify({
        "status": "online",
        "engine": "GPT-OSS-20B",
        "uptime": "active"
    }), 200

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_law():
    # 2. Handle Preflight OPTIONS request explicitly
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "https://ipc-to-bns-mauve.vercel.app")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        return response, 200

    try:
        user_data = request.json
        if not user_data:
            return jsonify({"error": "No data provided"}), 400
            
        raw_query = user_data.get('query', '')
        section_id = clean_section_input(raw_query)

        if not section_id:
            return jsonify({"error": "Please provide a valid IPC section number."}), 400

        matches = LAW_MAP.get(section_id)

        if not matches:
            return jsonify({
                "error": f"Detailed mapping for IPC {section_id} is not in the current library.",
                "suggestion": "Try common sections like 302, 376, 420, or 498A."
            }), 404

        # Logic to fetch Primary and Related/Mirror notes
        primary_match = next((m for m in matches if m.get('type') == 'Primary'), matches[0])
        related_matches = [m for m in matches if m.get('type') in ['Related', 'Mirror']]
        
        special_context = primary_match.get('special_note', None)

        # 3. Construct Context for the AI
        context_payload = f"PRIMARY SECTION: BNS {primary_match['bns']} - {primary_match['subject']}. Summary: {primary_match['summary']}\n"
        
        if special_context:
            context_payload += f"SPECIAL CONTEXT/FACT: {special_context}\n"
        
        if related_matches:
            context_payload += "RELATED/AGGRAVATED SECTIONS:\n"
            for rm in related_matches:
                context_payload += f"- BNS {rm['bns']} ({rm['subject']}): {rm['summary']}\n"

        # 4. Generate AI Analysis
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a Senior Legal Expert specializing in the IPC to BNS transition. "
                        "STRICT RULE: Focus EXCLUSIVELY on the provided 'DATABASE CONTEXT'. "
                        "Explain the 'unbundling' of the law. "
                        "IMPORTANT: If a 'SPECIAL CONTEXT/FACT' is provided, incorporate it into your "
                        "explanation as a 'Special Legal Note' to provide context."
                    )
                },
                {
                    "role": "user", 
                    "content": (
                        f"### DATABASE CONTEXT FOR IPC {section_id}:\n"
                        f"{context_payload}\n\n"
                        f"### TASK:\n"
                        f"Explain the transition for IPC {section_id}. "
                        "Use Markdown formatting. Include a table for sections if applicable. "
                        "Ensure the 'Special Legal Note' is highlighted if it was provided."
                    )
                }
            ],
            temperature=0.0,
            extra_body={"reasoning_format": "hidden"}
        )

        return jsonify({
            "ipc_section": section_id,
            "primary_bns": primary_match['bns'],
            "related_bns": [rm['bns'] for rm in related_matches],
            "analysis": completion.choices[0].message.content
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
