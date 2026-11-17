from dotenv import load_dotenv
import os

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO")
gemini_api = os.getenv("GEMINI_API_KEY")
groq_api = os.getenv("GROQ_API_KEY")
qdrant_api = os.getenv("QDRANT_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL is not set in .env")
if "connect_timeout" not in db_url:
    db_url += "&connect_timeout=10"

sqlalchemy_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
collection_name = "wiki_passages"
dense_embedding_model = "BAAI/bge-small-en-v1.5"   
sparse_embedding_model = "Qdrant/bm25"
dense_vector_name = "bge_small"
sparse_vector_name = "bm25"
judge_model = "gemini-3.5-flash-lite"

if gemini_api is None:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.") 

if groq_api is None:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

if qdrant_api is None:
    raise ValueError("QDRANT_API_KEY is not set in the environment variables.")

if qdrant_url is None:
    raise ValueError("QDRANT_URL is not set in the environment variables.")


max_text_chars =1000
checks_per_ip_per_hour = int(os.getenv("CHECKS_PER_IP_PER_HOUR", "5"))
checks_per_day = int(os.getenv("CHECKS_PER_DAY", "50"))
max_attempts = 3