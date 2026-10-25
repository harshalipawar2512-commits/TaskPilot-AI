# 🚀 TaskPilot AI

TaskPilot is an AI-powered productivity and task-planning application built with Streamlit and OpenAI.

## Features

- Dashboard with task statistics
- Manual task creation
- AI-generated multi-day plans
- TaskPilot AI chat
- Smart next-task recommendation
- AI task breakdown into subtasks
- Productivity analytics
- Task history
- Local JSON task persistence
- Works without an API key for basic task management

## 1. Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## 2. Configure OpenAI

Create:

`.streamlit/secrets.toml`

and add:

```toml
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-5-mini"
```

Do NOT upload `secrets.toml` to GitHub.

## 3. Streamlit Cloud

Upload the project to GitHub and deploy `app.py`.

Then open:

**App → Settings → Secrets**

Add:

```toml
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-5-mini"
```

## Project structure

```text
TaskPilot/
├── app.py
├── agent.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml.example
```
