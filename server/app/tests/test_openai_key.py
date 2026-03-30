import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

OPENAI_KEY = os.getenv('OpenAI_Key')

client = OpenAI(api_key=OPENAI_KEY)

res = client.responses.create(
    model="gpt-5-mini",
    input="which number is behind 2 ",
)

print(res)