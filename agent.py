import os
from typing import List

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def get_api_key():
    """Get Groq API key from Streamlit Secrets first, then environment."""
    try:
        import streamlit as st

        key = st.secrets.get("GROQ_API_KEY", None)

        if key:
            return key

    except Exception:
        pass

    return os.getenv("GROQ_API_KEY")


def get_client():
    """Create an OpenAI-compatible client configured for Groq."""
    key = get_api_key()

    if not key or OpenAI is None:
        return None

    return OpenAI(
        api_key=key,
        base_url="https://api.groq.com/openai/v1"
    )
def call_ai(prompt: str) -> str:
    """Send a compact prompt to Groq."""
    client = get_client()

    if client is None:
        return (
            "⚠️ **Groq AI is not configured.**\n\n"
            "TaskPilot can still manage saved tasks, but AI features need "
            "`GROQ_API_KEY` in Streamlit Secrets or your environment.\n\n"
            "For Streamlit Cloud, add it under **Settings → Secrets**."
        )

    model = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b"
    )

    # Keep the request below Groq's token limit
    max_chars = 24000

    if len(prompt) > max_chars:
        prompt = prompt[:max_chars] + (
            "\n\n[Additional context shortened to fit the AI request limit.]"
        )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=1500,
        )

        return response.choices[0].message.content

    except Exception as e:
        return (
            f"⚠️ **AI request failed.**\n\n"
            f"Error: `{str(e)}`"
        )

def generate_plan(goal: str, days: int, hours: float) -> str:
    prompt = f"""
You are TaskPilot, an intelligent productivity planning agent.

Create a practical {days}-day plan for this goal:

{goal}

Available study/work time: {hours} hours per day.

Return:

1. Goal summary
2. Priority strategy
3. Day-by-day plan
4. Specific tasks and estimated minutes
5. Milestones
6. Final review checklist

Keep the plan realistic, actionable, and concise.
"""

    result = call_ai(prompt)

    if result.startswith("⚠️"):
        return f"""### Goal
{goal}

### {days}-Day Starter Plan

- **Day 1:** Define the exact outcome and list all required tasks.
- **Day 2:** Complete the highest-priority task.
- **Day 3:** Continue the core work and review progress.
- **Day 4:** Complete the next major task.
- **Day 5:** Practice/review and fix weak areas.
- **Day 6:** Finish remaining important work.
- **Day 7:** Review, test yourself, and plan the next cycle.

**Daily capacity:** approximately {hours} hours.

> Connect a Groq API key to receive a fully personalized AI-generated plan.
"""

    return result


def ai_chat(message: str, context: str) -> str:
    prompt = f"""
You are TaskPilot AI, a personal productivity assistant.

User request:
{message}

Current task list:
{context}

Help the user directly.

If they ask what to do next, consider:
- priority
- deadline
- estimated time
- task status
- dependencies

Give concise actionable advice.

Do not invent completed tasks or deadlines.
"""

    return call_ai(prompt)


def suggest_next_task(tasks: list) -> str:
    if not tasks:
        return "🎉 You have no pending tasks."

    prompt = f"""
You are TaskPilot's prioritization engine.

Choose the best next task from this list:

{tasks}

Consider:

- urgency/deadline
- priority
- estimated effort
- dependencies implied by descriptions

Return the recommended task and a short reason.
"""

    result = call_ai(prompt)

    if result.startswith("⚠️"):
        ordered = sorted(
            tasks,
            key=lambda x: (
                {
                    "High": 0,
                    "Medium": 1,
                    "Low": 2
                }.get(x.get("priority"), 3),

                x.get("due_date") or "9999",

                x.get("estimated", 9999),
            ),
        )

        t = ordered[0]

        return (
            f"🎯 **Next best task:** {t['title']}\n\n"
            f"Reason: {t.get('priority', 'Unknown')} priority "
            f"with deadline "
            f"{t.get('due_date') or 'not specified'}."
        )

    return result


def break_down_task(title: str, description: str) -> List[str]:
    prompt = f"""
Break this task into 4-8 small actionable subtasks.

Task:
{title}

Description:
{description}

Return ONLY a numbered list of subtasks.
"""

    result = call_ai(prompt)

    if result.startswith("⚠️"):
        return [
            f"Define the expected outcome of: {title}",
            "Collect required resources/information",
            "Complete the main work",
            "Review the result",
            "Mark the task complete and record any follow-up",
        ]

    lines = []

    for line in result.splitlines():
        clean = line.strip().lstrip("0123456789.- ").strip()

        if clean:
            lines.append(clean)

    return lines[:8]
