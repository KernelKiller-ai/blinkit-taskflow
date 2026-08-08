import os
from dotenv import load_dotenv
from google import genai

# .env file ko explicitly load karein
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY .env file me missing hai!")

# Client me direct API key pass karein
client = genai.Client(api_key=api_key)

def generate_subtasks(task_title: str) -> str:
    """
    Gemini Interactions API se task ke subtasks generate karta hai.
    """
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=f"Task: '{task_title}'. Is task ke 3-5 clear subtasks Hindi/Hinglish me bullet points me batao."
    )
    return interaction.output_text