import streamlit as st
import anthropic
from datetime import date, timedelta
import os

# ---------------- API SETUP ----------------

api_key = os.environ.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(
    api_key=api_key
)

# ---------------- READ MODULE 1 DATA ----------------

strategy_data = st.session_state.get(
    "strategy_data",
    {}
)

brand_name = strategy_data.get(
    "business_name",
    "Maison Dubois"
)

industry = strategy_data.get(
    "industry",
    "Bakery"
)

language = strategy_data.get(
    "language",
    "English"
)

platforms_from_strategy = strategy_data.get(
    "platforms",
    ["Instagram"]
)

tone_from_strategy = strategy_data.get(
    "brand_tone",
    "Friendly"
)

content_pillars = strategy_data.get(
    "content_pillars",
    []
)

pillar_options = []

for pillar in content_pillars:

    if isinstance(pillar, dict):

        pillar_options.append(
            pillar.get(
                "title",
                "Content"
            )
        )

if not pillar_options:

    pillar_options = [
        "Behind the scenes",
        "Customer stories",
        "Tips and advice"
    ]

# ---------------- UI ----------------

st.title("📅 Content Calendar Generator")

st.caption(
    "Generate a post brief from Module 1 strategy data."
)

st.success(
    f"Connected to strategy for {brand_name}"
)

# ---------------- INPUTS ----------------

pillar = st.selectbox(
    "Content Pillar",
    pillar_options
)

platform = st.selectbox(
    "Platform",
    platforms_from_strategy
)

tone = st.selectbox(
    "Tone",
    [
        tone_from_strategy,
        "Professional",
        "Friendly",
        "Bold",
        "Luxury",
        "Playful"
    ]
)

post_date = st.date_input(
    "Post Date",
    value=date.today()
)

# ---------------- GENERATE SINGLE POST ----------------

if st.button("Generate Post Brief"):

    with st.spinner("Creating your brief..."):

        prompt = f"""
You are a content strategist writing a creative brief.

Brand Name:
{brand_name}

Industry:
{industry}

Language:
{language}

Content Pillar:
{pillar}

Platform:
{platform}

Tone:
{tone}

Post Date:
{post_date}

Write:
1. Post Objective
2. Key Message
3. Content Direction
4. Format
5. Call To Action

Keep it realistic and specific.
"""

        response = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=400,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        brief = response.content[0].text

    st.success("Brief ready.")

    st.subheader(
        f"{platform} · {pillar}"
    )

    st.write(brief)

# ---------------- GENERATE 30 DAY CALENDAR ----------------

if st.button("Generate 30-Day Calendar"):

    st.write("### 📅 30-Day Content Plan")

    for i in range(30):

        day = date.today() + timedelta(days=i)

        with st.expander(f"Day {i + 1} — {day}"):

            prompt = f"""
Create a social media post brief.

Brand:
{brand_name}

Industry:
{industry}

Language:
{language}

Platform:
{platform}

Tone:
{tone}

Content Pillar:
{pillar}

Date:
{day}

Include:
1. Post Objective
2. Key Message
3. Content Direction
4. Format
5. CTA
"""

            response = client.messages.create(
                model="claude-opus-4-1",
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            st.write(
                response.content[0].text
            )
