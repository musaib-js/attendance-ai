from openai import OpenAI
import os
from dotenv import load_dotenv
from genai.prompts import SQL_QUERY_GENERATION_PROMPT

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_sql_query(question):
    prompt = SQL_QUERY_GENERATION_PROMPT.format(user_requirement=question)

    response = client.responses.create(
        model="gpt-4o",
        input=prompt
    )

    return response.output_text.strip()
