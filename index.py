import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize Flask App & CORS first to avoid NameErrors
app = Flask(__name__)
# Replace the URL below with your actual Vercel URL for better security
CORS(app, resources={r"/api/*": {"origins": "https://ipc-to-bns-mauve.vercel.app"}})

# 3. Initialize Clients
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
            return jsonify({"error": "No data provided"}), 400

        # Extract only digits from the query (e.g., "302" from "IPC 302")
        raw_query = str(user_data.get('query', '')).strip()
        section_num = ''.join(filter(str.isdigit, raw_query))

        if not section_num:
            return jsonify({"error": "Please provide a valid section number."}), 400

        # 4. Search Supabase (Handles exact match and variations)
        db_response = supabase.table("laws_mapping")\
            .select("*")\
            .or_(f"ipc_section.eq.{section_num},ipc_section.ilike.% {section_num} %")\
            .execute()
        
        law_context = ""
        bns_val = ""

        if db_response.data:
            # Grab the first match for the header
            bns_val = db_response.data[0].get('bns_section', '')
            context_list = []
            for item in db_response.data:
                context_list.append(
                    f"- BNS {item['bns_section']} (IPC {item['ipc_section']}): {item['title']}. "
                    f"Changes: {item['key_changes']}"
                )
            law_context = "OFFICIAL BPR&D MAPPING DATA:\n" + "\n".join(context_list)
        else:
            law_context = "No direct database entry found for this section."

        # 5. AI Reasoning with Fallback Knowledge
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a Senior Indian Legal Expert specializing in the transition from IPC to BNS. "
                        "Rules:\n"
                        "1. If BPR&D data is provided, use it as the primary source.\n"
                        "2. If the data is missing, use your internal knowledge of the BNS (2023) to provide the mapping.\n"
                        "3. For IPC 302, explicitly state it is now BNS Section 101.\n"
                        "4. Always use bullet points and keep the summary professional."
                    )
                },
                {"role": "user", "content": f"Context: {law_context}\n\nQuestion: Analyze the transition for IPC Section {section_num}."}
            ],
            temperature=0.1, # Low temperature for high accuracy
            max_tokens=1024
        )

        # 6. Return response in the format the Frontend expects
        return jsonify({
            "analysis": completion.choices[0].message.content,
            "bns_section": bns_val if bns_val else "MAPPED",
            "source_data": db_response.data 
        })

    except Exception as e:
        print(f"CRITICAL_ERROR: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

# 7. Execution Logic for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
