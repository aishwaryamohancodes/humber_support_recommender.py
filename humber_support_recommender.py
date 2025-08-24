import streamlit as st
from collections import Counter, defaultdict
import streamlit.components.v1 as components

HUMBER_SLS_URL = "https://humber.ca/learningresources/"

SERVICE_DESCRIPTIONS = {
    "Note Taking Services": "Note creation for ALS-registered students via PALS (by referral).",
    "Learning Skills Workshops": "Workshops on time mgmt, test prep, memory, presentations, group work, APA, integrity, etc.",
    "Learning Support Drop-In": "One-on-one drop-in for non-course-specific skills: focus, strategies, digital learning tips.",
    "Peer Tutoring": "1:1 (or small group) course-specific support; in-person or virtual via Upswing.",
    "Math & Writing Centre": "Specialized tutors for math, writing, ESL, physics, stats, calculus; North & Lakeshore.",
    "PASS": "Peer Assisted Study Sessions—structured, weekly, peer-led review for tough courses.",
    "STEM Specialist": "Advanced STEM help when needs exceed general tutoring support (last-resort escalation).",
}

# ---------------------------
# App State
# ---------------------------
if "step" not in st.session_state:
    st.session_state.step = "Q0"
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "scores" not in st.session_state:
    st.session_state.scores = defaultdict(int)
if "finished" not in st.session_state:
    st.session_state.finished = False

def add_score(*services, w=1):
    for s in services:
        st.session_state.scores[s] += w

def restart():
    st.session_state.step = "Q0"
    st.session_state.answers = {}
    st.session_state.scores = defaultdict(int)
    st.session_state.finished = False

def go(next_step):
    st.session_state.step = next_step

def finish():
    st.session_state.finished = True

# ---------------------------
# Fallbacks to guarantee Top 3
# ---------------------------
def prioritized_fallbacks(answers):
    prio = []
    if answers.get("Q0") == "Yes":
        prio.append("Note Taking Services")

    if answers.get("Q1", "").startswith("Academic"):
        if answers.get("Q1_pref") == "One-on-one":
            prio += ["Peer Tutoring", "Math & Writing Centre", "Learning Support Drop-In",
                     "Learning Skills Workshops", "PASS", "STEM Specialist"]
        else:
            prio += ["PASS", "Peer Tutoring", "Learning Skills Workshops",
                     "Learning Support Drop-In", "Math & Writing Centre", "STEM Specialist"]
    else:
        prio += ["Learning Skills Workshops", "Learning Support Drop-In", "Peer Tutoring",
                 "PASS", "Math & Writing Centre", "STEM Specialist"]

    seen, ordered = set(), []
    for s in prio:
        if s not in seen:
            ordered.append(s); seen.add(s)
    return ordered

def ensure_top3(counter, answers):
    counts = Counter(counter)

    if answers.get("Q0") == "Yes":
        counts["Note Taking Services"] += 1

    if answers.get("Q1") == "Learning skills / study strategies":
        counts["Learning Skills Workshops"] += 1
        counts["Learning Support Drop-In"] += 1

    if answers.get("Q1", "").startswith("Academic") and answers.get("Q1_pref") == "One-on-one":
        counts["Peer Tutoring"] += 1

    if answers.get("Q1", "").startswith("Academic") and answers.get("Q1_pref") == "Group":
        counts["PASS"] += 1

    if len(counts) < 3:
        for svc in prioritized_fallbacks(answers):
            if svc not in counts:
                counts[svc] = 1
            if len(counts) >= 3:
                break

    universal = ["Peer Tutoring", "Learning Skills Workshops", "Learning Support Drop-In",
                 "Math & Writing Centre", "PASS", "STEM Specialist", "Note Taking Services"]
    i = 0
    while len(counts) < 3 and i < len(universal):
        counts[universal[i]] += 1
        i += 1

    return counts

# ---------------------------
# UI Header
# ---------------------------
st.title("🎓 Humber Learning Services Recommender")
st.caption("Answer a few quick questions to get personalized support recommendations.")
if st.button("🔄 Restart"):
    restart()

# ---------------------------
# Flow
# ---------------------------
# Q0 — ALS Note Taking (asked first)
if not st.session_state.finished and st.session_state.step == "Q0":
    q = "Do you have an ALS-approved accommodation for note-taking?"
    ans = st.radio(q, ["Yes", "No"], key="Q0")
    if st.button("Next ➜", key="next_Q0"):
        st.session_state.answers["Q0"] = ans
        if ans == "Yes":
            add_score("Note Taking Services", w=2)
        go("Q1")

# Q1 — Academic vs Learning Skills
elif not st.session_state.finished and st.session_state.step == "Q1":
    q = "What type of support do you need?"
    ans = st.radio(q, ["Academic/content-specific help", "Learning skills / study strategies"], key="Q1")
    if st.button("Next ➜", key="next_Q1"):
        st.session_state.answers["Q1"] = ans
        if ans.startswith("Academic"):
            go("Q1_pref")
        else:
            add_score("Learning Skills Workshops", "Learning Support Drop-In", w=1)
            go("Q3")

# Q1_pref — Preference (Academic path)
elif not st.session_state.finished and st.session_state.step == "Q1_pref":
    q = "When receiving academic help, do you prefer one-on-one or group sessions?"
    ans = st.radio(q, ["One-on-one", "Group"], key="Q1_pref")
    if st.button("Next ➜", key="next_Q1_pref"):
        st.session_state.answers["Q1_pref"] = ans
        if ans == "One-on-one":
            add_score("Peer Tutoring", w=1)
            go("Q2A")
        else:
            add_score("PASS", w=1)
            go("Q2B")

# Q2A — Subject struggle (Alone/1:1)
elif not st.session_state.finished and st.session_state.step == "Q2A":
    q = "Do you struggle with specific subjects like Math, Science, or Writing?"
    ans = st.radio(q, ["Yes", "No"], key="Q2A")
    if st.button("Next ➜", key="next_Q2A"):
        st.session_state.answers["Q2A"] = ans
        if ans == "Yes":
            add_score("Peer Tutoring", "Math & Writing Centre", w=2)
            go("Q3A")
        else:
            go("Q4A")

# Q3A — 1:1 vs Drop-in (Alone/subject)
elif not st.session_state.finished and st.session_state.step == "Q3A":
    q = "Would you prefer scheduled one-on-one sessions or drop-in advice?"
    ans = st.radio(q, ["Scheduled one-on-one", "Drop-in"], key="Q3A")
    if st.button("Next ➜", key="next_Q3A"):
        st.session_state.answers["Q3A"] = ans
        if ans.startswith("Scheduled"):
            go("Q3A_follow")
        else:
            add_score("Learning Support Drop-In", w=2)
            go("Q4A")

# Q3A_follow — STEM last-resort escalation
elif not st.session_state.finished and st.session_state.step == "Q3A_follow":
    q = "Do you need specialized STEM support beyond what Math/Writing tutors can provide?"
    ans = st.radio(q, ["Yes", "No"], key="Q3A_follow")
    if st.button("Next ➜", key="next_Q3A_follow"):
        st.session_state.answers["Q3A_follow"] = ans
        if ans == "Yes":
            add_score("STEM Specialist", w=2)
        go("Q4A")

# Q4A — Interest in skills support
elif not st.session_state.finished and st.session_state.step == "Q4A":
    q = "Would you also like support for study skills (time mgmt, memory, presentations, test prep)?"
    ans = st.radio(q, ["Yes", "No"], key="Q4A")
    if st.button("Next ➜", key="next_Q4A"):
        st.session_state.answers["Q4A"] = ans
        if ans == "Yes":
            go("Q3")
        else:
            finish()

# Q2B — Group academic branch → PASS?
elif not st.session_state.finished and st.session_state.step == "Q2B":
    q = "Would you like structured, peer-led study sessions for your course (PASS)?"
    ans = st.radio(q, ["Yes", "No"], key="Q2B")
    if st.button("Next ➜", key="next_Q2B"):
        st.session_state.answers["Q2B"] = ans
        if ans == "Yes":
            add_score("PASS", w=3)
            go("Q3B_follow")
        else:
            go("Q3B")

# Q3B — Group but not PASS → group work skills?
elif not st.session_state.finished and st.session_state.step == "Q3B":
    q = "Would you like help with group projects, communication, or presentations?"
    ans = st.radio(q, ["Yes", "No"], key="Q3B")
    if st.button("Next ➜", key="next_Q3B"):
        st.session_state.answers["Q3B"] = ans
        if ans == "Yes":
            add_score("Learning Skills Workshops", w=2)
        else:
            add_score("Peer Tutoring", w=2)
        finish()

# Q3B_follow — after PASS, optional skills add-on
elif not st.session_state.finished and st.session_state.step == "Q3B_follow":
    q = "Would you also like skills support for presentations, test prep, or time management?"
    ans = st.radio(q, ["Yes", "No"], key="Q3B_follow")
    if st.button("Next ➜", key="next_Q3B_follow"):
        st.session_state.answers["Q3B_follow"] = ans
        if ans == "Yes":
            add_score("Learning Skills Workshops", w=1)
        finish()

# Q3 — Skills path (direct)
elif not st.session_state.finished and st.session_state.step == "Q3":
    q = "Which skills do you want to improve?"
    ans = st.radio(
        q,
        [
            "Time management, stress, memory, or presentations",
            "General strategies or digital learning tips",
        ],
        key="Q3",
    )
    if st.button("Next ➜", key="next_Q3"):
        st.session_state.answers["Q3"] = ans
        if ans.startswith("Time"):
            add_score("Learning Skills Workshops", w=3)
        else:
            add_score("Learning Support Drop-In", w=3)
        finish()

# ---------------------------
# Results
# ---------------------------
if st.session_state.finished:
    st.subheader("🎯 Your top matches")

    raw_counts = Counter(st.session_state.scores)
    counts = ensure_top3(raw_counts, st.session_state.answers)
    top3 = counts.most_common(3)

    # 🎉 Confetti + 🎈 Balloons
    components.html(
        """
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
        function fire() {
          confetti({particleCount: 120, spread: 70, origin: { y: 0.6 }});
          setTimeout(() => confetti({particleCount: 80, spread: 100, startVelocity: 50, origin: { y: 0.7 }}), 350);
          setTimeout(() => confetti({particleCount: 60, spread: 120, startVelocity: 60, origin: { y: 0.8 }}), 700);
        }
        fire();
        </script>
        """,
        height=0, width=0
    )
    st.balloons()

    for rank, (svc, score) in enumerate(top3, start=1):
        with st.container(border=True):
            st.markdown(f"**{rank}. {svc}**  \n*Score:* {score}")
            if svc in SERVICE_DESCRIPTIONS:
                st.caption(SERVICE_DESCRIPTIONS[svc])

    st.markdown("---")
    st.markdown(
        f"🔗 **Explore all services or book now:** [Humber Student Learning Services]({HUMBER_SLS_URL})"
    )
