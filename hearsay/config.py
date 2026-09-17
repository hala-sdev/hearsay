from dotenv import load_dotenv
import os

load_dotenv()
gemini_api = os.getenv("GEMINI_API_KEY")

if gemini_api is None:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.") 