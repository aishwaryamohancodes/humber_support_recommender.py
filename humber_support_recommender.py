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
                     "Learning Support Drop-In", "Math & Wr
