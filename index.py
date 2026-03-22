import os
import re
from flask import Flask, request, jsonify
from supabase import create_client, Client
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

# 1. Setup
load_dotenv()
app = Flask(__name__)

# 2. CORS Configuration
CORS(app, resources={r"/api/*": {"origins": ["https://ipc-to-bns-mauve.vercel.app", "http://localhost:3000"]}})

# 3. Clients
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_ANON_KEY"))
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/api/analyze', methods=['POST'])
def analyze_law():
    try:
        user_data = request.json
        if not user_data:
            return jsonify({"error": "No data received"}), 400

        # --- THE FIX FOR 124A, 120B, etc. ---
        # 1. Get raw input
        raw_input = str(user_data.get('query', '')).strip()
        # 2. Remove "IPC" if typed, remove spaces/symbols, keep numbers and letters
        section_clean = re.sub(r'[^a-zA-Z0-9]', '', raw_input).upper().replace("IPC", "")

        if not section_clean:
            return jsonify({"error": "Please enter a valid section (e.g., 302 or 124A)"}), 400

        # 4. Database Search (Searching as Text)
        db_res = supabase.table("laws_mapping")\
            .select("*")\
            .ilike("ipc_section", f"%{section_clean}%")\
            .execute()
        
        law_context = ""
        bns_num = ""

        if db_res.data:
            # Match the closest alphanumeric string (e.g., "124A" instead of just "124")
            match = next((i for i in db_res.data if i['ipc_section'].replace(" ", "").upper() == section_clean), db_res.data[0])
            bns_num = str(match.get('bns_section', ''))
            law_context = f"OFFICIAL MAPPING: IPC {match['ipc_section']} is BNS {match['bns_section']}. Title: {match['title']}. Changes: {match['key_changes']}"

        # 5. Safety Net Mapping (Hardcoded for 100% UI accuracy)
        fallbacks = {
            "124A": "152", "120B": "61", "302": "101", 
            "307": "109", "376": "64", "420": "318"
        }
        final_bns = bns_num if bns_num else fallbacks.get(section_clean, "MAPPED")

        # 6. REFINED AI PROMPT (Forcing Accuracy)
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a Senior Legal Expert on the Bharatiya Nyaya Sanhita (BNS) 2023. "
                        "Your goal is to explain the transition from the old IPC to the new BNS. "
                        "\nSPECIFIC RULES:"
                        "\n- IPC 124A (Sedition) is now BNS Section 152 (Acts endangering sovereignty)."
                        "\n- IPC 302 (Murder) is now BNS Section 101."
                        "\n- IPC 420 (Cheating) is now BNS Section 318."
                        "\n- If the database context is provided, use it. If not, use your internal knowledge."
                        "\n- Provide a professional summary with bullet points."
                    )
                },
                {"role": "user", "content": f"Analyze IPC Section {section_clean}. (Context: {law_context})"}
            ],
            temperature=0.1 # Keep it strict and factual
        )

        return jsonify({
            "analysis": completion.choices[0].message.content,
            "bns_section": final_bns,
            "source_data": db_res.data 
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
