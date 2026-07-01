from google import genai
from config import GEMINI_KEY

client = genai.Client(api_key=GEMINI_KEY)

text = "Spring Boot makes it easy to create stand-alone, production-grade Spring based Applications that you can just run. Most Spring Boot applications need minimal Spring configuration."

# AI에게 '핵심만 한국어로'라고 지시
prompt = f"다음 영어 글을 한국어로 핵심만 3~4줄로 요약해줘:\n\n{text}"

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)
print(response.text)