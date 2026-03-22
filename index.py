import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

# 1. Load Environment Variables
load_dotenv()

app = Flask(__name__)
CORS(app) # Allows your frontend to talk to this API

# 2. Initialize Clients
# These variables must be set in your Render Dashboard
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

@app.route('/api/analyze', methods=['POST'])
def analyze_law():
    user_data = request.json
    section_query = str(user_data.get('section', '')).strip()
    user_question = user_data.get('question', 'Explain the changes in this section.')

    if not section_query:
        return jsonify({"error": "Please provide a section number (e.g., 302 or 103)."}), 400

    # 3. Search Supabase using Partial Matching (ilike)
    # This ensures "302" finds "302" and "103" finds "103(1)", "103(2)", etc.
    try:
        db_response = supabase.table("laws_mapping")\
            .select("*")\
            .or_(f"ipc_section.ilike.%{section_query}%,bns_section.ilike.%{section_query}%")\
            .execute()
        
        # 4. Build Context from the BPR&D Data
        law_context = ""
        if db_response.data:
            context_list = []
            for item in db_response.data:
                context_list.append(
                    f"- BNS {item['bns_section']} (IPC {item['ipc_section']}): {item['title']}. "
                    f"Official Summary: {item['key_changes']}"
                )
            law_context = "OFFICIAL BPR&D MAPPING DATA:\n" + "\n".join(context_list)
        else:
            law_context = "No direct mapping found in the BPR&D database for this specific section number."

        # 5. AI Reasoning with Llama 3.3 70B
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are an expert Indian Legal Assistant. Use the provided BPR&D mapping "
                        "context to answer accurately. \n"
                        "Rules:\n"
                        "1. If context is provided, prioritize it over your general knowledge.\n"
                        "2. Explain the transition from IPC to BNS clearly.\n"
                        "3. Use bullet points for readability.\n"
                        "4. If no context is found, state that you are relying on general BNS knowledge."
                    )
                },
                {"role": "user", "content": f"{law_context}\n\nUser Question: {user_question}"}
            ],
            temperature=0.3, # Keeps it factual and consistent
            max_tokens=1024
        )

        return jsonify({
            "answer": completion.choices[0].message.content,
            "source_data": db_response.data # Sends the raw data back for the frontend to show
        })

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

# 6. Render-Specific Execution
if __name__ == '__main__':
    # Render assigns a port dynamically via the PORT env variable
    port = int(os.environ.get("PORT", 5000))
    # host='0.0.0.0' is required for the app to be reachable on Render
    app.run(host='0.0.0.0', port=port)
