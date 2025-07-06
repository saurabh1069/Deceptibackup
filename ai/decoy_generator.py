from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_fake_page(topic: str):
    prompt = f"Generate a believable but fake HTML admin login page about: {topic}. Include security hints and vulnerable-looking elements."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
