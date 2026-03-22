import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

# 1. Load Environment Variables
load_dotenv()

# 2. CREATE THE APP FIRST (Crucial!)
app = Flask(__name__)
CORS(app) 

# 3. Initialize Clients
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# 4. NOW define your routes
@app.route('/api/analyze', methods=['POST'])
def analyze_law():
    # Your function logic here...
