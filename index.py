import os
import re
from flask import Flask, request, jsonify
from supabase import create_client, Client
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)

# Updated CORS to specifically allow your Vercel frontend
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://ipc-to-bns-mauve.vercel.app",
            "http://localhost:3000"
        ]
    }
})

# Initialize your exact clients
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_ANON_KEY"))
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/api/analyze', methods=['POST'])
def analyze_law():
    try:
        user_data = request.json
        raw_input = str(user_data.get('query', '')).strip()
        
        # Your Cleaning Logic: "IPC 124A" -> "124A"
        section_clean = re.sub(r'[^a-zA-Z0-9]', '', raw_input).upper().replace("IPC", "")

        if not section_clean:
            return jsonify({"error": "Please enter a valid section number"}), 400

        # 1. Your Database Search Logic
        db_res = supabase.table("laws_mapping").select("*").ilike("ipc_section", f"%{section_clean}%").execute()
        
        # Your Filter for exact matches
        all_matches = [
            i for i in db_res.data 
            if i['ipc_section'].replace(" ", "").upper() == section_clean
        ]

        # 2. Your Logic: Identify Primary vs Related
        # Your exact fallbacks
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

        # 3. AI Context (No Browser Search)
        law_context = f"IPC {section_clean} maps to Primary BNS {primary}. Related/Specific BNS sections: {', '.join(related) if related else 'None'}."
        
        # Using the requested model: llama-3.3-70b-versatile
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a Senior Legal Expert on the Indian Penal Code (IPC) and Bharatiya Nyaya Sanhita (BNS). "
                        "IMPORTANT: IPC 302 is Punishment for Murder. IPC 376 is Punishment for Rape. "
                        "Explain how the law has been 'unbundled'. Define the Primary section as the General Punishment "
                        "and explain Related sections as specific aggravations or definitions. Use clear bullet points."
                    )
                },
                {"role": "user", "content": f"Explain the transition for IPC {section_clean}. {law_context}"}
            ],
            temperature=0.2,
            # This ensures 'thinking' text doesn't break the JSON output
            extra_body={"reasoning_format": "hidden"} 
        )

        return jsonify({
            "analysis": completion.choices[0].message.content,
            "primary_bns": primary,
            "related_bns": related
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use environment port for deployment (Render/Vercel)
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
