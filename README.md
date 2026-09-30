# TwinStudy AI: The Cognitive Student Digital Twin & Flight Simulator

An intelligent, sovereign AI-powered digital twin designed for student productivity, proactive decision-making, and academic governance. TwinStudy continuously models study patterns, simulates multi-branch "what-if" academic dilemmas, verifies real effort with proof-based teach-back assessments, and provides parental oversight with strict data privacy controls.

---

## 🌟 Key Architecture & Features

1. **🔮 Multi-Branch What-If Decision Simulator**:
   - Analyzes real course timetables, impending deadlines, and historical study telemetry.
   - Compares alternative futures (e.g., *Cram for High-Weight Exam* vs. *Submit Assignment on Time* vs. *AI Hybrid Compromise*).
   - Generates quantitative projections: net GPA impact, burnout risks, late penalties, and behavioral recommendations.

2. **📸 Proof-Based Real Effort Verification (No Fake Checkboxes)**:
   - Replaces unverified checkboxes with tangible academic proof (handwritten notes, code commit URLs, lab calculations).
   - Generates contextual 8-question teach-back quizzes evaluated by AI with instant feedback and score certificates.
   - Awards verifiable effort points (+100 pts) and extends study streaks.

3. **👨‍👩‍👧 Minor Student Transparency & Guardian Dashboard**:
   - Secure parent/guardian monitoring dashboard.
   - Live telemetry: weekly verified study hours, syllabus completion, risk alerts, and emergency nudge dispatch.
   - Sovereign permission controls allowing students to govern access to specific personal data streams.

4. **⚡ Focus Cockpit & Cognitive Telemetry**:
   - Interactive Pomodoro & deep work telemetry tracker.
   - Real-time cognitive stamina monitoring and session analytics.

5. **🤖 Study Buddy Interactive Assistant**:
   - Context-aware chatbot trained on the student's actual enrolled subjects, assignments, and calendar constraints.

---

## 🚀 Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the full-stack server
python server.py
```

Open your browser at **[http://localhost:5000](http://localhost:5000)**.

---

## ☁️ Deploying to Vercel

This repository is pre-configured with `vercel.json` and `api/index.py` for direct Vercel serverless deployment.

1. Connect your GitHub repository `navinx002-byte/TwinStudy` to [Vercel](https://vercel.com/new).
2. Click **Deploy**.
3. Vercel automatically deploys the frontend and the Python serverless API functions.
