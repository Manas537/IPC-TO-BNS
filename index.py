import os
import re
from flask import Flask, request, jsonify
from supabase import create_client, Client
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app)

supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_ANON_KEY"))
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/api/analyze', methods=['POST'])
def analyze_law():
    try:
        user_data = request.json
        raw_input = str(user_data.get('query', '')).strip()
        
        # Clean: "IPC 124A" -> "124A"
        section_clean = re.sub(r'[^a-zA-Z0-9]', '', raw_input).upper().replace("IPC", "")

        if not section_clean:
            return jsonify({"error": "Please enter a valid section number"}), 400

        # 1. Database Search
        db_res = supabase.table("laws_mapping").select("*").ilike("ipc_section", f"%{section_clean}%").execute()
        
        # Filter for exact matches only (to avoid '30' matching '302')
        all_matches = [
            i for i in db_res.data 
            if i['ipc_section'].replace(" ", "").upper() == section_clean
        ]

        # 2. Logic: Identify Primary vs Related
        # If no DB results, check this Safety Fallback
        fallbacks = {
            "376": ["64", "66", "70", "71", "72"],
            "300": ["101"], "302": ["101"], "124A": ["152"],
            "498A": ["85", "86"], "188": ["223"], "420": ["318"]
        }

        bns_list = list(dict.fromkeys([str(i['bns_section']) for i in all_matches]))
        if not bns_list and section_clean in fallbacks:
            bns_list = fallbacks[section_clean]

        if not bns_list:
            return jsonify({"error": "Section mapping not found in database."}), 404

        # Define Primary (General Punishment) and Related (Specific Cases)
        primary = bns_list[0]
        related = bns_list[1:]
# 3. AI Context: Updated for the 120B Model with Surfing
        law_context = f"IPC {section_clean} maps to Primary BNS {primary}. Related/Specific BNS sections: {', '.join(related) if related else 'None'}."
        
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a Senior Legal Expert specializing in the 2024 BNS transition. "
                        "Your goal is to explain how the law has been 'unbundled'. "
                        "1. Use the provided mapping as your primary guide. "
                        "2. Use your 'browser_search' tool to verify these section numbers against the FINAL Act No. 45 of 2023. "
                        "3. If the provided mapping contradicts the final law (e.g., Section 72 being Privacy vs Maiming), "
                        "politely correct it and provide the official 2024 definition."
                    )
                },
                {"role": "user", "content": f"Explain the transition for IPC {section_clean}. {law_context}"}
            ],
            # This is the "Surfing" switch you wanted
            tools=[{"type": "browser_search"}], 
            temperature=0.2
        )
        return jsonify({
            "analysis": completion.choices[0].message.content,
            "primary_bns": primary,
            "related_bns": related
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
