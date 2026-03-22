import os
import re
from flask import Flask, request, jsonify
from supabase import create_client, Client
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize Flask App
app = Flask(__name__)

# 3. Configure CORS (Update with your specific Vercel URL)
CORS(app, resources={r"/api/*": {"origins": ["https://ipc-to-bns-mauve.vercel.app", "http://localhost:3000"]}})

# 4. Initialize Clients
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

@app.route('/api/analyze', methods=['POST'])
def analyze_law():
    try:
        user_data = request.json
        if not user_data:
            return jsonify({"error": "No data received"}), 400

        # FIX: Regex to keep numbers AND letters (124A, 120B, etc.)
        # This removes spaces and punctuation but keeps alphanumerics
        raw_query = str(user_data.get('query', '')).strip()
        section_num = re.sub(r'[^a-zA-Z0-9]', '', raw_query).upper()

        if not section_num:
            return jsonify({"error": "Please provide a valid section number."}), 400

        # 5. Search Supabase (Broadened to find partial/exact matches with letters)
        db_response = supabase.table("laws_mapping")\
            .select("*")\
            .or_(f"ipc_section.eq.{section_num},ipc_section.ilike.%{section_num}%")\
            .execute()
        
        law_context = ""
        bns_val = ""

        if db_response.data:
            # Try to find an exact match first for the big green box
            exact_match = next((item for item in db_response.data if item['ipc_section'].upper() == section_num), db_response.data[0])
            bns_val = str(exact_match.get('bns_section', ''))
            
            context_list = [
                f"- BNS {item['bns_section']} (IPC {item['ipc_section']}): {item['title']}. Changes: {item['key_changes']}"
                for item in db_response.data
            ]
            law_context = "OFFICIAL BPR&D DATA:\n" + "\n".join(context_list)
        else:
            law_context = "No direct database entry found for this alphanumeric section."

        # 6. Alphanumeric Fallbacks for UI Consistency
        if not bns_val:
            fallbacks = {
                "124A": "152",
                "120B": "61",
                "120A": "61",
                "376D": "70",
                "302": "101",
                "420": "318"
            }
            bns_val = fallbacks.get(section_num, "MAPPED")

        # 7. AI Analysis
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a Senior Indian Legal Expert. Analyze the transition from IPC to BNS (2023). "
                        "Note: IPC 124A (Sedition) is now BNS 152 (Acts endangering sovereignty). "
                        "Identify the correct BNS mapping and explain changes in definition or punishment using bullet points."
                    )
                },
                {"role": "user", "content": f"Context: {law_context}\n\nMapping Request: IPC Section {section_num}"}
            ],
            temperature=0.1
        )

        return jsonify({
            "analysis": completion.choices[0].message.content,
            "bns_section": bns_val,
            "source_data": db_response.data 
        })

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
