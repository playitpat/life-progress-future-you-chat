import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime, date

# ---------- Simple persistence layer ----------

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

GOALS_FILE = os.path.join(DATA_DIR, "goals.json")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")
CHAT_FILE = os.path.join(DATA_DIR, "future_chat.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error saving data to {path}: {e}")


def init_state_from_disk():
    """Load goals, logs, and chat history from disk into session_state once."""
    if st.session_state.get("initialized_from_disk"):
        return

    st.session_state["goals"] = load_json(GOALS_FILE, [])
    st.session_state["logs"] = load_json(LOGS_FILE, [])
    st.session_state["future_chat_history"] = load_json(CHAT_FILE, [])

    st.session_state["initialized_from_disk"] = True


def save_goals_to_disk():
    save_json(GOALS_FILE, st.session_state.get("goals", []))


def save_logs_to_disk():
    save_json(LOGS_FILE, st.session_state.get("logs", []))


def save_chat_to_disk():
    save_json(CHAT_FILE, st.session_state.get("future_chat_history", []))


# Initialize state from disk once per browser session
init_state_from_disk()

# Sidebar menu
st.sidebar.title('Navigation')
page = st.sidebar.selectbox(
    'Go to',
    ['Home', 'Set Goals', 'Log Today', 'Dashboard', 'Chat with Future You']
)

# ----------------------
# Home
# ----------------------
if page == 'Home':
    st.title("🌱 Life Progress Dashboard")
    st.write(
        "Welcome. This is your space to design the person you are becoming.  \n"
        "Set goals, log small steps, and let future you react to your progress."
    )

    # Simple summary stats
    num_goals = len(st.session_state["goals"])
    num_logs = len(st.session_state["logs"])
    categories = sorted({g["Category"] for g in st.session_state["goals"]}) if st.session_state["goals"] else []

    if st.session_state["logs"]:
        try:
            last_log_date = max(
                datetime.fromisoformat(log["Date"]) for log in st.session_state["logs"]
            )
            last_log_str = last_log_date.strftime("%Y-%m-%d")
        except Exception:
            last_log_str = "Unknown"
    else:
        last_log_str = "No logs yet"

    st.subheader("Today at a glance")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active goals", num_goals)
    with col2:
        st.metric("Total log entries", num_logs)
    with col3:
        st.metric("Last logged day", last_log_str)

    if categories:
        st.caption("Goal areas: " + ", ".join(categories))
    else:
        st.caption("Goal areas will appear here once you create your first goal.")

    st.markdown("---")

    st.subheader("How this app works")

    st.markdown(
        """
        **Set Goals**  
        • Define what you want to work on in areas like career, education, finance, health, hobbies, and relationships  

        **Log Today**  
        • Record what you actually did each day so you can see your real habits  

        **Dashboard**  
        • Track how often you show up for each goal and see where your energy is going  

        **Chat with Future You**  
        • Talk to a future version of yourself who reacts to your data, not just to your words  
        """
    )

    st.info("Tip: Start by creating one small, easy goal in the Set Goals section. Future you will notice.")

# ----------------------
# Set Goals
# ----------------------
elif page == 'Set Goals':
    st.header('Set Goals')

    st.title("🎯 Set Your Goals")
    st.write(
        "Define the habits and routines that build a balanced and meaningful life.  \n"
        "Small steps today shape future you 🌱"
    )

    st.subheader("Add a New Goal")

    # Goal creation form
    with st.form("new_goal_form"):
        goal_name = st.text_input("Goal Name", placeholder="Run a marathon")

        category = st.selectbox(
            "Category",
            ["Career", "Education", "Finance", "Health", "Hobbies", "Relationships"]
        )

        goal_description = st.text_input(
            "Why is this goal important",
            placeholder="I want more energy and a healthier routine"
        )

        submitted = st.form_submit_button("➕ Add Goal")

    if submitted:
        if goal_name.strip():
            new_goal = {
                "Goal": goal_name.strip(),
                "Category": category,
                "Description": goal_description.strip(),
            }
            st.session_state["goals"].append(new_goal)
            save_goals_to_disk()
            st.success(f"Goal '{goal_name}' added! Keep going 🚀")
        else:
            st.warning("Please enter a goal name before adding.")

    st.markdown("---")

    st.subheader("Your Current Goals")

    if not st.session_state["goals"]:
        st.info("You do not have any goals yet. Add one above to get started.")
    else:
        # Display each goal as a small card with a delete button
        for i, goal in enumerate(st.session_state["goals"]):
            col1, col2, col3 = st.columns([4, 3, 1])

            with col1:
                st.write(f"**{goal['Goal']}**")
                if goal["Description"]:
                    st.caption(goal["Description"])

            with col2:
                st.write(f"Category: `{goal['Category']}`")

            with col3:
                if st.button("Delete", key=f"delete_{i}"):
                    del st.session_state["goals"][i]
                    save_goals_to_disk()
                    st.rerun()

        st.caption("Tip: Good goals are simple, clear, and repeatable.")

# ----------------------
# Log Today
# ----------------------
elif page == 'Log Today':
    st.header('Log Today')

    # Make sure goals exist
    if not st.session_state["goals"]:
        st.info("You do not have any goals yet. Go to **Set Goals** to create one before logging progress.")
    else:
        st.title("📝 Log Today's Progress")

        st.write(
            "Record what you did today for your goals.  \n"
            "Future-you will look back at these small steps 🌱"
        )

        st.subheader("Add a New Entry")

        goal_names = [g["Goal"] for g in st.session_state["goals"]]

        with st.form("log_today_form"):
            selected_goal = st.selectbox(
                "Which goal did you work on today",
                goal_names
            )

            log_date = st.date_input("Date", value=date.today())

            note = st.text_input(
                "Short note",
                placeholder="Easy run, heavy day at work, studied grammar, etc."
            )

            submitted_log = st.form_submit_button("💾 Save Log")

        if submitted_log:
            new_log = {
                "Goal": selected_goal,
                "Date": log_date.isoformat(),
                "Note": note.strip(),
            }
            st.session_state["logs"].append(new_log)
            save_logs_to_disk()
            st.success(f"Progress logged for '{selected_goal}'")

        st.markdown("---")
        st.subheader("Recent Entries")

        if not st.session_state["logs"]:
            st.info("No progress logged yet. Add your first entry above.")
        else:
            # Show the most recent entries (sorted by date descending)
            logs_df = pd.DataFrame(st.session_state["logs"])
            logs_df["Date"] = pd.to_datetime(logs_df["Date"])
            logs_df = logs_df.sort_values("Date", ascending=False).head(20)

            st.dataframe(logs_df, use_container_width=True)
            st.caption("These recent logs will feed your dashboard and future-you chat.")

# ----------------------
# Dashboard
# ----------------------
elif page == 'Dashboard':
    st.header('Dashboard')

    st.title("📊 Your Progress Overview")

    if not st.session_state["goals"]:
        st.info("You do not have any goals yet. Go to **Set Goals** to create one before using the dashboard.")
    elif not st.session_state["logs"]:
        st.info("You have not logged any progress yet. Go to **Log Today** to add your first entries.")
    else:
        # Build logs dataframe
        logs_df = pd.DataFrame(st.session_state["logs"]).copy()
        logs_df["Date"] = pd.to_datetime(logs_df["Date"])

        # Build goals dataframe for category information
        goals_df = pd.DataFrame(st.session_state["goals"]).copy()  # columns: Goal, Category, Description

        # Merge logs with goal categories
        logs_merged = logs_df.merge(goals_df[["Goal", "Category"]], on="Goal", how="left")

        # High level stats
        total_goals = len(goals_df)
        total_logs = len(logs_df)
        distinct_days = logs_df["Date"].dt.date.nunique()
        categories = sorted(goals_df["Category"].unique())

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active goals", total_goals)
        with col2:
            st.metric("Total log entries", total_logs)
        with col3:
            st.metric("Days with activity", distinct_days)

        st.caption("Goal areas: " + ", ".join(categories))

        st.markdown("---")

        st.subheader("Progress by Goal")

        # Aggregate per goal - qualitative: count of logs and last activity
        goal_summary = (
            logs_merged
            .groupby(["Goal", "Category"], as_index=False)
            .agg(
                Entries=("Note", "count"),
                Last_Activity=("Date", "max"),
            )
        )

        # Sort by category then goal
        goal_summary = goal_summary.sort_values(["Category", "Goal"])

        # Format date for display
        goal_summary["Last_Activity"] = goal_summary["Last_Activity"].dt.strftime("%Y-%m-%d")

        st.dataframe(goal_summary, use_container_width=True)
        st.caption("Entries is the number of times you logged progress for each goal.")

        st.markdown("---")

        st.subheader("Where Your Effort Has Gone")

        chart_data = goal_summary.set_index("Goal")["Entries"]
        st.bar_chart(chart_data)

        st.caption("This chart shows how often you have shown up for each goal so far.")

# ----------------------
# Chat with Future You
# ----------------------
elif page == 'Chat with Future You':
    st.header('Chat with Future You')
    st.title("🧭 Chat with Future You")

    # Try to import OpenAI only inside this page
    try:
        from openai import OpenAI
    except ModuleNotFoundError:
        st.error(
            "The 'openai' package is not available.\n"
            "Make sure it is listed in requirements.txt and redeploy the app."
        )
        st.stop()

    # Get API key (Streamlit secrets or environment)
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error("No OPENAI_API_KEY found in environment or Streamlit secrets.")
        st.stop()

    client = OpenAI(api_key=api_key)

    # Required data
    if not st.session_state["goals"]:
        st.info("Please create at least one goal before using this page.")
        st.stop()
    if not st.session_state["logs"]:
        st.info("Please add at least one log entry before chatting with future you.")
        st.stop()

    # Text summaries
    logs_df = pd.DataFrame(st.session_state["logs"]).copy()
    logs_df["Date"] = pd.to_datetime(logs_df["Date"])

    goals_df = pd.DataFrame(st.session_state["goals"]).copy()

    cutoff = datetime.now().date() - pd.Timedelta(days=30)
    recent_logs = logs_df[logs_df["Date"].dt.date >= cutoff]

    if not recent_logs.empty:
        recent_summary = (
            recent_logs
            .groupby("Goal", as_index=False)
            .agg(
                Entries=("Note", "count"),
                Last_Activity=("Date", "max")
            )
        )
        recent_summary["Last_Activity"] = recent_summary["Last_Activity"].dt.strftime("%Y-%m-%d")
    else:
        recent_summary = pd.DataFrame(columns=["Goal", "Entries", "Last_Activity"])

    goals_text = "\n".join(
        f"- {g['Goal']} (Category: {g['Category']})" +
        (f" — {g['Description']}" if g["Description"] else "")
        for g in st.session_state["goals"]
    )

    if not recent_summary.empty:
        progress_text = "\n".join(
            f"- {row['Goal']}: {row['Entries']} log(s), last activity {row['Last_Activity']}."
            for _, row in recent_summary.iterrows()
        )
    else:
        progress_text = "No activity logged in the last 30 days."

    # Layout
    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.subheader("Ask Future You")

        horizon = st.selectbox(
            "Time horizon",
            ["6 months", "1 year", "2 years", "5 years"],
            index=1
        )

        tone = st.selectbox(
            "Tone of future you",
            ["Supportive coach", "Tough love", "Best friend", "Stoic mentor"],
            index=0
        )

        user_question = st.text_area(
            "Your question",
            placeholder="Example: Am I on the right track?",
            height=100
        )

        ask = st.button("✨ Talk to Future Me", use_container_width=True)
        clear_chat = st.button("🧹 Clear conversation", use_container_width=True)

        with st.expander("Current goals & activity"):
            st.markdown("**Goals:**")
            st.text(goals_text or "No goals.")
            st.markdown("**Last 30 days:**")
            st.text(progress_text)

    with right_col:
        st.subheader("Conversation")

        if not st.session_state["future_chat_history"]:
            st.info("Your conversation will appear here.")
        else:
            for msg in st.session_state["future_chat_history"]:
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['content']}")
                else:
                    st.markdown(f"**Future You:** {msg['content']}")

    # ---- BUTTON LOGIC ----

    if clear_chat:
        st.session_state["future_chat_history"] = []
        save_chat_to_disk()
        st.rerun()

    if ask:
        if not user_question.strip():
            st.warning("Enter a question first.")
            st.stop()

        st.session_state["future_chat_history"].append(
            {"role": "user", "content": user_question}
        )
        save_chat_to_disk()

        system_prompt = f"""
You are the user's future self from {horizon}.
You reason only from their goals and recent activity.
Your tone is: {tone}.
Respond in 3–6 short paragraphs.
"""

        user_prompt = f"""
Goals:
{goals_text}

Recent progress:
{progress_text}

My question to my future self:
"{user_question}"
"""

        try:
            with st.spinner("Thinking as future you..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=600,
                )

            answer = response.choices[0].message.content

            st.session_state["future_chat_history"].append(
                {"role": "assistant", "content": answer}
            )
            save_chat_to_disk()
            st.rerun()

        except Exception as e:
            st.error(f"OpenAI error: {e}")
