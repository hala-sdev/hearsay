#from google import genai
from hearsay.config import gemini_api, groq_api
from groq import Groq
import json
#client = genai.Client(api_key=gemini_api)

#response = client.models.generate_content(
#    model="gemini-3.6-flash",
#    contents="Write a short story about a robot learning to love.")

#print(response.text)
groq_client = Groq(api_key=groq_api)

def extract_statements(text):
    response_g = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You extract the objective statements from the text and break it down to a list of statements. Replace all pronouns with the subject that it is referred to and if a statement includes several facts, split them into separate statements. For example, if a statement says 'the show is called Star. Critics praised the film for its stunning visuals.', then the only statement should be 'the show is called Star.' since the other sentence is an opinion so it gets dropped. Do not make facts overlap between statements. For example, if a statement says 'The cat is black and called snowy', it should be split into two statements: 'The cat is black.' and 'The cat is called snowy.'. Also do not repeat facts, if a statement says 'the company, known as XYZ, is an AI company', it should be split to 'the company is known as XYZ.' and 'XYZ is an AI company.'"},
            {"role": "user", "content": text}
        ],
        model = "openai/gpt-oss-120b",
        temperature = 0,
        response_format = {
            "type": "json_schema",
            "json_schema" : {
                "name": "extracted_statements",
                "schema": {
                    "type": "object",
                    "properties": {
                        "statements": {
                            "type": "array",
                            "items": {
                                "type": "string"
                                }
                                }},
                                "required": ["statements"]}}}
                                )
    claims = json.loads(response_g.choices[0].message.content)
    return claims["statements"]


if __name__ == "__main__":

    text = "NASA's Voyager 1 spacecraft, launched on September 5, 1977, is currently more than 24 billion kilometers from Earth. It reached interstellar space in August 2012, becoming the first human-made object to do so. The spacecraft carries a Golden Record containing 116 images and a variety of sounds from Earth, and its radio signals currently take over 22 hours to reach Earth."

    extracted_statements = extract_statements(text)
    print("Extracted Statements:")
    for statement in extracted_statements:
        print("-", statement)
