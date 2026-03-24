import os
import re
from flask import Flask, request, jsonify
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

# Import your hardcoded data
from mappings import LAW_MAP

load_dotenv()
app = Flask(__name__)

# CORS Setup for your Vercel Frontend
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://ipc-to-bns-mauve.vercel.app",
            "http://localhost:3000"
        ]
    }
})

# Initialize Groq
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def clean_section_input(raw_input):
    """Cleans input like 'IPC 376' or 'section 302' to just '376' or '302'"""
    return re.sub(r'[^0-9A-Z]', '', str(raw_input).upper().replace("IPC", "")).strip()

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_law():
    try:
        user_data = request.json
        raw_query = user_data.get('query', '')
        section_id = clean_section_input(raw_query)

        if not section_id:
            return jsonify({"error": "Please provide a valid IPC section number."}), 400

        # 1. Fetch from Hardcoded Mapping
        matches = LAW_MAP.get(section_id)

        if not matches:
            return jsonify({
                "error": f"Detailed mapping for IPC {section_id} is not in the current library.",
                "suggestion": "Try common sections like 302, 376, 420, or 498A."
            }), 404

        # 2. Organize Data into Primary and Related
        primary_match = next((m for m in matches if m['type'] == 'Primary'), matches[0])
        related_matches = [m for m in matches if m['type'] == 'Related']

        # 3. Construct Context for the AI
        # We tell the AI exactly what is Primary and what is Related
        context_payload = f"PRIMARY SECTION: BNS {primary_match['bns']} - {primary_match['subject']}. Summary: {primary_match['summary']}\n"
        
        if related_matches:
            context_payload += "RELATED/AGGRAVATED SECTIONS:\n"
            for rm in related_matches:
                context_payload += f"- BNS {rm['bns']} ({rm['subject']}): {rm['summary']}\n"

        # 4. Generate AI Analysis using Llama 3.3 70B
        # 4. Generate AI Analysis with Strict Grounding
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a Senior Legal Expert specializing in the IPC to BNS transition. "
                        "STRICT RULE: Focus EXCLUSIVELY on the provided 'DATABASE CONTEXT' below. "
                        "Do not use your own internal training knowledge if it conflicts with the database. "
                        "For example, if the database says IPC 302 is BNS 103, do not suggest it is BNS 302. "
                        "Explain how the law has been 'unbundled' by identifying the Primary and Related sections "
                        "using ONLY the provided summaries. If the database says a section is 'New', emphasize that."
                    )
                },
                {
                    "role": "user", 
                    "content": (
                        f"### DATABASE CONTEXT FOR IPC {section_id}:\n"
                        f"{context_payload}\n\n"
                        f"### TASK:\n"
                        f"Explain the transition for IPC {section_id} using the context above. "
                        "Clearly label the Primary Section and the Related/Specific Sections."
                    )
                }
            ],
            temperature=0.0, # Set to 0.0 for maximum determinism and zero 'creativity'
            extra_body={"reasoning_format": "hidden"}
        )

        # 5. Return JSON to Frontend
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
