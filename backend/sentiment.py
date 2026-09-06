from google import genai
import os
import json


def score_sentiment(headlines: list) -> tuple:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    text = "\n".join(f"- {h}" for h in headlines)
    prompt = f"""You are an aggressive financial sentiment analyzer. Analyze these market headlines and determine the dominant directional bias (BULLISH or BEARISH).

Headlines:
{text}

Return exactly this JSON format:
{{"signal": "BULLISH" or "BEARISH", "confidence": 0.80, "reason": "one line summary"}}"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    clean = response.text.strip().replace("```json", "").replace("```", "").strip()
    data = json.loads(clean)
    return data["signal"], data["confidence"], data["reason"]
