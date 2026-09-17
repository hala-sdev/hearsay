from google import genai
from hearsay.config import gemini_api

client = genai.Client(api_key=gemini_api)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Write a short story about a robot learning to love.")

print(response.text)
