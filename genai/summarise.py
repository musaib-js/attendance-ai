from openai import OpenAI
import os
from dotenv import load_dotenv
from genai.prompts import SUMMARISATION_PROMPT

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarise_attendance_data(question, json_data):
    prompt = SUMMARISATION_PROMPT.format(question=question, json_data=json_data)

    response = client.responses.create(
        model="gpt-4o",
        input = prompt
    )

    return response.output_text.strip()
