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

LAW_META = {
    "IPC": "Indian Penal Code",
    "BNS": "Bharatiya Nyaya Sanhita"
}

# 1. Robust CORS Setup
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
    """Cleans input to keep numbers, letters, and brackets for sub-sections."""
    if not raw_input:
        return ""
    # We allow numbers, letters, and parentheses to catch 376(1)
    cleaned = str(raw_input).upper().replace("IPC", "").strip()
    return re.sub(r'[^0-9A-Z()]', '', cleaned)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "uptime": "active"
    }), 200

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_law():
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

        # --- LOGIC: AGGREGATE PRIMARY AND RELATED SUB-SECTIONS ---
        all_matches = []
        
        # Look for the exact section AND any sub-sections (e.g., 376, 376(1), 376A)
        # This ensures searching '376' pulls in '376(1)' and '376(2)'
        for key in LAW_MAP.keys():
            # Match if it's exact OR starts with the number followed by a bracket or letter
            if key == section_id or key.startswith(f"{section_id}(") or key.startswith(f"{section_id}A"):
                all_matches.extend(LAW_MAP[key])

        if not all_matches:
            return jsonify({
                "error": f"Detailed mapping for IPC {section_id} is not in the current library.",
                "suggestion": "Try common sections like 302, 376, 420, or 498A."
            }), 404

        # Identify the main result and the sub-sections
        primary_match = next((m for m in all_matches if m.get('type') == 'Primary'), all_matches[0])
        related_matches = [m for m in all_matches if m != primary_match]
        
        special_context = primary_match.get('special_note', None)

        # 3. Construct Context for the AI
        context_payload = f"PRIMARY SECTION: BNS {primary_match['bns']} - {primary_match['subject']}.\nSUMMARY: {primary_match['summary']}\n"
        
        if special_context:
            context_payload += f"SPECIAL CONTEXT/FACT: {special_context}\n"
        
        if related_matches:
            context_payload += "\nRELATED SUB-SECTIONS OR AGGRAVATED OFFENCES FOUND:\n"
            for rm in related_matches:
                context_payload += f"- BNS {rm['bns']} ({rm['subject']}): {rm['summary']}\n"

        # 4. Generate AI Analysis
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b", # Ensure your Groq provider supports this specific model string
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a Senior Legal Expert specializing in the IPC to BNS transition. "
                        "STRICT RULE: Focus EXCLUSIVELY on the provided 'DATABASE CONTEXT'. "
                        "Explain how the law has been 'unbundled' or reorganized. "
                        "If multiple BNS sub-sections are provided, explain how they relate to the original IPC section."
                    )
                },
                {
                    "role": "user", 
                    "content": (
                        f"### DATABASE CONTEXT FOR IPC {section_id}:\n"
                        f"{context_payload}\n\n"
                        f"### TASK:\n"
                        f"Explain the transition for IPC {section_id} into the BNS. "
                        "Use Markdown formatting with tables for clarity. "
                        "Highlight any changes in terminology or fine amounts if mentioned in the summary."
                    )
                }
            ],
            temperature=0.0
        )

        return jsonify({
            "ipc_section": section_id,
            "primary_bns": primary_match['bns'],
            "related_bns": list(set([rm['bns'] for rm in related_matches])),
            "analysis": completion.choices[0].message.content
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == '__main__':
    # Use PORT from environment for deployment (Render/Railway/Vercel)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
