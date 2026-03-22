import os
import re
from flask import Flask, request, jsonify
from supabase import create_client, Client
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["https://ipc-to-bns-mauve.vercel.app", "http://localhost:3000", "https://ipc-to-bns.onrender.com"]}})

supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_ANON_KEY"))
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/api/analyze', methods=['POST'])
def analyze_law():
    try:
        user_data = request.json
        raw_input = str(user_data.get('query', '')).strip()
        
        # ✅ Standardize Input (Handles 124A, 498A etc)
        section_clean = re.sub(r'[^a-zA-Z0-9]', '', raw_input).upper().replace("IPC", "")

        if not section_clean:
            return jsonify({"error": "Invalid Section"}), 400

        # ✅ Change 1: Fetch ALL mappings from Supabase
        db_res = supabase.table("laws_mapping").select("*").ilike("ipc_section", f"%{section_clean}%").execute()
        
        # Filter for exact matches to avoid "30" matching "300"
        all_matches = [
            i for i in db_res.data 
            if i['ipc_section'].replace(" ", "").upper() == section_clean
        ]

        # ✅ Change 2: Separate Primary + Related
        # We use a set to avoid duplicates, then list
        bns_list = list(dict.fromkeys([str(i['bns_section']) for i in all_matches]))
        
        # Hardcoded Safety Net (If DB is missing a link)
        fallbacks = {
            "300": ["101"], "302": ["101"], "124A": ["152"], 
            "188": ["223"], "498A": ["85", "86"], "420": ["318"]
        }
        
        final_list = bns_list if bns_list else fallbacks.get(section_clean, [])
        primary = final_list[0] if final_list else "MAPPED"
        related = final_list[1:] if len(final_list) > 1 else []

        # ✅ Change 3 & 6: Fix AI Context & Prompt
        law_context = f"IPC {section_clean} maps to BNS sections: {', '.join(final_list)}."
        
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a BNS Legal Expert. IPC sections often map to MULTIPLE BNS sections. "
                        "Always identify the Primary section and mention Related sections if applicable. "
                        "Explain if a section was split, combined, or redefined. Use bullet points."
                    )
                },
                {"role": "user", "content": f"Analyze IPC {section_clean}. {law_context}"}
            ],
            temperature=0.2
        )

        # ✅ Change 4: Structured JSON Response
        return jsonify({
            "analysis": completion.choices[0].message.content,
            "bns_section": primary,  # For the main green box
            "related_bns": related,   # For the 'Related' UI section
            "all_mappings": final_list
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
