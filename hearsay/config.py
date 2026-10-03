from dotenv import load_dotenv
import os

load_dotenv()
gemini_api = os.getenv("GEMINI_API_KEY")
groq_api = os.getenv("GROQ_API_KEY")
qdrant_api = os.getenv("QDRANT_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")

if gemini_api is None:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.") 

if groq_api is None:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

if qdrant_api is None:
    raise ValueError("QDRANT_API_KEY is not set in the environment variables.")

if qdrant_url is None:
    raise ValueError("QDRANT_URL is not set in the environment variables.")