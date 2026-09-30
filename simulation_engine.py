"""
Digital Twin Cognitive & Simulation Engine (Python & Pandas)
Includes MyStudyLife Timetable & Scout AI Planner, PLUS advanced Digital Twin Features:
Counterfactual "What-If" simulation, Fatigue modeling, Sacrifice Index, and Adaptive Recalibration.
"""

import datetime
import json
import os
import requests
import pandas as pd
import numpy as np

class DigitalTwinEngine:
    def __init__(self):
        # Default behavioral weights (Cognitive DNA)
        self.default_profile = {
            "name": "Alex Chen",
            "role": "3rd Year Computer Science Student",
            "risk_tolerance": 0.65,        # 0.0 (Ultra Safe) to 1.0 (High Risk)
            "high_stakes_bias": 0.75,      # 0.0 (Equal) to 1.0 (Prioritizes major exams over homework)
            "fatigue_sensitivity": 0.70,   # Drop in cognitive efficiency under sleep debt
            "night_owl_factor": 0.85,      # Efficiency multiplier during late night (20:00 - 01:00)
            "target_sleep_hours": 7.0,
            "min_sleep_threshold": 5.0
        }
        
        # Privacy Permissions (Sovereign Vault)
        self.privacy_permissions = {
            "academic_calendar": True,
            "sleep_biometrics": True,
            "social_activity": False,
            "private_notes": False
        }
        
        # MyStudyLife Class Timetable
        self.classes_schedule = self._init_classes_schedule()
        
        # MyStudyLife Tasks & Deadlines
        self.tasks = self._init_default_tasks()
        
        # Decision history log & Scout Chat history
        self.decision_history = []
        self.scout_messages = [
            {"role": "assistant", "content": "👋 Hi Alex! I am Scout, your MyStudyLife AI study coach. Ask me about your timetable, upcoming deadlines, or study plans. (For multi-future simulation, check your Twin tab!)"}
        ]
        
        # Load state if exists
        self.state_file = os.path.join(os.path.dirname(__file__), "twin_state.json")
        self.load_state()

    def _init_classes_schedule(self):
        return pd.DataFrame([
            {"Day": "Monday", "Time": "10:00 - 11:30 AM", "Course": "CS 301 - Algorithms", "Room": "Room 402", "Instructor": "Dr. Vance", "Color": "#3b82f6"},
            {"Day": "Monday", "Time": "01:00 - 02:30 PM", "Course": "CS 340 - Database Systems", "Room": "Lab 2B", "Instructor": "Prof. Chen", "Color": "#10b981"},
            {"Day": "Tuesday", "Time": "09:00 - 10:30 AM", "Course": "CS 370 - Computer Networks", "Room": "Auditorium C", "Instructor": "Dr. Sarah", "Color": "#8b5cf6"},
            {"Day": "Wednesday", "Time": "10:00 - 11:30 AM", "Course": "CS 301 - Algorithms", "Room": "Room 402", "Instructor": "Dr. Vance", "Color": "#3b82f6"},
            {"Day": "Wednesday", "Time": "02:00 - 04:00 PM", "Course": "CS 340 - Database Lab", "Room": "Lab 2B", "Instructor": "Prof. Chen", "Color": "#10b981"},
            {"Day": "Thursday", "Time": "11:00 - 12:30 PM", "Course": "CS 370 - Computer Networks", "Room": "Auditorium C", "Instructor": "Dr. Sarah", "Color": "#8b5cf6"},
            {"Day": "Friday", "Time": "10:00 - 11:30 AM", "Course": "CS 301 - Tutorial / Problem Solving", "Room": "Room 402", "Instructor": "TA Mark", "Color": "#3b82f6"},
        ])

    def _init_default_tasks(self):
        return pd.DataFrame([
            {
                "id": "task_1",
                "course": "CS 301 - Algorithms",
                "title": "Midterm Examination",
                "type": "Exam",
                "due_in_hours": 72,
                "weight_percent": 40,
                "est_prep_hours_needed": 16,
                "current_readiness": 55, # %
                "completed": False,
                "late_allowed": False
            },
            {
                "id": "task_2",
                "course": "CS 340 - Database Systems",
                "title": "Assignment #2: SQL & Normalization",
                "type": "Assignment",
                "due_in_hours": 36,
                "weight_percent": 15,
                "est_prep_hours_needed": 8,
                "current_readiness": 30, # %
                "completed": False,
                "late_allowed": True,
                "late_penalty_per_day": 10 # % deduction per 24h
            },
            {
                "id": "task_3",
                "course": "CS 370 - Computer Networks",
                "title": "Lab Quiz 3: Packet Routing",
                "type": "Quiz",
                "due_in_hours": 120,
                "weight_percent": 5,
                "est_prep_hours_needed": 4,
                "current_readiness": 70,
                "completed": False,
                "late_allowed": False
            }
        ])

    def add_new_task(self, course, title, task_type, due_hours, weight, hours_needed):
        new_row = pd.DataFrame([{
            "id": f"task_{len(self.tasks)+1}",
            "course": course,
            "title": title,
            "type": task_type,
            "due_in_hours": due_hours,
            "weight_percent": weight,
            "est_prep_hours_needed": hours_needed,
            "current_readiness": 20,
            "completed": False,
            "late_allowed": (task_type == "Assignment")
        }])
        self.tasks = pd.concat([self.tasks, new_row], ignore_index=True)
        self.save_state()

    def toggle_task_completion(self, task_id, completed):
        idx = self.tasks[self.tasks["id"] == task_id].index
        if len(idx) > 0:
            self.tasks.loc[idx, "completed"] = completed
            self.save_state()

    def save_state(self):
        data = {
            "profile": self.default_profile,
            "privacy_permissions": self.privacy_permissions,
            "decision_history": self.decision_history
        }
        try:
            with open(self.state_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                    self.default_profile.update(data.get("profile", {}))
                    self.privacy_permissions.update(data.get("privacy_permissions", {}))
                    self.decision_history = data.get("decision_history", [])
            except Exception:
                pass

    def reset_twin_memory(self):
        self.default_profile["high_stakes_bias"] = 0.75
        self.default_profile["risk_tolerance"] = 0.65
        self.default_profile["fatigue_sensitivity"] = 0.70
        self.decision_history = []
        self.save_state()
        return "Twin cognitive memory reset to baseline."

    # --- SCOUT AI ASSISTANT CHAT ENGINE (MyStudyLife Baseline) ---
    def ask_scout(self, user_msg: str) -> str:
        msg_lower = user_msg.lower()
        if "next class" in msg_lower or "today" in msg_lower:
            ans = "📅 **Next Class:** Today you have **CS 301 - Algorithms** at 10:00 AM in Room 402 with Dr. Vance, followed by **CS 340 - Database Systems** at 1:00 PM in Lab 2B."
        elif "deadline" in msg_lower or "due" in msg_lower or "homework" in msg_lower or "assignment" in msg_lower:
            ans = "🚨 **Upcoming Deadlines:**\n- **CS 340 Assignment #2:** Due in **36 hours** (Worth 15%)\n- **CS 301 Algorithms Midterm:** In **72 hours** (Worth 40%)\n- **CS 370 Lab Quiz:** In **120 hours** (Worth 5%)"
        elif "exam" in msg_lower or "midterm" in msg_lower or "revision" in msg_lower:
            ans = "📚 **Revision Guidance:** Your **Algorithms Midterm** is 40% of your total grade. You currently need ~16 prep hours. Recommendation: Focus on Dynamic Programming & Graph Theory."
        else:
            ans = f"🤖 **Scout:** I've noted that! You have 3 active assessments this week. If you're facing a tough choice between studying for the exam vs. finishing your assignment, test it in the **'What-If Simulator'** tab to see your trade-offs simulated!"
        
        self.scout_messages.append({"role": "user", "content": user_msg})
        self.scout_messages.append({"role": "assistant", "content": ans})
        return ans

    # --- PANDAS FATIGUE & ENERGY MODELING ---
    def generate_fatigue_curve(self, scenario: str, hours: int = 48) -> pd.DataFrame:
        timeline = []
        has_biometrics = self.privacy_permissions.get("sleep_biometrics", True)
        base_fatigue_sens = self.default_profile["fatigue_sensitivity"] if has_biometrics else 0.50
        
        for h in range(1, hours + 1):
            clock_hour = (datetime.datetime.now().hour + h) % 24
            
            if 20 <= clock_hour or clock_hour <= 1:
                circadian = 85.0  # Peak night focus
            elif 2 <= clock_hour <= 7:
                circadian = 35.0  # Deep sleep window
            elif 8 <= clock_hour <= 12:
                circadian = 75.0  # Morning focus
            else:
                circadian = 60.0  # Afternoon
                
            if scenario == "timeline_a": # Cram exam, skip sleep
                sleep_debt_multiplier = 1.0 - (h / hours) * 0.45 * base_fatigue_sens
                energy = max(20.0, circadian * sleep_debt_multiplier - (15.0 if 2 <= clock_hour <= 6 else 0))
                cognitive_focus = max(15.0, energy - 10.0)
            elif scenario == "timeline_b": # Normal study, sleep
                energy = circadian
                cognitive_focus = max(40.0, energy * 0.95)
            else: # Hybrid
                sleep_debt_multiplier = 1.0 - (h / hours) * 0.20 * base_fatigue_sens
                energy = max(35.0, circadian * sleep_debt_multiplier)
                cognitive_focus = max(35.0, energy * 0.92)

            timeline.append({
                "Hour": f"+{h}h ({clock_hour}:00)",
                "Biological_Energy": round(energy, 1),
                "Cognitive_Focus": round(cognitive_focus, 1),
                "Burnout_Risk_Zone": 40.0
            })
            
        return pd.DataFrame(timeline)

    # --- MULTI-BRANCH SIMULATION ENGINE (WHAT-IF) ---
    def simulate_what_if(self, query: str, api_key: str = None) -> dict:
        tasks_df = self.tasks.copy()
        exam_task = tasks_df[tasks_df["type"] == "Exam"].iloc[0]
        assign_task = tasks_df[tasks_df["type"] == "Assignment"].iloc[0]

        # Quantitative simulation results via Pandas
        exam_score_a = min(96, exam_task["current_readiness"] + 38)
        assign_score_a = max(0, assign_task["current_readiness"] - 20)
        burnout_a = 78
        gpa_impact_a = (exam_score_a * (exam_task["weight_percent"] / 100)) + (assign_score_a * (assign_task["weight_percent"] / 100))

        assign_score_b = 92
        exam_score_b = min(78, exam_task["current_readiness"] + 18)
        burnout_b = 42
        gpa_impact_b = (exam_score_b * (exam_task["weight_percent"] / 100)) + (assign_score_b * (assign_task["weight_percent"] / 100))

        exam_score_c = 88
        assign_score_c = 82
        burnout_c = 52
        gpa_impact_c = (exam_score_c * (exam_task["weight_percent"] / 100)) + (assign_score_c * (assign_task["weight_percent"] / 100))

        net_tradeoff_delta = round(gpa_impact_a - gpa_impact_b, 2)
        high_stakes_bias = self.default_profile["high_stakes_bias"]
        
        if high_stakes_bias > 0.82:
            recommended_branch = "Timeline A"
            rec_reason = "Your profile heavily favors acing high-stakes exams over routine homework penalties."
        elif high_stakes_bias < 0.50:
            recommended_branch = "Timeline B"
            rec_reason = "Your profile avoids late penalties and maintains consistent submission reliability."
        else:
            recommended_branch = "Timeline C (Dynamic Hybrid)"
            rec_reason = "Balanced strategy optimizes total GPA points while preventing acute cognitive burnout."

        result = {
            "query": query,
            "timelines": {
                "A": {
                    "title": "Timeline A: 100% Exam Cramming",
                    "action": "Dedicate the next 48 hours exclusively to Algorithms Midterm. Completely defer Assignment #2.",
                    "exam_score_projected": f"{exam_score_a}% (A Grade)",
                    "assignment_score_projected": f"{assign_score_a}% (-20% Late Deduction)",
                    "burnout_risk": f"{burnout_a}% (High Danger)",
                    "total_weighted_points": round(gpa_impact_a, 1),
                    "pros": ["Maximizes mastery of 40%-weight exam topics", "Deep continuous focus without context switching"],
                    "cons": ["Guaranteed late penalty on Database assignment", "Severe sleep debt causes brain fog on exam day"]
                },
                "B": {
                    "title": "Timeline B: Submit Assignment First",
                    "action": "Spend next 8 focus hours completing and submitting Assignment #2 on time, then begin exam revision.",
                    "exam_score_projected": f"{exam_score_b}% (B/B- Grade)",
                    "assignment_score_projected": f"{assign_score_b}% (Full Marks)",
                    "burnout_risk": f"{burnout_b}% (Low / Sustainable)",
                    "total_weighted_points": round(gpa_impact_b, 1),
                    "pros": ["15% coursework marks 100% secured with zero penalty", "Maintains healthy 7h sleep schedule"],
                    "cons": ["Only 6 hours left for 40%-weight midterm", "High stress during exam revision"]
                },
                "C": {
                    "title": "Timeline C: Recommended Dynamic Hybrid",
                    "action": "Timebox 4.5 hours tonight for 75% assignment completion (MVP submission), then shift 12 hours to high-yield exam modules.",
                    "exam_score_projected": f"{exam_score_c}% (A- / B+ Grade)",
                    "assignment_score_projected": f"{assign_score_c}% (Solid Submission)",
                    "burnout_risk": f"{burnout_c}% (Moderate)",
                    "total_weighted_points": round(gpa_impact_c, 1),
                    "pros": ["Yields the highest overall GPA points", "Protects biological sleep threshold before test"],
                    "cons": ["Requires strict discipline to stop working on assignment"]
                }
            },
            "recommended_choice": recommended_branch,
            "recommendation_rationale": rec_reason,
            "sacrifice_index": {
                "description": f"Choosing Timeline A over B yields a net difference of {net_tradeoff_delta:+} total course points.",
                "delta": net_tradeoff_delta
            },
            "active_permissions": self.privacy_permissions
        }
        return result

    # --- ADAPTIVE REINFORCEMENT LEARNING LOOP ---
    def record_feedback(self, chosen_timeline: str, user_notes: str = ""):
        old_bias = self.default_profile["high_stakes_bias"]
        old_risk = self.default_profile["risk_tolerance"]

        if chosen_timeline == "A":
            new_bias = min(0.98, old_bias + 0.12)
            new_risk = min(0.95, old_risk + 0.10)
            learned_message = f"Twin Brain Recalibrated: High-Stakes Exam Priority increased from {old_bias*100:.0f}% -> {new_bias*100:.0f}%. Risk Tolerance updated to {new_risk*100:.0f}%."
        elif chosen_timeline == "B":
            new_bias = max(0.40, old_bias - 0.12)
            new_risk = max(0.30, old_risk - 0.10)
            learned_message = f"Twin Brain Recalibrated: Prioritizing deadline certainty and zero late-penalties ({old_bias*100:.0f}% -> {new_bias*100:.0f}%)."
        else:
            new_bias = old_bias
            new_risk = old_risk
            learned_message = "Twin Brain Confirmed: Current balanced cognitive profile matches your preferred strategy."

        self.default_profile["high_stakes_bias"] = round(new_bias, 3)
        self.default_profile["risk_tolerance"] = round(new_risk, 3)

        event = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "chosen_timeline": chosen_timeline,
            "user_notes": user_notes,
            "adjustment": learned_message
        }
        self.decision_history.append(event)
        self.save_state()
        return learned_message

    def handle_emergency_extension(self, extension_hours: int = 48):
        idx = self.tasks[self.tasks["type"] == "Assignment"].index
        if len(idx) > 0:
            self.tasks.loc[idx, "due_in_hours"] += extension_hours
            return f"Course Correction Applied: Assignment deadline extended by +{extension_hours} hours. Late penalty risk has dropped to 0%!"
        return "No active assignment found to extend."
