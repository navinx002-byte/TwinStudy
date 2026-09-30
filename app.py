import streamlit as st
import pandas as pd
import numpy as np
from simulation_engine import DigitalTwinEngine

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="HumanTwin AI | MyStudyLife + Scout (Enhanced)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN STYLING (HTML + CSS) ---
st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    
    /* Top Header */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 22px 28px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.0rem;
    }
    .differentiator-pill {
        display: inline-block;
        background: rgba(168, 85, 247, 0.18);
        border: 1px solid rgba(168, 85, 247, 0.4);
        color: #d8b4fe;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-left: 8px;
    }

    /* Timetable Cards */
    .class-card {
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(17, 24, 39, 0.7);
        transition: transform 0.15s ease;
    }
    .class-card:hover { transform: translateY(-2px); }
    .class-time { font-size: 0.8rem; color: #94a3b8; font-weight: 600; }
    .class-name { font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin: 4px 0; }
    .class-meta { font-size: 0.85rem; color: #cbd5e1; }

    /* Timeline Cards */
    .timeline-card {
        background: rgba(17, 24, 39, 0.88);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 16px;
        border-left: 5px solid #3b82f6;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }
    .card-a { border-left-color: #ef4444; }
    .card-b { border-left-color: #3b82f6; }
    .card-c { border-left-color: #10b981; background: rgba(16, 185, 129, 0.05); }

    .card-badge {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 14px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .badge-a { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-b { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-c { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }

    .card-title { font-size: 1.15rem; font-weight: 700; color: #f1f5f9; margin-bottom: 8px; }
    .card-desc { font-size: 0.9rem; color: #cbd5e1; line-height: 1.45; margin-bottom: 14px; }
    
    .sacrifice-banner {
        background: linear-gradient(90deg, rgba(30, 58, 138, 0.45) 0%, rgba(88, 28, 135, 0.45) 100%);
        border: 1px solid rgba(96, 165, 250, 0.3);
        border-radius: 12px;
        padding: 14px 18px;
        margin: 14px 0;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE STATE ---
if "twin" not in st.session_state:
    st.session_state.twin = DigitalTwinEngine()
if "last_simulation" not in st.session_state:
    st.session_state.last_simulation = None
if "adaptation_alert" not in st.session_state:
    st.session_state.adaptation_alert = None

twin = st.session_state.twin

# --- SIDEBAR: TWIN BRAIN & SOVEREIGN PRIVACY VAULT ---
with st.sidebar:
    st.markdown("### 🎓 MyStudyLife Profile")
    st.markdown(f"**Student:** {twin.default_profile['name']}")
    st.caption(f"{twin.default_profile['role']}")
    
    st.markdown("---")
    st.markdown("#### 🧠 Cognitive Behavioral DNA")
    st.caption("✨ *Extra Feature: Missing in standard MyStudyLife*")
    
    high_stakes = st.slider(
        "Exam vs. Homework Priority", 
        0.0, 1.0, 
        float(twin.default_profile["high_stakes_bias"]),
        help="Higher values mean the Twin will sacrifice routine homework to ace high-stakes exams."
    )
    twin.default_profile["high_stakes_bias"] = high_stakes
    
    risk_tol = st.slider(
        "Deadline Risk Tolerance", 
        0.0, 1.0, 
        float(twin.default_profile["risk_tolerance"]),
        help="Tolerance for cutting assignments close to late-penalty boundaries."
    )
    twin.default_profile["risk_tolerance"] = risk_tol
    
    st.progress(twin.default_profile["night_owl_factor"], text="Night-Owl Efficiency: 85%")
    
    st.markdown("---")
    st.markdown("#### 🛡️ Sovereign Privacy Vault")
    st.caption("✨ *Extra Feature: Complete user control over AI access*")
    
    allow_acad = st.toggle("Academic Calendar & Timetable", value=twin.privacy_permissions["academic_calendar"])
    allow_sleep = st.toggle("Sleep & Biometrics", value=twin.privacy_permissions["sleep_biometrics"])
    allow_social = st.toggle("Personal Chats & Social", value=twin.privacy_permissions["social_activity"])
    
    twin.privacy_permissions["academic_calendar"] = allow_acad
    twin.privacy_permissions["sleep_biometrics"] = allow_sleep
    twin.privacy_permissions["social_activity"] = allow_social
    twin.save_state()
    
    if not allow_sleep:
        st.warning("⚠️ Biometrics Muted: Using fallback baseline model.")

    st.markdown("---")
    if st.button("🔄 Forget & Reset Memory", use_container_width=True):
        msg = twin.reset_twin_memory()
        st.session_state.adaptation_alert = msg
        st.rerun()

# --- TOP HERO BANNER ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">MyStudyLife + Scout <span class="differentiator-pill">ENHANCED WITH DIGITAL TWIN</span></div>
    <div class="hero-subtitle">All the class schedules and Scout AI study coaching of MyStudyLife—supercharged with <strong>What-If Multi-Branch Simulations, Pandas Fatigue Curves, and Adaptive Learning</strong>.</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.adaptation_alert:
    st.info(st.session_state.adaptation_alert, icon="🧠")

# --- MAIN TABS ---
tab_life, tab_scout, tab_sim, tab_analytics, tab_shock = st.tabs([
    "📅 MyStudyLife Timetable & Tasks",
    "🤖 Scout AI Study Coach",
    "🔮 [NEW] 'What-If' Decision Simulator",
    "📊 [NEW] Biological Battery & Fatigue",
    "⚡ [NEW] Emergency Shock-Absorber"
])

# ==============================================================================
# TAB 1: MYSTUDYLIFE TIMETABLE & TASKS (CORE BASELINE)
# ==============================================================================
with tab_life:
    st.markdown("### 📅 Weekly Class Timetable & Schedule")
    
    # Class schedule display by day
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    col_days = st.columns(5)
    
    for i, d in enumerate(days):
        with col_days[i]:
            st.markdown(f"**{d}**")
            day_classes = twin.classes_schedule[twin.classes_schedule["Day"] == d]
            if len(day_classes) == 0:
                st.caption("No classes scheduled")
            else:
                for _, c in day_classes.iterrows():
                    st.markdown(f"""
                    <div class="class-card" style="border-left: 4px solid {c['Color']};">
                        <div class="class-time">⏰ {c['Time']}</div>
                        <div class="class-name">{c['Course'].split('-')[1]}</div>
                        <div class="class-meta">📍 {c['Room']} | 👨‍🏫 {c['Instructor']}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📝 MyStudyLife Task & Assignment Tracker")
    
    # Render interactive task checklist
    for _, t in twin.tasks.iterrows():
        c1, c2, c3, c4 = st.columns([0.5, 3, 1.5, 2])
        with c1:
            checked = st.checkbox("", value=bool(t["completed"]), key=f"chk_{t['id']}")
            if checked != t["completed"]:
                twin.toggle_task_completion(t["id"], checked)
                st.rerun()
        with c2:
            st.markdown(f"**{t['title']}** ({t['course']})")
        with c3:
            st.caption(f"⏳ Due in {t['due_in_hours']}h | Weight: {t['weight_percent']}%")
        with c4:
            st.progress(t["current_readiness"] / 100, text=f"Readiness: {t['current_readiness']}%")

    with st.expander("➕ Add New Class / Assignment"):
        with st.form("new_task_form"):
            c_name = st.selectbox("Course", ["CS 301 - Algorithms", "CS 340 - Database Systems", "CS 370 - Computer Networks"])
            t_title = st.text_input("Title", "Final Project Phase 1")
            t_type = st.selectbox("Type", ["Assignment", "Exam", "Quiz"])
            t_due = st.number_input("Due in (hours)", 12, 300, 48)
            t_weight = st.number_input("Weight (%)", 5, 50, 15)
            t_prep = st.number_input("Hours Needed", 2, 40, 8)
            if st.form_submit_button("Add Task to MyStudyLife"):
                twin.add_new_task(c_name, t_title, t_type, t_due, t_weight, t_prep)
                st.success("Task added to your schedule!")
                st.rerun()


# ==============================================================================
# TAB 2: SCOUT AI ASSISTANT (CONVERSATIONAL COACH)
# ==============================================================================
with tab_scout:
    st.markdown("### 🤖 Scout: The MyStudyLife AI Study Coach")
    st.caption("Chat with Scout in plain English to get revision breakdowns, schedule reminders, and class details.")
    
    # Chat display container
    for m in twin.scout_messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            
    # Chat input
    user_chat = st.chat_input("Ask Scout: 'When is my next class?' or 'What is due this week?'")
    if user_chat:
        with st.chat_message("user"):
            st.markdown(user_chat)
        with st.chat_message("assistant"):
            reply = twin.ask_scout(user_chat)
            st.markdown(reply)
            st.rerun()


# ==============================================================================
# TAB 3: [NEW] "WHAT-IF" SIMULATOR (THE EXTRA WINNING FEATURE)
# ==============================================================================
with tab_sim:
    st.markdown("### 🔮 Decision Flight Simulator (Not in MyStudyLife)")
    st.info("💡 **Why this beats standard Scout:** Scout can only plan tasks linearly. Our Digital Twin forks reality into **Timeline A vs Timeline B** to show trade-offs *before* you make a risky decision.")

    default_q = "What will happen if I spend the next two days preparing for my exam instead of working on my assignment?"
    c_q, c_b = st.columns([4, 1])
    with c_q:
        q_input = st.text_input("Decision Dilemma:", value=default_q)
    with c_b:
        st.write("")
        st.write("")
        trigger = st.button("🚀 Simulate Futures", type="primary", use_container_width=True)

    if trigger or st.session_state.last_simulation is None:
        st.session_state.last_simulation = twin.simulate_what_if(q_input)

    sim = st.session_state.last_simulation
    t_data = sim["timelines"]

    st.markdown(f"""
    <div class="sacrifice-banner">
        <strong>🏆 Digital Twin Recommendation: <span style="color:#60a5fa;">{sim['recommended_choice']}</span></strong><br/>
        <span style="font-size:0.92rem; color:#cbd5e1;">{sim['recommendation_rationale']}</span>
    </div>
    """, unsafe_allow_html=True)

    colA, colB, colC = st.columns(3)

    with colA:
        st.markdown(f"""
        <div class="timeline-card card-a">
            <span class="card-badge badge-a">Timeline A</span>
            <div class="card-title">100% Exam Cramming</div>
            <div class="card-desc">{t_data['A']['action']}</div>
        </div>
        """, unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1: st.metric("Exam Readiness", t_data['A']['exam_score_projected'], delta="+38% Gain")
        with m2: st.metric("Assignment Score", t_data['A']['assignment_score_projected'], delta="-20% Late", delta_color="inverse")
        st.metric("Burnout Danger", t_data['A']['burnout_risk'], delta="Severe Sleep Debt", delta_color="inverse")
        if st.button("Override: Choose Timeline A", key="btn_a_new", use_container_width=True):
            alert = twin.record_feedback("A", "User prioritizes Exam over Assignment penalty.")
            st.session_state.adaptation_alert = alert
            st.rerun()

    with colB:
        st.markdown(f"""
        <div class="timeline-card card-b">
            <span class="card-badge badge-b">Timeline B</span>
            <div class="card-title">Submit Assignment First</div>
            <div class="card-desc">{t_data['B']['action']}</div>
        </div>
        """, unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1: st.metric("Exam Readiness", t_data['B']['exam_score_projected'], delta="-18% Risk", delta_color="inverse")
        with m2: st.metric("Assignment Score", t_data['B']['assignment_score_projected'], delta="Full Marks")
        st.metric("Burnout Danger", t_data['B']['burnout_risk'], delta="Normal Rest")
        if st.button("Override: Choose Timeline B", key="btn_b_new", use_container_width=True):
            alert = twin.record_feedback("B", "User prioritized assignment certainty.")
            st.session_state.adaptation_alert = alert
            st.rerun()

    with colC:
        st.markdown(f"""
        <div class="timeline-card card-c">
            <span class="card-badge badge-c">Timeline C (Recommended)</span>
            <div class="card-title">Dynamic Hybrid Strategy</div>
            <div class="card-desc">{t_data['C']['action']}</div>
        </div>
        """, unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1: st.metric("Exam Readiness", t_data['C']['exam_score_projected'], delta="+28% Strong")
        with m2: st.metric("Assignment Score", t_data['C']['assignment_score_projected'], delta="No Penalty")
        st.metric("Burnout Danger", t_data['C']['burnout_risk'], delta="Sustainable")
        if st.button("Accept Recommended Strategy", key="btn_c_new", type="primary", use_container_width=True):
            alert = twin.record_feedback("C", "User accepted Twin's balanced recommendation.")
            st.session_state.adaptation_alert = alert
            st.rerun()

    st.markdown("---")
    st.markdown(f"📊 **The Sacrifice Index (Pandas Net Math):** {sim['sacrifice_index']['description']}")


# ==============================================================================
# TAB 4: [NEW] BIOLOGICAL BATTERY & FATIGUE (STREAMLIT CHARTS + PANDAS)
# ==============================================================================
with tab_analytics:
    st.markdown("### 📊 Biological Energy & Fatigue Modeling (Streamlit Charts + Pandas)")
    st.caption("✨ *Extra Feature: MyStudyLife assumes 1 hour at 2 AM is the same as 10 AM. Our Twin models biological focus decay!*")

    df_a = twin.generate_fatigue_curve("timeline_a", hours=48)
    df_b = twin.generate_fatigue_curve("timeline_b", hours=48)
    df_c = twin.generate_fatigue_curve("timeline_c", hours=48)

    chart_df = pd.DataFrame({
        "Hour": df_a["Hour"],
        "Timeline A (All-Nighter Cramming)": df_a["Cognitive_Focus"],
        "Timeline B (Healthy Sleep)": df_b["Cognitive_Focus"],
        "Timeline C (Hybrid)": df_c["Cognitive_Focus"],
        "Critical Brain Fog Threshold": [40.0] * len(df_a)
    }).set_index("Hour")

    st.line_chart(chart_df, color=["#ef4444", "#3b82f6", "#10b981", "#fbbf24"])
    st.caption("🔴 Red = Cramming Focus Crash | 🔵 Blue = Stable Baseline | 🟢 Green = Balanced Plan | 🟡 Amber = Critical Fog Threshold")

    st.markdown("---")
    st.markdown("#### 📈 Multi-Scenario Risk Comparison")
    risk_summary = pd.DataFrame({
        "Scenario": ["Timeline A (Cram)", "Timeline B (Assignment)", "Timeline C (Hybrid)"],
        "Burnout Risk (%)": [78, 42, 52],
        "Late Penalty Risk (%)": [75, 0, 10],
        "Projected Exam Readiness (%)": [96, 78, 88]
    }).set_index("Scenario")
    st.bar_chart(risk_summary)


# ==============================================================================
# TAB 5: [NEW] EMERGENCY SHOCK ABSORBER (EDGE CASES)
# ==============================================================================
with tab_shock:
    st.markdown("### ⚡ Emergency Shock Absorber: Mid-Process Course Correction")
    st.caption("✨ *Extra Feature: When unexpected surprises happen, standard apps break. The Digital Twin recalibrates instantly.*")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("#### 🎁 Surprise: Assignment Extension")
        st.caption("Professor announces that Assignment #2 is extended by 48 hours.")
        if st.button("Trigger: +48h Deadline Extension", use_container_width=True):
            res = twin.handle_emergency_extension(48)
            st.success(res)
            st.session_state.last_simulation = twin.simulate_what_if("Recalculate with extended deadline")
            st.rerun()

    with col_s2:
        st.markdown("#### 🤒 Surprise: Sudden Illness / Energy Slump")
        st.caption("Student wakes up sick. Brain energy capacity drops by 40%.")
        if st.button("Trigger: Sudden Sickness Shock", use_container_width=True):
            twin.default_profile["fatigue_sensitivity"] = min(0.95, twin.default_profile["fatigue_sensitivity"] + 0.20)
            st.warning("Twin Alert: Fatigue sensitivity increased. Re-optimizing schedules for mandatory rest.")
            st.session_state.last_simulation = twin.simulate_what_if("Recalculate with sickness rest")
            st.rerun()
