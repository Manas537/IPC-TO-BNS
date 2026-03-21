import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app)

# Clients Setup
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_ANON_KEY"))
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/api/analyze', methods=['POST'])
def analyze_law():
    user_data = request.json
    section_query = user_data.get('section')
    user_question = user_data.get('question', 'Explain this section.')

    # 1. Look up the ACTUAL data in Supabase first (The "Source of Truth")
    db_response = supabase.table("laws_mapping").select("*").or_(f"ipc_section.eq.{section_query},bns_section.eq.{section_query}").execute()
    
    law_context = ""
    if db_response.data:
        law = db_response.data[0]
        law_context = f"Context: IPC {law['ipc_section']} is now BNS {law['bns_section']}. Title: {law['title']}. Changes: {law['key_changes']}"

    # 2. Ask Llama 3.3 70B to explain it using that context
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional Indian Legal Assistant. Use the provided mapping context to answer accurately. If no context is found, rely on your knowledge of BNS 2023 but add a disclaimer."},
                {"role": "user", "content": f"{law_context}\n\nUser Question: {user_question}"}
            ],
            temperature=0.5,
            max_tokens=1024
        )
        
        return jsonify({
            "answer": completion.choices[0].message.content,
            "metadata": db_response.data[0] if db_response.data else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
