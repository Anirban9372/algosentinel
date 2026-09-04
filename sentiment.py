from google import genai
import os
import json


def score_sentiment(headlines: list) -> tuple:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    text = "\n".join(f"- {h}" for h in headlines)
    prompt = f"""You are a financial sentiment analyzer. Analyze these market headlines and return ONLY a JSON object, no markdown.

Headlines:
{text}

Return exactly this format:
{{"signal": "BULLISH" or "BEARISH" or "NEUTRAL", "confidence": 0.0 to 1.0, "reason": "one line"}}"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    clean = response.text.strip().replace("```json", "").replace("```", "").strip()
    data = json.loads(clean)
    return data["signal"], data["confidence"], data["reason"]
