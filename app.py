import os
import json
from datetime import datetime, date, timedelta
import streamlit as st

from agent import (
    ai_chat,
    generate_plan,
    suggest_next_task,
    break_down_task,
)

st.set_page_config(
    page_title="TaskPilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Storage ----------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "plan" not in st.session_state:
    st.session_state.plan = None

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ---------- Helpers ----------
def add_task(title, description="", priority="Medium", category="General",
             due_date=None, estimated=30, subtasks=None):
    task = {
        "id": len(st.session_state.tasks) + 1,
        "title": title.strip(),
        "description": description.strip(),
        "priority": priority,
        "category": category,
        "due_date": due_date.isoformat() if isinstance(due_date, date) else str(due_date or ""),
        "estimated": int(estimated),
        "status": "Pending",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "subtasks": subtasks or [],
    }
    st.session_state.tasks.append(task)

def completed_count():
    return sum(t["status"] == "Completed" for t in st.session_state.tasks)

def pending_count():
    return sum(t["status"] == "Pending" for t in st.session_state.tasks)

def progress_pct():
    return round(completed_count() / len(st.session_state.tasks) * 100) if st.session_state.tasks else 0

def priority_icon(p):
    return {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(p, "⚪")

def save_tasks():
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.tasks, f, indent=2)

def load_tasks():
    if os.path.exists("tasks.json"):
        try:
            with open("tasks.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

if not st.session_state.tasks:
    st.session_state.tasks = load_tasks()

# ---------- CSS ----------
st.markdown("""
<style>
.main { background: #f7f8fc; }
.block-container { padding-top: 1.2rem; max-width: 1250px; }
.hero {
    padding: 28px;
    border-radius: 22px;
    background: linear-gradient(135deg,#101828,#243b72);
    color: white;
    margin-bottom: 22px;
}
.hero h1 { font-size: 42px; margin-bottom: 5px; }
.hero p { color: #dbe4ff; font-size: 17px; }
.card {
    background: white;
    border: 1px solid #e7eaf0;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 12px;
}
.small { color: #667085; font-size: 13px; }
.task-title { font-size: 18px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🚀 TaskPilot")
    st.caption("AI-powered personal task planner")

    pages = [
        "Dashboard",
        "Create Task",
        "AI Task Planner",
        "TaskPilot AI",
        "Smart Planner",
        "Analytics",
        "Task History",
    ]

    for p in pages:
        if st.button(p, use_container_width=True,
                     type="primary" if st.session_state.page == p else "secondary"):
            st.session_state.page = p
            st.rerun()

    st.divider()
    st.markdown("### Quick stats")
    st.metric("Total tasks", len(st.session_state.tasks))
    st.metric("Completed", completed_count())
    st.metric("Pending", pending_count())

    if st.button("💾 Save tasks", use_container_width=True):
        save_tasks()
        st.success("Saved")

# ---------- Dashboard ----------
if st.session_state.page == "Dashboard":
    st.markdown("""
    <div class="hero">
        <h1>🚀 TaskPilot AI</h1>
        <p>Plan smarter. Prioritize better. Get things done.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Total Tasks", len(st.session_state.tasks))
    c2.metric("✅ Completed", completed_count())
    c3.metric("⏳ Pending", pending_count())
    c4.metric("📈 Productivity", f"{progress_pct()}%")

    st.progress(progress_pct() / 100 if st.session_state.tasks else 0)

    st.markdown("### ⭐ Today's focus")

    if st.session_state.tasks:
        candidates = [t for t in st.session_state.tasks if t["status"] != "Completed"]
        if candidates:
            candidates.sort(key=lambda x: ({"High": 0, "Medium": 1, "Low": 2}.get(x["priority"], 3), x["due_date"] or "9999"))
            t = candidates[0]
            st.info(f"{priority_icon(t['priority'])} **{t['title']}** — {t['priority']} priority • {t['estimated']} min")
        else:
            st.success("🎉 All tasks completed!")
    else:
        st.info("No tasks yet. Create your first task or ask TaskPilot AI to build a plan.")

    st.markdown("### 📝 Recent tasks")
    for t in st.session_state.tasks[-5:][::-1]:
        with st.container(border=True):
            a, b, c = st.columns([5, 2, 1])
            a.markdown(f"**{priority_icon(t['priority'])} {t['title']}**")
            a.caption(f"{t['category']} • {t['estimated']} min • Due: {t['due_date'] or 'No deadline'}")
            b.write(t["status"])
            if t["status"] != "Completed":
                if c.button("✓", key=f"dashdone{t['id']}"):
                    t["status"] = "Completed"
                    save_tasks()
                    st.rerun()

# ---------- Create Task ----------
elif st.session_state.page == "Create Task":
    st.title("➕ Create Task")
    st.caption("Add a task manually or let AI break it into subtasks.")

    with st.form("create_task"):
        title = st.text_input("Task title", placeholder="e.g. Complete DBMS normalization")
        description = st.text_area("Description")
        c1, c2, c3 = st.columns(3)
        priority = c1.selectbox("Priority", ["High", "Medium", "Low"])
        category = c2.selectbox("Category", ["Study", "Work", "Project", "Personal", "General"])
        due = c3.date_input("Deadline", value=date.today())
        estimated = st.number_input("Estimated time (minutes)", 5, 1440, 30, step=5)
        submitted = st.form_submit_button("Create Task", type="primary", use_container_width=True)

    if submitted:
        if not title.strip():
            st.error("Enter a task title.")
        else:
            add_task(title, description, priority, category, due, estimated)
            save_tasks()
            st.success("Task created successfully!")
            st.rerun()

# ---------- AI Planner ----------
elif st.session_state.page == "AI Task Planner":
    st.title("🤖 AI Task Planner")
    st.write("Describe your goal and TaskPilot will turn it into an actionable plan.")

    goal = st.text_area(
        "What do you want to accomplish?",
        placeholder="Example: I need to prepare for my GATE exam in 30 days. I can study 3 hours every day.",
        height=140,
    )
    c1, c2 = st.columns(2)
    days = c1.number_input("Planning horizon (days)", 1, 90, 7)
    hours = c2.number_input("Available hours/day", 0.5, 16.0, 3.0, step=0.5)

    if st.button("✨ Generate Smart Plan", type="primary", use_container_width=True):
        if not goal.strip():
            st.warning("Describe your goal first.")
        else:
            with st.spinner("TaskPilot is planning..."):
                result = generate_plan(goal, days, hours)

            st.session_state.plan = result
            st.success("Plan generated!")

    if st.session_state.plan:
        st.markdown("### Your AI plan")
        st.markdown(st.session_state.plan)

        if st.button("➕ Add generated plan as a task"):
            add_task(
                title=f"AI Plan: {goal[:60]}",
                description=st.session_state.plan,
                priority="High",
                category="AI Plan",
                due_date=date.today() + timedelta(days=int(days)),
                estimated=int(hours * 60),
            )
            save_tasks()
            st.success("Plan added to your task list.")

# ---------- AI Chat ----------
elif st.session_state.page == "TaskPilot AI":
    st.title("💬 TaskPilot AI")
    st.caption("Ask for planning, prioritization, task breakdowns, or productivity advice.")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Ask TaskPilot anything...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        context = json.dumps(st.session_state.tasks, indent=2)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ai_chat(prompt, context)
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

# ---------- Smart Planner ----------
elif st.session_state.page == "Smart Planner":
    st.title("📅 Smart Planner")

    if not st.session_state.tasks:
        st.info("Create some tasks first.")
    else:
        active = [t for t in st.session_state.tasks if t["status"] != "Completed"]
        if active:
            with st.spinner("Finding your next best task..."):
                result = suggest_next_task(active)
            st.success(result)

        st.markdown("### All active tasks")
        active.sort(key=lambda x: ({"High": 0, "Medium": 1, "Low": 2}.get(x["priority"], 3), x["due_date"] or "9999"))
        for t in active:
            with st.container(border=True):
                st.markdown(f"### {priority_icon(t['priority'])} {t['title']}")
                st.write(f"**Priority:** {t['priority']}  |  **Category:** {t['category']}  |  **Due:** {t['due_date'] or 'None'}")
                st.caption(f"Estimated: {t['estimated']} minutes")
                if t["description"]:
                    st.write(t["description"])

                col1, col2 = st.columns(2)
                if col1.button("🤖 Break into subtasks", key=f"break{t['id']}"):
                    with st.spinner("Breaking down..."):
                        subtasks = break_down_task(t["title"], t["description"])
                    t["subtasks"] = subtasks
                    save_tasks()
                    st.rerun()

                if col2.button("✅ Complete", key=f"complete{t['id']}"):
                    t["status"] = "Completed"
                    save_tasks()
                    st.rerun()

                if t.get("subtasks"):
                    st.markdown("**Subtasks**")
                    for s in t["subtasks"]:
                        st.write(f"- {s}")

# ---------- Analytics ----------
elif st.session_state.page == "Analytics":
    st.title("📊 Productivity Analytics")

    total = len(st.session_state.tasks)
    done = completed_count()

    if total == 0:
        st.info("Add tasks to see analytics.")
    else:
        import pandas as pd

        df = pd.DataFrame(st.session_state.tasks)

        c1, c2, c3 = st.columns(3)
        c1.metric("Completion rate", f"{done / total * 100:.1f}%")
        c2.metric("High priority", int((df["priority"] == "High").sum()))
        c3.metric("Estimated workload", f"{int(df['estimated'].sum())} min")

        st.bar_chart(df["status"].value_counts())
        st.bar_chart(df["priority"].value_counts())

        st.markdown("### Task data")
        st.dataframe(
            df[["title", "priority", "category", "due_date", "estimated", "status"]],
            use_container_width=True,
            hide_index=True,
        )

# ---------- History ----------
elif st.session_state.page == "Task History":
    st.title("🗂️ Task History")

    if not st.session_state.tasks:
        st.info("No task history yet.")
    else:
        for t in reversed(st.session_state.tasks):
            with st.container(border=True):
                c1, c2 = st.columns([6, 1])
                c1.markdown(f"**{priority_icon(t['priority'])} {t['title']}**")
                c1.caption(f"Created: {t['created']} • Status: {t['status']} • Category: {t['category']}")
                if c2.button("🗑️", key=f"delete{t['id']}"):
                    st.session_state.tasks.remove(t)
                    save_tasks()
                    st.rerun()
