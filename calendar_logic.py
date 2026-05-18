# To fix the 'ModuleNotFoundError: No module named 'anthropic'', we need to install the package.
# Additionally, 'pandas' is used in the app.py and should also be installed.
# !pip install anthropic pandas

from anthropic import Anthropic
import json
import os
import re

# =========================================
# CLIENT
# =========================================

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# =========================================
# GENERATE CONTENT CALENDAR
# =========================================

def generate_calendar(
    brand_name,
    industry,
    platforms,
    pillars,
    language
):

    prompt = f"""
You are an expert social media content strategist.

CRITICAL RULES:
- Return ONLY valid JSON
- No markdown
- No explanation
- No text before or after JSON
- Generate EXACTLY 30 objects
- One post per day
- Days must be numbered 1 to 30

LANGUAGE RULE:
Write ALL content ONLY in {language}

Do not mix languages.
Do not use English unless language is English.

CONTENT QUALITY RULES:
- Make every post highly specific to the brand
- Avoid generic business content
- Mention bakery culture, pastries, desserts, coffee, customers, and Lyon naturally
- Include ideas around pastry classes and in-store experiences
- Make Instagram content visually driven
- Make Facebook content community-focused

Each JSON object must contain:

[
  {{
    "day": 1,
    "platform": "Instagram",
    "content_idea": "",
    "caption_starter": ""
  }}
]

Brand Name:
{brand_name}

Industry:
{industry}

Platforms:
{platforms}

Brand Strategy Context:
{pillars}

Language:
{language}
"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result = "".join(
        block.text
        for block in response.content
        if hasattr(block, "text")
    )

    return result

# =========================================
# GENERATE POST BRIEF
# =========================================

def generate_post_brief(
    day,
    platform,
    content_idea,
    brand_name,
    vibe,
    language
):

    prompt = f"""
You are a professional social media content writer.

STRICT RULE:
Write EVERYTHING ONLY in: {language}

No mixing languages.

Format:

Caption:
3–5 lines

Hashtags:
8–12 relevant hashtags

Image Direction:
Describe the visual clearly

Best Posting Time:
Best time + short reason

Brand: {brand_name}
Vibe: {vibe}
Platform: {platform}
Day: {day}
Content Idea: {content_idea}
Language: {language}
"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=600,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.content[0].text


# =========================================
# SAFE JSON HANDLING (DAY 8)
# =========================================

def extract_json_safe(text):

    text = text.strip()

    # Remove markdown fences
    text = re.sub(
        r"```json\s*",
        "",
        text
    )

    text = re.sub(
        r"```",
        "",
        text
    )

    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(
            text
        )

    except json.JSONDecodeError:
        pass

    # Try extracting JSON array/object
    match = re.search(
        r"(\[.*\]|\{.*\})",
        text,
        re.DOTALL
    )

    if match:

        try:
            return json.loads(
                match.group(1)
            )

        except:
            pass

    return None

# =========================================
# CLEAN CALENDAR DATA
# =========================================

def clean_calendar_data(data):

    cleaned = []

    for i, item in enumerate(data[:30]):

        if not isinstance(item, dict):

            item = {}

        cleaned_item = {

            "day": item.get(
                "day",
                i + 1
            ),

            "platform": str(
                item.get(
                    "platform",
                    "Instagram"
                )
            ),

            "content_idea": str(
                item.get(
                    "content_idea",
                    item.get(
                        "idea",
                        "Content idea missing"
                    )
                )
            ),

            "caption_starter": str(
                item.get(
                    "caption_starter",
                    item.get(
                        "caption",
                        "Caption missing"
                    )
                )
            ),

            "content_type": str(
                item.get(
                    "content_type",
                    "Post"
                )
            )
        }

        cleaned.append(cleaned_item)

    return cleaned

# =========================================
# SAFE CALENDAR GENERATION
# =========================================

def generate_calendar_safe(
    brand_name,
    industry,
    platforms,
    pillars,
    language
):

    for attempt in range(2):

        try:

            response = generate_calendar(
                brand_name,
                industry,
                platforms,
                pillars,
                language
            )

            data = extract_json_safe(response)

            if data is None:
                raise ValueError(
                    "Claude returned invalid JSON."
                )

            # Must be list
            if not isinstance(data, list):

                raise ValueError(
                    "Claude did not return a list."
                )

            # Clean data safely
            cleaned_data = clean_calendar_data(data)

            # Ensure exactly 30 posts
            while len(cleaned_data) < 30:

                cleaned_data.append({
                    "day": len(cleaned_data) + 1,
                    "platform": "Instagram",
                    "content_idea":
                        "Additional bakery content",
                    "caption_starter":
                        "Fresh pastries available today."
                })

            return cleaned_data[:30]

        except Exception as e:

            if attempt == 1:

                raise Exception(
                    f"Calendar generation failed: {str(e)}"
                )

    return []
