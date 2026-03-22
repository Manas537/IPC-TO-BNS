import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

# 1. Load Environment Variables
load_dotenv()

app = Flask(__name__)

# UPDATED: Restricted CORS to only your Vercel Frontend
CORS(app, resources={r"/api/*": {"origins": "https://ipc-to-bns-mauve.vercel.app"}})

# 2. Initialize Clients
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

@app.route('/api/analyze', methods=['POST'])
def analyze_law():
    user_data = request.json
    
    # UPDATED: The frontend sends 'query', so we extract the number from it
    raw_query = str(user_data.get('query', '')).strip()
    # Extract just the digits for the database search (e.g., "302" from "IPC 302")
    section_num = ''.join(filter(str.isdigit, raw_query))

    if not section_num:
        return jsonify({"error": "Please provide a valid section number."}), 400

    try:
        # 3. Search Supabase (ilike for partial matching)
        db_response = supabase.table("laws_mapping")\
            .select("*")\
            .or_(f"ipc_section.ilike.%{section_num}%,bns_section.ilike.%{section_num}%")\
            .execute()
        
        # 4. Build Context
        law_context = ""
        bns_val = "NOT_FOUND" # Default if not found
        
        if db_response.data:
            context_list = []
            # Grab the first match for the big header
            bns_val = db_response.data[0].get('bns_section', 'MAP_ERROR')
            
            for item in db_response.data:
                context_list.append(
                    f"- BNS {item['bns_section']} (IPC {item['ipc_section']}): {item['title']}. "
                    f"Official Summary: {item['key_changes']}"
                )
            law_context = "OFFICIAL BPR&D MAPPING DATA:\n" + "\n".join(context_list)
        else:
            law_context = "No direct mapping found in the BPR&D database for this specific section number."

        # 5. AI Reasoning
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a Precision Legal Mapper. Your job is to summarize the transition "
                        "from IPC to BNS based ONLY on BPR&D data. \n"
                        "Rules:\n"
                        "1. Clearly state if the punishment or definition has changed.\n"
                        "2. Use bullet points.\n"
                        "3. Keep it brief and professional."
                    )
                },
                {"role": "user", "content": f"{law_context}\n\nQuestion: Analyze IPC {section_num} to BNS transition."}
            ],
            temperature=0.1, # Low temperature for 100% precision
            max_tokens=1024
        )

        # UPDATED: Response keys now match what the index.html expects
        return jsonify({
            "analysis": completion.choices[0].message.content,
            "bns_section": bns_val,
            "source_data": db_response.data 
        })

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
