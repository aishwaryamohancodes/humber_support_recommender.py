import streamlit as st
from collections import Counter, defaultdict

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

st.title("🎓 Humber Learning Services Recommender")
st.caption("Answer a few quick questions to get personalized support recommendations.")

if st.button("🔄 Restart"):
    restart()

def go(next_step):
    st.session_state.step = next_step

def finish():
    st.session_state.finished = True

# Q0 ALS Note Taking
if not st.session_state.finished and st.session_state.step == "Q0":
    ans = st.radio("Do you have an ALS-approved accommodation for note-taking?", ["Yes", "No"], key="Q0")
    if st.button("Next ➜", key="next_Q0"):
        st.session_state.answers["Q0"] = ans
        if ans == "Yes":
            add_score("Note Taking Services", w=2)
        go("Q1")

elif not st.session_state.finished and st.session_state.step == "Q1":
    ans = st.radio("What type of support do you need?", ["Academic/content-specific help", "Learning skills / study strategies"], key="Q1")
    if st.button("Next ➜", key="next_Q1"):
        st.session_state.answers["Q1"] = ans
        if ans.startswith("Academic"):
            go("Q1_pref")
        else:
            go("Q3")

elif not st.session_state.finished and st.session_state.step == "Q1_pref":
    ans = st.radio("When receiving academic help, do you prefer one-on-one or group sessions?", ["One-on-one", "Group"], key="Q1_pref")
    if st.button("Next ➜", key="next_Q1_pref"):
        st.session_state.answers["Q1_pref"] = ans
        if ans == "One-on-one":
            go("Q2A")
        else:
            go("Q2B")

elif not st.session_state.finished and st.session_state.step == "Q2A":
    ans = st.radio("Do you struggle with specific subjects like Math, Science, or Writing?", ["Yes", "No"], key="Q2A")
    if st.button("Next ➜", key="next_Q2A"):
        st.session_state.answers["Q2A"] = ans
        if ans == "Yes":
            add_score("Peer Tutoring", "Math & Writing Centre")
            go("Q3A")
        else:
            go("Q4A")

elif not st.session_state.finished and st.session_state.step == "Q3A":
    ans = st.radio("Would you prefer scheduled one-on-one sessions or drop-in advice?", ["Scheduled one-on-one", "Drop-in"], key="Q3A")
    if st.button("Next ➜", key="next_Q3A"):
        st.session_state.answers["Q3A"] = ans
        if ans.startswith("Scheduled"):
            go("Q3A_follow")
        else:
            add_score("Learning Support Drop-In")
            go("Q4A")

elif not st.session_state.finished and st.session_state.step == "Q3A_follow":
    ans = st.radio("Do you need specialized STEM support beyond Math/Writing tutors?", ["Yes", "No"], key="Q3A_follow")
    if st.button("Next ➜", key="next_Q3A_follow"):
        st.session_state.answers["Q3A_follow"] = ans
        if ans == "Yes":
            add_score("STEM Specialist")
        go("Q4A")

elif not st.session_state.finished and st.session_state.step == "Q4A":
    ans = st.radio("Would you also like support for study skills (time mgmt, memory, presentations, test prep)?", ["Yes", "No"], key="Q4A")
    if st.button("Next ➜", key="next_Q4A"):
        st.session_state.answers["Q4A"] = ans
        if ans == "Yes":
            go("Q3")
        else:
            finish()

elif not st.session_state.finished and st.session_state.step == "Q2B":
    ans = st.radio("Would you like structured, peer-led study sessions for your course (PASS)?", ["Yes", "No"], key="Q2B")
    if st.button("Next ➜", key="next_Q2B"):
        st.session_state.answers["Q2B"] = ans
        if ans == "Yes":
            add_score("PASS", w=2)
            go("Q3B_follow")
        else:
            go("Q3B")

elif not st.session_state.finished and st.session_state.step == "Q3B":
    ans = st.radio("Would you like help with group projects, communication, or presentations?", ["Yes", "No"], key="Q3B")
    if st.button("Next ➜", key="next_Q3B"):
        st.session_state.answers["Q3B"] = ans
        if ans == "Yes":
            add_score("Learning Skills Workshops")
        else:
            add_score("Peer Tutoring")
        finish()

elif not st.session_state.finished and st.session_state.step == "Q3B_follow":
    ans = st.radio("Would you also like skills support for presentations, test prep, or time management?", ["Yes", "No"], key="Q3B_follow")
    if st.button("Next ➜", key="next_Q3B_follow"):
        st.session_state.answers["Q3B_follow"] = ans
        if ans == "Yes":
            add_score("Learning Skills Workshops")
        finish()

elif not st.session_state.finished and st.session_state.step == "Q3":
    ans = st.radio("Which skills do you want to improve?", ["Time mgmt, stress, memory, presentations", "General strategies or digital learning tips"], key="Q3")
    if st.button("Next ➜", key="next_Q3"):
        st.session_state.answers["Q3"] = ans
        if ans.startswith("Time"):
            add_score("Learning Skills Workshops", w=2)
        else:
            add_score("Learning Support Drop-In", w=2)
        finish()

if st.session_state.finished:
    st.subheader("🎯 Your top matches")
    from collections import Counter
    counts = Counter(st.session_state.scores)
    if len(counts) == 0:
        st.info("No strong matches based on your answers. Explore all services below.")
    else:
        for rank, (svc, score) in enumerate(counts.most_common(3), start=1):
            st.markdown(f"**{rank}. {svc}** (score: {score})")
            if svc in SERVICE_DESCRIPTIONS:
                st.caption(SERVICE_DESCRIPTIONS[svc])
    st.markdown("---")
    st.markdown(f"🔗 **Explore other services here:** [Humber Student Learning Services]({HUMBER_SLS_URL})")
