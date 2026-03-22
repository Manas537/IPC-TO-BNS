@app.route('/api/analyze', methods=['POST'])
def analyze_law():
    user_data = request.json
    raw_query = str(user_data.get('query', '')).strip()
    section_num = ''.join(filter(str.isdigit, raw_query))

    if not section_num:
        return jsonify({"error": "Valid section number required."}), 400

    try:
        # IMPROVED SEARCH: Handles exact matches and sub-sections
        db_response = supabase.table("laws_mapping")\
            .select("*")\
            .or_(f"ipc_section.eq.{section_num},ipc_section.ilike.{section_num}(%,ipc_section.ilike.%, {section_num},%")\
            .execute()
        
        law_context = ""
        bns_val = ""

        if db_response.data:
            bns_val = db_response.data[0].get('bns_section', '')
            context_list = [f"- BNS {i['bns_section']} (IPC {i['ipc_section']}): {i['title']}. Changes: {i['key_changes']}" for i in db_response.data]
            law_context = "OFFICIAL BPR&D DATA:\n" + "\n".join(context_list)
        
        # SMART AI PROMPT: Forces knowledge of IPC 302 -> BNS 101
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a Precision Legal Engine for Indian Law. \n"
                        "CRITICAL KNOWLEDGE: IPC 302 (Murder) is now BNS Section 101. \n"
                        "1. If 'OFFICIAL BPR&D DATA' is provided, summarize it.\n"
                        "2. If the data is empty, use your internal knowledge of BNS 2023 to provide the mapping.\n"
                        "3. Format: **BNS Section No**, **Summary**, and **Punishment Changes**."
                    )
                },
                {"role": "user", "content": f"DATA: {law_context}\n\nMapping Request: IPC Section {section_num}"}
            ],
            temperature=0.1
        )

        return jsonify({
            "analysis": completion.choices[0].message.content,
            "bns_section": bns_val if bns_val else "MAPPED", # Fallback for UI
            "source_data": db_response.data 
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
