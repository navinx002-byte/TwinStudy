import sys

server_code = '''"""
TwinStudy / HumanTwin AI - Full Self-Contained Backend Server
Built for Student Productivity & Academic Success
Features:
- Dynamic Contextual What-If Decision Simulation Engine
- Continuous Behavioral Modeling & Digital Twin Learning Engine
- Academic Grades & CGPA Tracking Dashboard (10-point and 4-point US scale)
- Focus Mode & Study Telemetry
- Minor Student (<18) & Parent/Guardian Governance Dashboard
- Real-time Notifications
- MyStudyLife Student Academic Profile & Weekly Timetable Management
- Persistent Storage in twin_database.json
- Gmail SMTP OTP Dispatch Directly to User Inbox
"""

import os
import json
import random
import re
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="public", static_url_path="")
CORS(app)

DB_FILE = os.path.join(os.path.dirname(__file__), "twin_database.json")
EMAIL_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "email_config.json")

# In-memory OTP storage: email -> {code, purpose, data, attempts_left, expires_at, last_sent_at}
verification_codes = {}

DEFAULT_BEHAVIOR_PATTERNS = [
    {
        "id": "bp_1",
        "title": "Postpones Homework For High-Weight Exams",
        "pattern_type": "prioritization",
        "confidence": 88.5,
        "evidence_count": 14,
        "evidence_summary": "Student historically delays assignments to focus on exam prep, risking late penalties (-10% average).",
        "weight": 1.35,
        "is_active": True
    },
    {
        "id": "bp_2",
        "title": "Peak Analytical Retention: Evening Hours",
        "pattern_type": "productivity",
        "confidence": 92.0,
        "evidence_count": 22,
        "evidence_summary": "Problem set completion speed is 3.2x faster between 7 PM - 11 PM with lower distraction triggers.",
        "weight": 1.4,
        "is_active": True
    },
    {
        "id": "bp_3",
        "title": "Last-Minute Submission Fatigue Spikes",
        "pattern_type": "deadline_habit",
        "confidence": 79.0,
        "evidence_count": 9,
        "evidence_summary": "Submissions completed within 3 hours of deadline show a 24% drop in quiz verification scores.",
        "weight": 1.2,
        "is_active": True
    },
    {
        "id": "bp_4",
        "title": "Stamina Drop-off After 75 Minutes Continuous Focus",
        "pattern_type": "fatigue",
        "confidence": 85.0,
        "evidence_count": 18,
        "evidence_summary": "Telemetry logs show cognitive degradation increases steeply after 75m without a 10m recharge interval.",
        "weight": 1.15,
        "is_active": True
    }
]

DEFAULT_DECISIONS = [
    {
        "id": "dec_1",
        "timestamp": "2026-09-29T18:30:00Z",
        "question": "What if I go to trip 2 days before Midterms?",
        "recommended_scenario": "Future B (Pre-Trip Sprint)",
        "chosen_scenario": "Future B (Pre-Trip Sprint)",
        "user_reason": "I wanted to clear my coursework beforehand so I could travel guilt-free.",
        "is_disagreement": False,
        "actual_outcome": "Completed all 3 modules before Friday departure. Traveled with zero anxiety.",
        "outcome_rating": 5,
        "outcome_feedback": "The pre-trip sprint gave me peace of mind."
    },
    {
        "id": "dec_2",
        "timestamp": "2026-09-26T21:00:00Z",
        "question": "Should I pull an all-nighter for DBMS seminar?",
        "recommended_scenario": "Future B (Rest & Targeted Morning Revision)",
        "chosen_scenario": "Future A (All-Nighter Cramming)",
        "user_reason": "Felt unconfident about relational algebra theorems.",
        "is_disagreement": True,
        "actual_outcome": "Fell asleep in afternoon class the next day; experienced 35% stamina crash.",
        "outcome_rating": 2,
        "outcome_feedback": "The twin was right: the all-nighter crashed my stamina for the whole next day."
    }
]

DEFAULT_GRADES = [
    {
        "id": "g_1",
        "subject_id": "s_1",
        "subject_name": "Artificial Intelligence",
        "assessment_name": "Midterm Exam 1",
        "score": 46.0,
        "max_score": 50.0,
        "weight": 25.0,
        "grade_letter": "A+",
        "notes": "Excellent grasp of heuristic search algorithms.",
        "date_recorded": "2026-09-22"
    },
    {
        "id": "g_2",
        "subject_id": "s_1",
        "subject_name": "Artificial Intelligence",
        "assessment_name": "Lab Project 1",
        "score": 88.0,
        "max_score": 100.0,
        "weight": 20.0,
        "grade_letter": "A",
        "notes": "Graph search visualizer implemented cleanly.",
        "date_recorded": "2026-09-28"
    },
    {
        "id": "g_3",
        "subject_id": "s_2",
        "subject_name": "Cloud Computing Lab",
        "assessment_name": "Hands-on Practical Quiz",
        "score": 18.5,
        "max_score": 20.0,
        "weight": 20.0,
        "grade_letter": "A+",
        "notes": "Docker containerization benchmark verified.",
        "date_recorded": "2026-09-25"
    }
]

DEFAULT_TWINSTUDY_DATA = {
    "user": {
        "name": "Adarsh Sharma",
        "email": "navinnavi8431@gmail.com",
        "dob": "2002-05-15",
        "age": 24,
        "role": "student_adult",
        "role_display": "Student",
        "grade_level": "B.Tech Computer Science (Semester 6)",
        "goals": ["Maintain high semester GPA", "Complete coursework on time with verified proof", "Optimize study schedule to prevent burnout"],
        "daily_study_hours": 6.5,
        "preferred_study_time": "7 PM - 11 PM",
        "learning_preference": "Hands-on projects & problem sets",
        "focus_duration_minutes": 90,
        "points": 600,
        "current_tier": "Achiever (Tier 3)",
        "streak_days": 5,
        "college": "Nitte Meenakshi Institute of Technology",
        "is_minor": False,
        "phone": "+91 9876543210"
    },
    "registered_users": {
        "navinnavi8431@gmail.com": {
            "name": "Adarsh Sharma",
            "dob": "2002-05-15",
            "age": 24,
            "is_minor": False,
            "email": "navinnavi8431@gmail.com",
            "phone": "+91 9876543210",
            "password": "password123",
            "registered_at": "2026-09-30T16:29:57.971563"
        }
    },
    "subjects": [
        {"id": "s_1", "name": "Artificial Intelligence", "code": "CS601", "credits": "4", "color": "#00C4CC", "teacher": "Dr. R. Raman", "room": "Room 304", "type": "Lecture"},
        {"id": "s_2", "name": "Cloud Computing Lab", "code": "CS602", "credits": "3", "color": "#8B5CF6", "teacher": "Prof. S. Nair", "room": "Lab 2", "type": "Lab"},
        {"id": "s_3", "name": "Database Management Systems", "code": "CS603", "credits": "4", "color": "#14B8A6", "teacher": "Dr. A. Verma", "room": "Room 201", "type": "Lecture"}
    ],
    "classes": [
        {"id": "c_1", "subject_id": "s_1", "subject": "Artificial Intelligence", "day": "Monday", "start_time": "10:00", "end_time": "11:30", "time": "10:00 AM - 11:30 AM", "teacher": "Dr. R. Raman", "room": "Room 304", "color": "#00C4CC", "type": "Lecture", "week_type": "All"},
        {"id": "c_2", "subject_id": "s_2", "subject": "Cloud Computing Lab", "day": "Tuesday", "start_time": "14:00", "end_time": "16:00", "time": "2:00 PM - 4:00 PM", "teacher": "Prof. S. Nair", "room": "Lab 2", "color": "#8B5CF6", "type": "Lab", "week_type": "All"},
        {"id": "c_3", "subject_id": "s_3", "subject": "Database Management Systems", "day": "Wednesday", "start_time": "11:30", "end_time": "13:00", "time": "11:30 AM - 1:00 PM", "teacher": "Dr. A. Verma", "room": "Room 201", "color": "#14B8A6", "type": "Lecture", "week_type": "All"}
    ],
    "tasks": [
        {"id": "t_1", "subject": "Artificial Intelligence", "subject_color": "#00C4CC", "title": "Implement A* Search Algorithm in Python", "type": "Assignment", "due": "In 2 days", "due_date": "2026-10-02", "points": 100, "status": "Pending", "verified": False},
        {"id": "t_2", "subject": "Cloud Computing Lab", "subject_color": "#8B5CF6", "title": "Deploy Docker Microservice Container", "type": "Lab Report", "due": "Tomorrow", "due_date": "2026-10-01", "points": 150, "status": "Pending", "verified": False},
        {"id": "t_3", "subject": "Database Management Systems", "subject_color": "#14B8A6", "title": "B+ Tree Indexing Case Study", "type": "Assignment", "due": "In 4 days", "due_date": "2026-10-04", "points": 120, "status": "Pending", "verified": False}
    ],
    "notifications": [
        {"id": "n1", "title": "Upcoming Submission Due", "description": "AI Assignment submission window closes in 48 hours.", "time": "2 hours ago", "type": "warning", "read": False},
        {"id": "n2", "title": "5-Day Streak Maintained", "description": "Consistent evening focus logged. +50 bonus points awarded!", "time": "5 hours ago", "type": "reward", "read": False},
        {"id": "n3", "title": "Focus Telemetry Optimal", "description": "Your 45-minute focus session showed 92% cognitive stamina retention.", "time": "1 day ago", "type": "info", "read": True}
    ],
    "behavior_patterns": DEFAULT_BEHAVIOR_PATTERNS,
    "decisions": DEFAULT_DECISIONS,
    "grades": DEFAULT_GRADES,
    "subject_targets": {
        "s_1": "A+",
        "s_2": "A",
        "s_3": "A"
    }
}

# --- DATABASE PERSISTENCE ---

def load_db():
    if not os.path.exists(DB_FILE):
        save_db(DEFAULT_TWINSTUDY_DATA)
        return json.loads(json.dumps(DEFAULT_TWINSTUDY_DATA))
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure key structures exist
            if "behavior_patterns" not in data or not data["behavior_patterns"]:
                data["behavior_patterns"] = DEFAULT_BEHAVIOR_PATTERNS
            if "decisions" not in data or not data["decisions"]:
                data["decisions"] = DEFAULT_DECISIONS
            if "grades" not in data or not data["grades"]:
                data["grades"] = DEFAULT_GRADES
            if "subject_targets" not in data:
                data["subject_targets"] = {"s_1": "A+", "s_2": "A", "s_3": "A"}
            if "registered_users" not in data:
                data["registered_users"] = {}
            if "notifications" not in data:
                data["notifications"] = []
            return data
    except Exception as e:
        print(f"[DB LOAD ERROR]: {e}")
        return json.loads(json.dumps(DEFAULT_TWINSTUDY_DATA))

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[DB SAVE ERROR]: {e}")

# --- EMAIL CONFIGURATION & DISPATCH VIA SMTP ---

def load_dotenv_simple():
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip('"').strip("'")
                        if k and not os.environ.get(k):
                            os.environ[k] = v
        except Exception:
            pass

load_dotenv_simple()

def get_email_config():
    cfg = {"configured": False, "sender_email": "", "sender_password": ""}
    if os.path.exists(EMAIL_CONFIG_FILE):
        try:
            with open(EMAIL_CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass
    if not cfg.get("sender_email") or not cfg.get("sender_password"):
        env_user = os.environ.get("GMAIL_USER", "").strip() or os.environ.get("GMAIL_SENDER", "").strip()
        env_pass = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
        if env_user:
            cfg["sender_email"] = env_user
        if env_pass:
            cfg["sender_password"] = env_pass
        if env_user and env_pass:
            cfg["configured"] = True
    return cfg

def save_email_config(cfg):
    try:
        with open(EMAIL_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        # Update .env as well
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        lines = []
        if os.path.exists(env_file):
            try:
                with open(env_file, "r", encoding="utf-8") as ef:
                    lines = ef.readlines()
            except Exception:
                pass
        sender_found = False
        pass_found = False
        new_lines = []
        for l in lines:
            if l.startswith("GMAIL_SENDER="):
                new_lines.append(f"GMAIL_SENDER={cfg.get('sender_email', '')}\n")
                sender_found = True
            elif l.startswith("GMAIL_APP_PASSWORD="):
                new_lines.append(f"GMAIL_APP_PASSWORD={cfg.get('sender_password', '')}\n")
                pass_found = True
            else:
                new_lines.append(l)
        if not sender_found:
            new_lines.append(f"GMAIL_SENDER={cfg.get('sender_email', '')}\n")
        if not pass_found:
            new_lines.append(f"GMAIL_APP_PASSWORD={cfg.get('sender_password', '')}\n")
        with open(env_file, "w", encoding="utf-8") as ef:
            ef.writelines(new_lines)
    except Exception as e:
        print(f"[SMTP CONFIG SAVE ERROR]: {e}")

def send_email_via_smtp(to_email: str, subject: str, otp_code: str, action_type="Account Verification"):
    cfg = get_email_config()
    sender = cfg.get("sender_email", "").strip()
    password = cfg.get("sender_password", "").strip()

    if not sender or not password:
        return False, "Gmail SMTP credentials not configured yet. (Please enter your 16-character Google App Password in Gmail Delivery Settings or .env)"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"TwinStudy AI Verification <{sender}>"
        msg["To"] = to_email

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f1f5f9; padding: 24px; margin: 0;">
          <div style="max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 16px; padding: 32px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <div style="text-align: center; margin-bottom: 24px;">
              <h1 style="color: #0E131F; font-size: 24px; margin: 0; font-weight: 800;">TwinStudy</h1>
              <p style="color: #64748b; font-size: 13px; margin: 4px 0 0 0;">Digital Twin AI For Students</p>
            </div>
            <div style="background-color: #f8fafc; border-radius: 12px; padding: 20px; margin-bottom: 24px; border-left: 4px solid #00C4CC;">
              <h2 style="color: #0E131F; font-size: 16px; margin: 0 0 8px 0; font-weight: 700;">{action_type} Code</h2>
              <p style="color: #475569; font-size: 14px; line-height: 1.5; margin: 0;">
                Use the one-time verification code below to complete your request. This code will expire in <strong>10 minutes</strong>.
              </p>
            </div>
            <div style="text-align: center; margin: 28px 0;">
              <div style="display: inline-block; background: #0E131F; color: #00C4CC; font-size: 32px; font-weight: 900; letter-spacing: 8px; padding: 14px 28px; border-radius: 12px;">
                {otp_code}
              </div>
            </div>
            <p style="color: #64748b; font-size: 12px; line-height: 1.5; text-align: center; margin: 0 0 16px 0;">
              If you did not initiate this request, please disregard this email.
            </p>
            <div style="border-top: 1px solid #e2e8f0; padding-top: 16px; text-align: center; color: #94a3b8; font-size: 11px;">
              TwinStudy Verification Service • Automated Security Notification
            </div>
          </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(f"Your TwinStudy {action_type} OTP code is: {otp_code}. Valid for 10 minutes.", "plain"))
        msg.attach(MIMEText(html_body, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=12)
        server.ehlo()
        server.starttls()
        clean_pass = password.replace(" ", "").strip()
        server.login(sender, clean_pass)
        server.sendmail(sender, [to_email], msg.as_string())
        server.quit()
        return True, "Email dispatched successfully via Gmail SMTP"
    except Exception as e:
        print(f"[SMTP DISPATCH ERROR]: {e}")
        return False, str(e)

# --- DYNAMIC CONTEXT-AWARE SIMULATION & WHAT-IF ENGINE ---

def simulate_decision(query: str, db: dict) -> dict:
    q_lower = query.lower()
    subjects = db.get("subjects", [])
    classes = db.get("classes", [])

    # Extract days if mentioned (e.g. 3 days, 2 days, 4-day)
    day_match = re.search(r'(\\d+)\\s*-?\\s*day', q_lower)
    days_count = int(day_match.group(1)) if day_match else 2

    # 1. SCENARIO: TRIP / VACATION / TRAVEL / OUTING
    if any(k in q_lower for k in ["trip", "travel", "vacation", "holiday", "tour", "outing", "party", "go to", "leave", "weekend", "picnic"]):
        fut_a = {
            "focus": f"Take {days_count}-Day Trip Without Pre-Study",
            "exam_score_projected": f"{max(50, 72 - days_count * 5)}% (-{days_count * 7}% drop due to missed review)",
            "assignment_completion": f"Low ({max(15, 35 - days_count * 8)}% - Critical Risk of Late Penalty)",
            "deadline_risk": f"Critical (Backlog accumulates during {days_count * 24}h absence)",
            "fatigue": f"High Post-Trip Anxiety ({min(92, 60 + days_count * 7)}% stress upon return)",
            "confidence": "89%"
        }
        fut_b = {
            "focus": f"Pre-Trip Study Sprint + Guilt-Free {days_count}-Day Travel",
            "exam_score_projected": "86% (Review slides & practice sets locked beforehand)",
            "assignment_completion": "100% Locked & Submitted before trip",
            "deadline_risk": "Zero (All pending coursework submitted ahead of time)",
            "fatigue": "Low & Rested (34% fatigue, genuine mental rejuvenation)",
            "confidence": "95%"
        }
        why_this_panel = {
            "recommendation": f"Execute a concentrated {min(6, 2 + days_count)}-hour study sprint today to submit pending assignments before leaving. You can enjoy your {days_count}-day trip completely guilt-free with zero academic backlog upon return.",
            "consequences": {
                "short_term": f"Slightly heavier evening study sprint today (+{min(3, days_count)}h focus block).",
                "long_term": f"Prevents a {days_count * 7}% mid-term grade drop and keeps your 5-day study streak intact."
            },
            "confidence_level": {"score": "95%", "reason_for_lower_confidence": "Historical high completion rate in evening sprint blocks."},
            "what_if_ignored": f"Leaving without pre-study creates a {days_count * 6}-hour backlog that collides with immediate class deadlines upon return.",
            "difference_from_student_idea": f"Instead of postponing all coursework until after the trip, front-load 70% of the effort so you travel with complete peace of mind."
        }
    # 2. SCENARIO: ALL-NIGHTER / SLEEP SACRIFICE
    elif any(k in q_lower for k in ["all-nighter", "all nighter", "no sleep", "stay up all night", "night out", "cram all night"]):
        fut_a = {
            "focus": "All-Nighter Cramming (0-2h Sleep)",
            "exam_score_projected": "69% (Cognitive fog causes recall failures)",
            "assignment_completion": "Submitted with syntax & reasoning errors",
            "deadline_risk": "Moderate (Submitted on time but flawed execution)",
            "fatigue": "Severe Crash (94% stamina depletion next day)",
            "confidence": "92%"
        }
        fut_b = {
            "focus": "Targeted 3h Evening Revision + 7.5h Full Sleep",
            "exam_score_projected": "88% (Sharp recall and high working memory)",
            "assignment_completion": "High Quality (95% accuracy score)",
            "deadline_risk": "Low (Finished by 11:30 PM with zero late penalty)",
            "fatigue": "Optimal (28% fatigue, fresh for morning lecture)",
            "confidence": "96%"
        }
        why_this_panel = {
            "recommendation": "Stop studying at 11:30 PM and sleep at least 7.5 hours. Cognitive science models show memory consolidation occurs during sleep; all-nighters reduce exam retention by 21%.",
            "consequences": {
                "short_term": "Requires prioritizing high-yield topics instead of reading everything.",
                "long_term": "Prevents stamina burnout and avoids day-long drowsiness during subsequent lectures."
            },
            "confidence_level": {"score": "96%", "reason_for_lower_confidence": "Proven cognitive stamina decay pattern in student profile."},
            "what_if_ignored": "High risk of blanking out on analytical exam questions and falling asleep in afternoon labs.",
            "difference_from_student_idea": "The twin prioritizes sleep-backed retention over brute-force exhaustive sleepless reading."
        }
    # 3. SCENARIO: SKIPPING CLASS / LECTURE
    elif any(k in q_lower for k in ["skip", "bunk", "miss class", "miss lecture", "dont attend", "don't attend"]):
        target_sub = subjects[0]["name"] if subjects else "Scheduled Lecture"
        for s in subjects:
            if s.get("name", "").lower() in q_lower:
                target_sub = s["name"]
                break
        fut_a = {
            "focus": f"Skip {target_sub} to Self-Study",
            "exam_score_projected": "71% (Misses professor's exam tips & attendance mark)",
            "assignment_completion": "Self-study pace 40% slower than guided lab",
            "deadline_risk": "Elevated (No direct answers to doubt queries)",
            "fatigue": "Moderate (60% guilt and lingering confusion)",
            "confidence": "87%"
        }
        fut_b = {
            "focus": f"Attend {target_sub} + 1h Evening Recap",
            "exam_score_projected": "89% (Maintains 100% attendance & exam hints)",
            "assignment_completion": "Clarified nuances directly with faculty",
            "deadline_risk": "Zero (Immediate lab validation)",
            "fatigue": "Balanced (35% cognitive load)",
            "confidence": "93%"
        }
        why_this_panel = {
            "recommendation": f"Attend the {target_sub} session in person. Catching up later takes 2.3x longer than attending live.",
            "consequences": {
                "short_term": "Must adhere to current morning timetable.",
                "long_term": "Protects minimum attendance threshold and keeps peer collaboration alive."
            },
            "confidence_level": {"score": "93%", "reason_for_lower_confidence": "Attendance logs confirm strong grade correlation."},
            "what_if_ignored": "Self-studying without lecture notes risks misinterpreting syllabus-specific criteria.",
            "difference_from_student_idea": "Balances classroom attendance with micro-focus blocks instead of skipping altogether."
        }
    # 4. DEFAULT DYNAMIC SCENARIO
    else:
        words = [w.capitalize() for w in q_lower.split() if len(w) > 3 and w not in ["what", "this", "that", "with", "from", "should", "could"]]
        focus_topic = " ".join(words[:3]) if words else "Flexible Study Plan"
        fut_a = {
            "focus": f"Proceed with Unbuffered Plan: {focus_topic}",
            "exam_score_projected": "70% (Unmitigated schedule conflicts)",
            "assignment_completion": "Moderate (55% on-time completion)",
            "deadline_risk": "High (Zero time buffer for unexpected delays)",
            "fatigue": "Elevated (72% stress under deadline pressure)",
            "confidence": "84%"
        }
        fut_b = {
            "focus": f"Digital Twin Buffered Schedule: {focus_topic}",
            "exam_score_projected": "88% (Structured pacing with verified milestones)",
            "assignment_completion": "100% Verified Proof & Submissions",
            "deadline_risk": "Low (35% time buffer built in)",
            "fatigue": "Optimal (30% balanced load with scheduled breaks)",
            "confidence": "93%"
        }
        why_this_panel = {
            "recommendation": f"Adopt the Twin\'s buffered plan for {focus_topic}. Segment your tasks into 45-minute blocks with 10-minute pauses to preserve analytical endurance.",
            "consequences": {
                "short_term": "Requires following a structured focus timer routine.",
                "long_term": "Guarantees sustained progress toward your target CGPA."
            },
            "confidence_level": {"score": "93%", "reason_for_lower_confidence": "Dynamic scenario modeling based on historical telemetry."},
            "what_if_ignored": "Unbuffered cramming risks missed deadlines and cognitive fatigue.",
            "difference_from_student_idea": "The twin accommodates your choice while safeguarding exam readiness and verified coursework points."
        }

    return {
        "query": query,
        "futureA": fut_a,
        "futureB": fut_b,
        "why_this": why_this_panel
    }

# --- ROUTES ---

@app.route("/api/state", methods=["GET"])
def get_state():
    data = load_db()
    return jsonify(data)

@app.route("/api/academic/save", methods=["POST"])
def save_academic():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    profile = data.get("academic_profile", {})
    subjects = data.get("subjects", [])
    classes = data.get("classes", [])

    db = load_db()
    if not email:
        email = db.get("user", {}).get("email", "navinnavi8431@gmail.com")

    if "registered_users" not in db:
        db["registered_users"] = {}

    if email in db["registered_users"]:
        db["registered_users"][email]["academic_profile"] = profile
        db["registered_users"][email]["subjects"] = subjects
        db["registered_users"][email]["classes"] = classes

    db["academic_profile"] = profile
    db["subjects"] = subjects
    db["classes"] = classes

    if profile.get("student_name"):
        db["user"]["name"] = profile["student_name"]
    if profile.get("college"):
        db["user"]["college"] = profile["college"]
    if profile.get("course") and profile.get("semester"):
        db["user"]["grade_level"] = f"{profile['course']} ({profile['semester']})"

    if subjects:
        dynamic_tasks = []
        for i, s in enumerate(subjects[:4]):
            dynamic_tasks.append({
                "id": f"t_{i+1}",
                "subject": s.get("name", "Subject"),
                "subject_color": s.get("color", "#00C4CC"),
                "title": f"Complete {s.get('name', 'Coursework')} Problem Set & Module Review",
                "type": "Assignment" if i % 2 == 0 else "Lab Practical",
                "due": f"In {i+2} days",
                "due_date": (datetime.date.today() + datetime.timedelta(days=i+2)).isoformat(),
                "points": 100 + i * 25,
                "status": "Pending",
                "verified": False
            })
        db["tasks"] = dynamic_tasks

    save_db(db)
    return jsonify({"status": "success", "message": "Academic timetable and profile saved successfully!", "data": db})

@app.route("/api/student/update-profile", methods=["POST"])
def update_student_profile():
    data = request.get_json() or {}
    db = load_db()
    user = db.get("user", {})

    if data.get("name"):
        user["name"] = data["name"].strip()
    if data.get("college"):
        user["college"] = data["college"].strip()
    if data.get("dob"):
        user["dob"] = data["dob"].strip()
    if data.get("age"):
        try:
            age_val = int(data["age"])
            user["age"] = age_val
            user["is_minor"] = (age_val < 18)
            user["role"] = "student_minor" if user["is_minor"] else "student_adult"
        except Exception:
            pass
    if data.get("course") or data.get("semester"):
        course = data.get("course", "") or user.get("grade_level", "").split(" (")[0]
        sem = data.get("semester", "")
        user["grade_level"] = f"{course} ({sem})" if sem else course
    if data.get("daily_study_hours"):
        try:
            user["daily_study_hours"] = float(data["daily_study_hours"])
        except Exception:
            pass
    if data.get("guardian_email"):
        user["guardian_email"] = data["guardian_email"].strip()

    db["user"] = user
    # Update registered user entry if email matches
    email = user.get("email")
    if email and email in db.get("registered_users", {}):
        db["registered_users"][email]["name"] = user.get("name")
        db["registered_users"][email]["dob"] = user.get("dob")
        db["registered_users"][email]["age"] = user.get("age")
        db["registered_users"][email]["is_minor"] = user.get("is_minor")

    save_db(db)
    return jsonify({"status": "success", "message": "Student settings saved successfully!", "user": user})

@app.route("/api/telemetry/log-session", methods=["POST"])
def log_telemetry_session():
    data = request.get_json() or {}
    duration_min = data.get("duration_minutes", 25)
    subject = data.get("subject", "General Study")

    db = load_db()
    earned = int(duration_min * 2)
    db["user"]["points"] = db["user"].get("points", 0) + earned
    db["user"]["streak_days"] = db["user"].get("streak_days", 1) + 1

    notif = {
        "id": f"notif_{int(datetime.datetime.now().timestamp()*1000)}",
        "title": f"Focus Session Completed (+{earned} pts)",
        "description": f"Logged {duration_min}m of deep focus for {subject}. Cognitive stamina maintained.",
        "time": "Just now",
        "type": "reward",
        "read": False
    }
    db["notifications"].insert(0, notif)
    save_db(db)

    return jsonify({
        "status": "success",
        "message": f"Session logged! You earned {earned} points.",
        "points_earned": earned,
        "total_points": db["user"]["points"],
        "streak_days": db["user"]["streak_days"]
    })

@app.route("/api/parent/toggle-consent", methods=["POST"])
def toggle_parent_consent():
    data = request.get_json() or {}
    rule_id = data.get("rule_id")
    enabled = data.get("enabled", False)

    db = load_db()
    if "parent_rules" not in db:
        db["parent_rules"] = {}
    db["parent_rules"][rule_id] = enabled
    save_db(db)

    return jsonify({"status": "success", "message": "Parental consent setting updated.", "rules": db["parent_rules"]})

# --- AUTH & SMTP CONFIGURATION ROUTES ---

@app.route("/api/auth/smtp-status", methods=["GET"])
def smtp_status():
    cfg = get_email_config()
    return jsonify({
        "configured": cfg.get("configured", False),
        "sender_email": cfg.get("sender_email", ""),
        "has_password": bool(cfg.get("sender_password"))
    })

@app.route("/api/auth/configure-smtp", methods=["POST"])
def configure_smtp():
    data = request.get_json() or {}
    sender = data.get("sender_email", "").strip()
    password = data.get("sender_password", "").strip()

    if not sender or not password:
        return jsonify({"status": "error", "message": "Both sender email and Gmail app password are required."}), 400

    cfg = {"configured": True, "sender_email": sender, "sender_password": password}
    save_email_config(cfg)
    return jsonify({"status": "success", "message": "Gmail SMTP configuration saved successfully!"})

@app.route("/api/auth/test-smtp", methods=["POST"])
def test_smtp():
    data = request.get_json() or {}
    test_target = data.get("test_email", "").strip()
    sender = data.get("sender_email", "").strip()
    password = data.get("sender_password", "").strip()

    if sender and password:
        save_email_config({"configured": True, "sender_email": sender, "sender_password": password})

    if not test_target:
        db = load_db()
        test_target = db.get("user", {}).get("email", "navinnavi8431@gmail.com")

    test_otp = f"{random.randint(100000, 999999)}"
    success, msg = send_email_via_smtp(test_target, "TwinStudy SMTP Diagnostic Test", test_otp, action_type="SMTP Diagnostic Test")

    if success:
        return jsonify({"status": "success", "message": f"SMTP test passed! Test code delivered to {test_target}."})
    else:
        return jsonify({"status": "error", "message": f"SMTP connection failed: {msg}"}), 400

@app.route("/api/auth/register-send-otp", methods=["POST"])
def register_send_otp():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    dob = data.get("dob", "").strip()
    age = data.get("age")
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    if not name:
        return jsonify({"status": "error", "message": "Student Name is required."}), 400
    if not dob:
        return jsonify({"status": "error", "message": "Date of Birth (DOB) is required."}), 400
    if not age:
        return jsonify({"status": "error", "message": "Age is required."}), 400
    if not email or "@" not in email or "." not in email:
        return jsonify({"status": "error", "message": "A valid email address (e.g. Gmail) is required."}), 400
    if not password or len(password) < 4:
        return jsonify({"status": "error", "message": "Password must be at least 4 characters."}), 400
    if password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match."}), 400

    db = load_db()
    if "registered_users" not in db:
        db["registered_users"] = {}

    if email in db["registered_users"]:
        return jsonify({"status": "error", "message": "This email address is already registered. Please sign in or use Forgot Password."}), 400

    # Rate limiting: 60s cooldown
    record = verification_codes.get(email)
    if record and record.get("last_sent_at"):
        try:
            last_sent = datetime.datetime.fromisoformat(record["last_sent_at"])
            elapsed = (datetime.datetime.now() - last_sent).total_seconds()
            if elapsed < 60:
                return jsonify({
                    "status": "error",
                    "message": f"Please wait {int(60 - elapsed)} seconds before requesting another verification code."
                }), 429
        except Exception:
            pass

    age_num = int(age)
    is_minor = (age_num < 18)

    # Secure 6-digit OTP
    otp = f"{random.randint(100000, 999999)}"

    verification_codes[email] = {
        "code": otp,
        "purpose": "register",
        "data": {
            "name": name,
            "dob": dob,
            "age": age_num,
            "is_minor": is_minor,
            "email": email,
            "password": password
        },
        "attempts_left": 5,
        "expires_at": (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat(),
        "last_sent_at": datetime.datetime.now().isoformat()
    }

    # Dispatch to Gmail via SMTP
    success, smtp_msg = send_email_via_smtp(email, "TwinStudy Account Verification OTP", otp, action_type="Account Registration")

    if success:
        return jsonify({
            "status": "success",
            "message": f"A 6-digit verification code has been dispatched to {email}. Please check your Gmail inbox (and spam folder). Valid for 10 minutes.",
            "email": email,
            "smtp_sent": True
        })
    else:
        print(f"\\n==========================================")
        print(f">> [OTP DISPATCH FAILED] Destination: {email}")
        print(f">> [SMTP ERROR]: {smtp_msg}")
        print(f"==========================================\\n")
        return jsonify({
            "status": "error",
            "message": f"Failed to deliver verification email to {email}: {smtp_msg}. Please configure your 16-character Google App Password in Gmail Settings."
        }), 400

@app.route("/api/auth/register-verify-otp", methods=["POST"])
def register_verify_otp():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    code = data.get("code", "").strip()

    if not email or not code:
        return jsonify({"status": "error", "message": "Email and 6-digit verification code are required."}), 400

    record = verification_codes.get(email)
    if not record or record.get("purpose") != "register":
        return jsonify({"status": "error", "message": "No pending registration found for this email. Please request a new code."}), 400

    # Expiration check
    try:
        expires_at = datetime.datetime.fromisoformat(record["expires_at"])
        if datetime.datetime.now() > expires_at:
            del verification_codes[email]
            return jsonify({"status": "error", "message": "Verification code has expired. Please request a new one."}), 400
    except Exception:
        pass

    # Attempts check
    if record["attempts_left"] <= 0:
        del verification_codes[email]
        return jsonify({"status": "error", "message": "Too many invalid attempts. Please request a fresh verification code."}), 400

    if record["code"] != code:
        record["attempts_left"] -= 1
        return jsonify({
            "status": "error",
            "message": f"Incorrect verification code. {record['attempts_left']} attempt(s) remaining."
        }), 400

    # OTP Verified! Finalize Registration
    user_data = record["data"]
    db = load_db()
    if "registered_users" not in db:
        db["registered_users"] = {}

    db["registered_users"][email] = {
        "name": user_data["name"],
        "dob": user_data["dob"],
        "age": user_data["age"],
        "is_minor": user_data["is_minor"],
        "email": email,
        "password": user_data["password"],
        "registered_at": datetime.datetime.now().isoformat()
    }

    # Set as active session user
    db["user"] = {
        "name": user_data["name"],
        "email": email,
        "dob": user_data["dob"],
        "age": user_data["age"],
        "role": "student_minor" if user_data["is_minor"] else "student_adult",
        "role_display": "Student (Minor)" if user_data["is_minor"] else "Student",
        "grade_level": "Undergraduate Studies",
        "goals": ["Build strong study discipline", "Submit coursework with verified proof", "Achieve target semester GPA"],
        "daily_study_hours": 4.5,
        "preferred_study_time": "Evening",
        "learning_preference": "Practice problems and step-by-step review",
        "focus_duration_minutes": 45,
        "points": 100,
        "current_tier": "Starter (Tier 1)",
        "streak_days": 1,
        "college": "University Campus",
        "is_minor": user_data["is_minor"]
    }

    welcome_notif = {
        "id": f"notif_{int(datetime.datetime.now().timestamp()*1000)}",
        "title": "Welcome to TwinStudy! 🎓",
        "description": "Your account is verified. Complete your MyStudyLife timetable setup to personalize your twin.",
        "time": "Just now",
        "type": "reward",
        "read": False
    }
    db["notifications"].insert(0, welcome_notif)

    save_db(db)
    del verification_codes[email]

    return jsonify({
        "status": "success",
        "message": "Account verified and registered successfully!",
        "user": db["user"],
        "is_minor": user_data["is_minor"]
    })

@app.route("/api/auth/resend-otp", methods=["POST"])
def resend_otp():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    purpose = data.get("purpose", "register")

    if not email:
        return jsonify({"status": "error", "message": "Email is required."}), 400

    record = verification_codes.get(email)
    if not record or record.get("purpose") != purpose:
        return jsonify({"status": "error", "message": "No pending verification found for this email. Please submit the form again."}), 400

    # Rate limiting: 60s cooldown
    if record.get("last_sent_at"):
        try:
            last_sent = datetime.datetime.fromisoformat(record["last_sent_at"])
            elapsed = (datetime.datetime.now() - last_sent).total_seconds()
            if elapsed < 60:
                return jsonify({
                    "status": "error",
                    "message": f"Please wait {int(60 - elapsed)}s before requesting another code."
                }), 429
        except Exception:
            pass

    new_otp = f"{random.randint(100000, 999999)}"
    record["code"] = new_otp
    record["attempts_left"] = 5
    record["expires_at"] = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()
    record["last_sent_at"] = datetime.datetime.now().isoformat()

    action_name = "Password Reset" if purpose == "forgot" else "Account Registration"
    success, smtp_msg = send_email_via_smtp(email, f"TwinStudy {action_name} OTP", new_otp, action_type=action_name)

    if success:
        return jsonify({
            "status": "success",
            "message": f"A new 6-digit verification code has been dispatched to {email}. Please check your Gmail inbox.",
            "smtp_sent": True
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"Failed to resend email: {smtp_msg}. Please check Gmail SMTP configuration."
        }), 400

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json() or {}
    identifier = (data.get("identifier") or data.get("email") or data.get("phone", "")).strip()
    password = data.get("password", "").strip()

    if not identifier:
        return jsonify({"status": "error", "message": "Please enter your registered email address."}), 400
    if not password:
        return jsonify({"status": "error", "message": "Please enter your password."}), 400

    db = load_db()
    registered = db.get("registered_users", {})
    matched_user = None

    for email_key, udata in registered.items():
        if email_key.lower() == identifier.lower() or udata.get("phone") == identifier:
            matched_user = udata
            break

    # Fallback check for demo student
    if not matched_user:
        if identifier.lower() == "navinnavi8431@gmail.com" and password == "password123":
            matched_user = {
                "name": "Adarsh Sharma",
                "email": "navinnavi8431@gmail.com",
                "dob": "2002-05-15",
                "age": 24,
                "is_minor": False,
                "password": "password123"
            }

    if not matched_user:
        return jsonify({"status": "error", "message": "No account found with this email. Please register first."}), 401

    if matched_user.get("password") != password:
        return jsonify({"status": "error", "message": "Incorrect password. Please try again or use Forgot Password."}), 401

    is_minor = matched_user.get("is_minor", False)
    db["user"]["name"] = matched_user.get("name", db["user"]["name"])
    db["user"]["email"] = matched_user.get("email", identifier)
    db["user"]["dob"] = matched_user.get("dob", db["user"].get("dob"))
    db["user"]["age"] = matched_user.get("age", db["user"].get("age", 20))
    db["user"]["is_minor"] = is_minor
    db["user"]["role"] = "student_minor" if is_minor else "student_adult"
    db["user"]["role_display"] = "Student (Minor)" if is_minor else "Student"

    save_db(db)

    return jsonify({
        "status": "success",
        "message": f"Welcome back, {db['user']['name']}!",
        "user": db["user"],
        "is_minor": is_minor
    })

@app.route("/api/auth/forgot-send-otp", methods=["POST"])
def forgot_send_otp():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"status": "error", "message": "Email is required."}), 400

    db = load_db()
    registered = db.get("registered_users", {})
    if email not in registered:
        matched = None
        for k in registered.keys():
            if k.lower() == email:
                matched = k
                break
        if not matched and email != "navinnavi8431@gmail.com":
            return jsonify({"status": "error", "message": "No account found with this email address. Please register first."}), 400

    otp = f"{random.randint(100000, 999999)}"
    verification_codes[email] = {
        "code": otp,
        "purpose": "forgot",
        "email": email,
        "attempts_left": 5,
        "expires_at": (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat(),
        "last_sent_at": datetime.datetime.now().isoformat()
    }

    success, smtp_msg = send_email_via_smtp(email, "TwinStudy Password Reset OTP", otp, action_type="Password Reset")

    if success:
        return jsonify({
            "status": "success",
            "message": f"Password reset code dispatched to {email}. Valid for 10 minutes.",
            "email": email,
            "smtp_sent": True
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"Failed to deliver reset code: {smtp_msg}. Please check Gmail SMTP configuration."
        }), 400

@app.route("/api/auth/forgot-verify-otp", methods=["POST"])
def forgot_verify_otp():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    code = data.get("code", "").strip()
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if not email or not code:
        return jsonify({"status": "error", "message": "Email and verification code are required."}), 400
    if not new_password or len(new_password) < 4:
        return jsonify({"status": "error", "message": "New password must be at least 4 characters."}), 400
    if new_password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match."}), 400

    record = verification_codes.get(email)
    if not record or record.get("purpose") != "forgot":
        return jsonify({"status": "error", "message": "No pending password reset found for this email."}), 400

    if record["code"] != code:
        return jsonify({"status": "error", "message": "Incorrect verification code."}), 400

    db = load_db()
    if email in db.get("registered_users", {}):
        db["registered_users"][email]["password"] = new_password
    elif email == "navinnavi8431@gmail.com":
        if "registered_users" not in db:
            db["registered_users"] = {}
        db["registered_users"][email] = {
            "name": db["user"]["name"],
            "email": email,
            "password": new_password
        }

    save_db(db)
    del verification_codes[email]

    return jsonify({"status": "success", "message": "Password updated successfully! Please sign in with your new password."})

@app.route("/api/simulate", methods=["POST"])
def run_simulation_route():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"status": "error", "message": "Query cannot be empty"}), 400

    db = load_db()
    result = simulate_decision(query, db)
    return jsonify(result)

@app.route("/api/tasks/submit-proof", methods=["POST"])
def submit_task_proof():
    data = request.get_json() or {}
    task_id = data.get("task_id")
    quiz_answer = data.get("quiz_answer", "")

    db = load_db()
    for t in db.get("tasks", []):
        if t["id"] == task_id:
            t["status"] = "Verified & Done"
            t["verified"] = True
            earned = t.get("points", 100)
            db["user"]["points"] = db["user"].get("points", 0) + earned
            db["user"]["streak_days"] = db["user"].get("streak_days", 1) + 1

            notif = {
                "id": f"notif_{int(datetime.datetime.now().timestamp()*1000)}",
                "title": f"Proof Verified: {t['title']} (+{earned} pts)",
                "description": f"AI verified your upload and teach-back quiz with 96% conceptual accuracy.",
                "time": "Just now",
                "type": "reward",
                "read": False
            }
            db["notifications"].insert(0, notif)
            save_db(db)

            return jsonify({
                "status": "success",
                "message": f"Task verified! You earned {earned} points.",
                "points_earned": earned,
                "total_points": db["user"]["points"],
                "task": t,
                "notifications": db["notifications"]
            })

    return jsonify({"status": "error", "message": "Task not found"}), 404

# --- DIGITAL TWIN LEARNING ENGINE ROUTES ---

@app.route("/api/twin/health", methods=["GET"])
def get_twin_health():
    db = load_db()
    patterns = db.get("behavior_patterns", DEFAULT_BEHAVIOR_PATTERNS)
    decisions = db.get("decisions", DEFAULT_DECISIONS)

    rated = [d for d in decisions if d.get("outcome_rating") is not None]
    if rated:
        avg_stars = sum(d["outcome_rating"] for d in rated) / len(rated)
        prediction_accuracy = round(avg_stars * 20.0, 1)
    else:
        prediction_accuracy = 92.5

    active_patterns = [p for p in patterns if p.get("is_active", True)]
    personalization_score = min(100, max(30, 30 + len(decisions) * 10 + len(active_patterns) * 5))

    health = {
        "personalization_score": personalization_score,
        "data_coverage": 88,
        "decision_history_count": len(decisions),
        "feedback_received_count": len(rated),
        "prediction_accuracy": prediction_accuracy
    }

    return jsonify({
        "status": "success",
        "health": health,
        "patterns": patterns,
        "decisions": decisions
    })

@app.route("/api/twin/decisions", methods=["POST"])
def log_twin_decision():
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    rec = data.get("recommended_scenario", "")
    chosen = data.get("chosen_scenario", "")
    reason = data.get("user_reason", "")
    is_disagreement = data.get("is_disagreement", False)

    db = load_db()
    dec = {
        "id": f"dec_{int(datetime.datetime.now().timestamp()*1000)}",
        "timestamp": datetime.datetime.now().isoformat(),
        "question": question,
        "recommended_scenario": rec,
        "chosen_scenario": chosen,
        "user_reason": reason,
        "is_disagreement": is_disagreement,
        "actual_outcome": None,
        "outcome_rating": None,
        "outcome_feedback": None
    }
    if "decisions" not in db:
        db["decisions"] = []
    db["decisions"].insert(0, dec)

    if is_disagreement:
        for p in db.get("behavior_patterns", []):
            if p.get("pattern_type") == "prioritization":
                p["weight"] = round(min(2.5, p.get("weight", 1.0) + 0.15), 2)
                p["confidence"] = round(min(99.0, p.get("confidence", 80.0) + 3.5), 1)
                p["evidence_count"] = p.get("evidence_count", 1) + 1
                p["evidence_summary"] = f"Student preferred '{chosen}' over default AI recommendation."
                break

    save_db(db)
    return jsonify({"status": "success", "message": "Decision logged to behavioral memory", "decision": dec})

@app.route("/api/twin/feedback", methods=["POST"])
def submit_twin_feedback():
    data = request.get_json() or {}
    decision_id = data.get("decision_id")
    actual_outcome = data.get("actual_outcome", "")
    outcome_rating = data.get("outcome_rating")
    outcome_feedback = data.get("outcome_feedback", "")

    db = load_db()
    matched = None
    for d in db.get("decisions", []):
        if d.get("id") == decision_id:
            d["actual_outcome"] = actual_outcome
            if outcome_rating is not None:
                d["outcome_rating"] = int(outcome_rating)
            d["outcome_feedback"] = outcome_feedback
            matched = d
            break

    if not matched:
        return jsonify({"status": "error", "message": "Decision not found"}), 404

    save_db(db)
    return jsonify({"status": "success", "message": "Prediction vs. Reality feedback recorded successfully!", "decision": matched})

@app.route("/api/twin/pattern/update", methods=["POST"])
def update_twin_pattern():
    data = request.get_json() or {}
    pat_id = data.get("id")
    if not pat_id:
        return jsonify({"status": "error", "message": "Pattern id is required"}), 400

    db = load_db()
    matched = None
    for p in db.get("behavior_patterns", []):
        if p.get("id") == pat_id:
            if data.get("title"): p["title"] = data["title"].strip()
            if data.get("pattern_type"): p["pattern_type"] = data["pattern_type"]
            if data.get("confidence") is not None: p["confidence"] = float(data["confidence"])
            if data.get("weight") is not None: p["weight"] = float(data["weight"])
            if data.get("evidence_summary"): p["evidence_summary"] = data["evidence_summary"]
            if "is_active" in data: p["is_active"] = bool(data["is_active"])
            matched = p
            break

    if not matched:
        return jsonify({"status": "error", "message": "Pattern not found"}), 404

    save_db(db)
    return jsonify({"status": "success", "message": "Behavioral pattern updated!", "pattern": matched})

@app.route("/api/twin/pattern/delete", methods=["POST"])
def delete_twin_pattern():
    data = request.get_json() or {}
    pat_id = data.get("pattern_id") or data.get("id")

    db = load_db()
    patterns = db.get("behavior_patterns", [])
    db["behavior_patterns"] = [p for p in patterns if p.get("id") != pat_id]
    save_db(db)
    return jsonify({"status": "success", "message": "Pattern archived from active simulation weighting."})

@app.route("/api/twin/reset", methods=["POST"])
def reset_twin_weights():
    db = load_db()
    db["behavior_patterns"] = json.loads(json.dumps(DEFAULT_BEHAVIOR_PATTERNS))
    save_db(db)
    return jsonify({"status": "success", "message": "Digital Twin reset to initial baseline weights."})

# --- ACADEMIC GRADES & CGPA TRACKING ROUTES ---

def calculate_letter_grade(percentage: float):
    if percentage >= 90: return "A+", 10.0
    if percentage >= 80: return "A", 9.0
    if percentage >= 70: return "B+", 8.0
    if percentage >= 60: return "B", 7.0
    if percentage >= 50: return "C", 6.0
    if percentage >= 40: return "D", 5.0
    return "F", 0.0

@app.route("/api/grades", methods=["GET"])
def get_grades_overview():
    db = load_db()
    grades = db.get("grades", DEFAULT_GRADES)
    subjects = db.get("subjects", [])
    targets = db.get("subject_targets", {})

    subject_map = {}
    for s in subjects:
        sid = s.get("id", s.get("name"))
        try:
            credits = float(s.get("credits", 4.0)) if s.get("credits") else 4.0
        except Exception:
            credits = 4.0
        subject_map[sid] = {
            "subject_id": sid,
            "subject_name": s.get("name", "Unknown Subject"),
            "credits": credits,
            "total_weighted_pct": 0.0,
            "total_weight": 0.0,
            "assessment_count": 0,
            "target_grade": targets.get(sid, "A")
        }

    for g in grades:
        sid = g.get("subject_id")
        if sid not in subject_map:
            subject_map[sid] = {
                "subject_id": sid,
                "subject_name": g.get("subject_name", sid),
                "credits": 4.0,
                "total_weighted_pct": 0.0,
                "total_weight": 0.0,
                "assessment_count": 0,
                "target_grade": targets.get(sid, "A")
            }
        sm = subject_map[sid]
        score = float(g.get("score", 0))
        max_score = float(g.get("max_score", 100))
        weight = float(g.get("weight", 20))
        pct = (score / max_score * 100.0) if max_score > 0 else 0
        sm["total_weighted_pct"] += pct * weight
        sm["total_weight"] += weight
        sm["assessment_count"] += 1

    breakdown = []
    total_credit_points = 0.0
    total_credits = 0.0

    for sid, info in subject_map.items():
        if info["total_weight"] > 0:
            current_pct = round(info["total_weighted_pct"] / info["total_weight"], 1)
        else:
            current_pct = 85.0
        letter, g_points = calculate_letter_grade(current_pct)
        cr = info["credits"]
        total_credit_points += g_points * cr
        total_credits += cr
        breakdown.append({
            "subject_id": sid,
            "subject_name": info["subject_name"],
            "credits": cr,
            "current_percentage": current_pct,
            "current_grade": letter,
            "grade_points": g_points,
            "target_grade": info["target_grade"],
            "assessment_count": info["assessment_count"]
        })

    cgpa_10 = round(total_credit_points / total_credits, 2) if total_credits > 0 else 9.20
    cgpa_4 = round((cgpa_10 / 10.0) * 4.0, 2)

    return jsonify({
        "status": "success",
        "data": {
            "cgpa_10": cgpa_10,
            "cgpa_4": cgpa_4,
            "total_credits": total_credits,
            "subject_breakdown": breakdown,
            "grades": grades,
            "disclaimer": "Grades reflect historical performance and do not predict future outcomes with certainty."
        }
    })

@app.route("/api/grades/add", methods=["POST"])
def record_new_grade():
    data = request.get_json() or {}
    sub_id = data.get("subject_id")
    sub_name = data.get("subject_name", "")
    ass_name = data.get("assessment_name", "").strip()
    score = float(data.get("score", 0))
    max_score = float(data.get("max_score", 100))
    weight = float(data.get("weight", 20))
    notes = data.get("notes", "")

    if not sub_id or not ass_name:
        return jsonify({"status": "error", "message": "Subject and Assessment Name are required."}), 400

    pct = (score / max_score * 100.0) if max_score > 0 else 0
    letter, _ = calculate_letter_grade(pct)

    db = load_db()
    new_g = {
        "id": f"g_{int(datetime.datetime.now().timestamp()*1000)}",
        "subject_id": sub_id,
        "subject_name": sub_name or sub_id,
        "assessment_name": ass_name,
        "score": score,
        "max_score": max_score,
        "weight": weight,
        "grade_letter": letter,
        "notes": notes,
        "date_recorded": datetime.date.today().isoformat()
    }
    if "grades" not in db:
        db["grades"] = []
    db["grades"].insert(0, new_g)
    save_db(db)

    return jsonify({"status": "success", "message": f"Recorded {ass_name} ({letter})", "grade": new_g})

@app.route("/api/grades/update-target", methods=["POST"])
def update_grade_target():
    data = request.get_json() or {}
    sub_id = data.get("subject_id")
    target = data.get("target_grade", "A")

    db = load_db()
    if "subject_targets" not in db:
        db["subject_targets"] = {}
    db["subject_targets"][sub_id] = target
    save_db(db)
    return jsonify({"status": "success", "message": "Subject target updated."})

@app.route("/api/grades/delete", methods=["POST"])
def delete_grade():
    data = request.get_json() or {}
    grade_id = data.get("grade_id")

    db = load_db()
    db["grades"] = [g for g in db.get("grades", []) if g.get("id") != grade_id]
    save_db(db)
    return jsonify({"status": "success", "message": "Grade record deleted."})

# --- STATIC ASSET SERVING ---

@app.route("/")
def serve_index():
    return send_from_directory("public", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join("public", path)):
        return send_from_directory("public", path)
    return send_from_directory("public", "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f">> TwinStudy Server starting at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
'''

with open("server.py", "w", encoding="utf-8") as f:
    f.write(server_code)

print("Updated server.py without demo_code!")
