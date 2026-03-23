import os
import re
from flask import Flask, request, jsonify
from supabase import create_client, Client
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

# 1. Setup & Configuration
load_dotenv()
app = Flask(__name__)

# IMPORTANT: This handles the connection between your Vercel URL and Render Backend
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://ipc-to-bns-mauve.vercel.app", 
            "http://localhost:3000",
            "http://127.0.0.1:5000"
        ]
    }
})

# Initialize Clients
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"), 
    os.environ.get("SUPABASE_ANON_KEY")
)
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/api/analyze', methods=['POST'])
def analyze_law():
    try:
        # Get data from Frontend
        user_data = request.json
        if not user_data:
            return jsonify({"error": "No data provided"}), 400
            
        raw_input = str(user_data.get('query', '')).strip()
        
        # Clean Input: "IPC 302" -> "302"
        section_clean = re.sub(r'[^a-zA-Z0-9]', '', raw_input).upper().replace("IPC", "")

        if not section_clean:
            return jsonify({"error": "Please enter a valid section number"}), 400

        # 2. Database Search (Supabase) - Keep 1:Many Logic
        # This fetches all rows where the IPC section matches.
        db_res = supabase.table("laws_mapping").select("*").ilike("ipc_section", f"%{section_clean}%").execute()
        
        # Filtering for exact matches to ensure '30' doesn't match '302'
        all_matches = [
            i for i in db_res.data 
            if i['ipc_section'].replace(" ", "").upper() == section_clean
        ]

        # 3. Logic: Identify Primary vs Related (1:Several Mapping)
        # Fallbacks for high-priority sections if Supabase is down or empty
        fallbacks = {
            "376": ["64", "66", "70", "71", "72"],
            "300": ["101"], "302": ["101"], "124A": ["152"],
            "498A": ["85", "86"], "188": ["223"], "420": ["318"]
        }

        # Create a unique list of BNS sections found in the DB
        bns_list = list(dict.fromkeys([str(i['bns_section']) for i in all_matches]))
        
        # Use fallback if DB returned nothing but the code is in our list
        if not bns_list and section_clean in fallbacks:
            bns_list = fallbacks[section_clean]

        if not bns_list:
            return jsonify({"error": "Section mapping not found in our 2024 database."}), 404

        # Separation logic: The first BNS is "Primary", the rest are "Related/Parallel"
        primary = bns_list[0]
        related = bns_list[1:]
        
        # Context string for the AI to understand the 'Unbundling'
        law_context = (
            f"IPC {section_clean} has been unbundled into multiple BNS sections. "
            f"Primary Section: {primary}. Parallel/Specific Sections: {', '.join(related) if related else 'None'}."
        )
        
        # 4. AI Explanation Generation (GPT-OSS 20B)
        # extra_body ensures the 'internal monologue' doesn't crash the API
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a Senior Legal Expert. Your task is to explain the 2024 BNS transition. "
                        "Focus on 'Unbundling': explaining how one IPC section might now be split into several "
                        "specific BNS sections. Use the provided mapping as your source of truth. "
                        "Respond in clean Markdown with bullet points."
                    )
                },
                {
                    "role": "user", 
                    "content": f"Explain the transition for IPC {section_clean}. Data: {law_context}"
                }
            ],
            temperature=0.2,
            max_tokens=600,
            extra_body={"reasoning_format": "hidden"} 
        )

        # 5. Return JSON to Frontend
        return jsonify({
            "analysis": completion.choices[0].message.content,
            "primary_bns": primary,
            "related_bns": related,
            "is_unbundled": len(related) > 0
        })

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": "Internal server error. Check Render logs."}), 500

# 6. Deployment Entry Point
if __name__ == '__main__':
    # PORT is automatically assigned by Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
