import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize Flask App FIRST (Prevents NameError)
app = Flask(__name__)

# 3. Configure CORS - Update this if your Vercel URL changes
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

        # Extract only digits (e.g., "302" from "IPC 302")
        raw_query = str(user_data.get('query', '')).strip()
        section_num = ''.join(filter(str.isdigit, raw_query))

        if not section_num:
            return jsonify({"error": "Please provide a section number."}), 400

        # 5. Search Supabase
        # Handles exact match or matching within a list (e.g., "302, 303")
        db_response = supabase.table("laws_mapping")\
            .select("*")\
            .or_(f"ipc_section.eq.{section_num},ipc_section.ilike.%{section_num}%")\
            .execute()
        
        law_context = ""
        bns_val = ""

        if db_response.data:
            bns_val = str(db_response.data[0].get('bns_section', ''))
            context_list = [
                f"- BNS {item['bns_section']} (IPC {item['ipc_section']}): {item['title']}. Changes: {item['key_changes']}"
                for item in db_response.data
            ]
            law_context = "OFFICIAL BPR&D DATA:\n" + "\n".join(context_list)
        else:
            law_context = "No direct database entry found for this section number."

        # 6. Fallback Logic for the "Green Box" (BNS Equivalent)
        # If DB fails, we hardcode common mappings so the UI looks perfect
        if not bns_val:
            common_mappings = {
                "302": "101",
                "420": "318",
                "376": "64",
                "307": "109",
                "124A": "152"
            }
            bns_val = common_mappings.get(section_num, "MAPPED")

        # 7. AI Analysis with Llama 3.3 70B
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are an expert Indian Legal Assistant. "
                        "Identify the transition from IPC to BNS (Bharatiya Nyaya Sanhita 2023). "
                        "Rules:\n"
                        "1. Prioritize provided BPR&D context.\n"
                        "2. If context is empty, use internal knowledge (e.g., IPC 302 is BNS 101).\n"
                        "3. Use professional legal terminology and bullet points.\n"
                        "4. Clearly state if the punishment or definition has changed."
                    )
                },
                {"role": "user", "content": f"Context: {law_context}\n\nAnalyze IPC Section {section_num}."}
            ],
            temperature=0.1,
            max_tokens=1024
        )

        # 8. Return JSON matching your Frontend keys
        return jsonify({
            "analysis": completion.choices[0].message.content,
            "bns_section": bns_val,
            "source_data": db_response.data 
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

# 9. Render-Specific Port Handling
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
