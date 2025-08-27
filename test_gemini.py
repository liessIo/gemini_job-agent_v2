# test_gemini.py

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file.")
genai.configure(api_key=api_key)

try:
    print("Attempting to initialize GenerativeModel...")
    # This is the line that causes errors in the other file
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    print("Model initialized successfully.")
    
    print("Sending a test prompt...")
    response = model.generate_content("Hello, world!")
    
    print("Successfully received a response from the API.")
    print("---")
    print(response.text)
    print("---")
    print("✅ Test successful!")

except Exception as e:
    print(f"❌ Test failed with an error: {e}")