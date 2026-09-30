import re

def update_frontend_components():
    with open("public/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Add demo OTP states and pattern filter state
    state_anchor = 'const [regCountdown, setRegCountdown] = useState(0);'
    new_states = '''const [regCountdown, setRegCountdown] = useState(0);
      const [regDemoOtp, setRegDemoOtp] = useState(null);
      const [forgotDemoOtp, setForgotDemoOtp] = useState(null);
      const [patternCategoryFilter, setPatternCategoryFilter] = useState("all");'''
    html = html.replace(state_anchor, new_states, 1)

    # 2. Add all missing functions right before `const checkSmtpStatus`
    func_anchor = 'const checkSmtpStatus = async () => {'
    new_functions = '''// ---------------- MISSING FUNCTIONS FIXED ----------------
      const handleAskFaq = (query) => {
        if (!query || !query.trim()) return;
        const userText = query.trim();
        const newMessages = [...chatMessages, { role: "user", content: userText }];
        setChatMessages(newMessages);
        setChatInput("");

        setTimeout(() => {
          const qLower = userText.toLowerCase();
          let reply = "";
          
          if (qLower.includes("what-if") || qLower.includes("what if")) {
            reply = "🔮 The What-If Flight Simulator projects parallel futures before you act! Ask dilemmas like 'What if I go to trip 3 days?' or 'What if I study all night?' and your Twin calculates projected exam readiness, fatigue, and provides transparent 'Why This?' explainability receipts.";
          } else if (qLower.includes("focus") || qLower.includes("telemetry") || qLower.includes("stamina")) {
            const minsToday = state?.study_telemetry?.total_focus_minutes_today || 0;
            const stamina = state?.study_telemetry?.stamina_score || 95;
            reply = `⏱️ Focus Mode tracks timed deep study sessions (25m - 90m). You earn +2 points per minute of verified focus! Today you have completed ${minsToday} focus minutes with a current stamina score of ${stamina}%.`;
          } else if (qLower.includes("proof") || qLower.includes("task") || qLower.includes("quiz")) {
            reply = "📸 Proof-Based Verification eliminates fake checkboxes! Upload your study notes or code (PDF, image, code) from your device, and solve a 3-question Teach-Back Quiz. Scoring >= 2/3 verifies your effort, earns points (+80 to +150 pts), and unlocks higher tiers.";
          } else if (qLower.includes("class") || qLower.includes("schedule") || qLower.includes("timetable")) {
            const numClasses = state?.classes?.length || 0;
            const numSubj = state?.subjects?.length || 0;
            reply = numClasses > 0
              ? `📅 You have ${numClasses} classes scheduled across ${numSubj} enrolled subjects this week. Check 'My Timetable & Subjects' in the sidebar for your room, faculty, and timings!`
              : "📅 Your timetable is not set up yet. Click 'My Timetable & Subjects' in the sidebar to add your college subjects and weekly class timings!";
          } else if (qLower.includes("grade") || qLower.includes("cgpa")) {
            reply = "📈 The Grades & CGPA Tracker computes your cumulative GPA on both the 10.0 and 4.0 scale, tracks subject-wise performance against your target percentage, and maintains an assessment history.";
          } else {
            reply = `👋 Scout AI here! TwinStudy tracks your personal study habits, simulates 'what-if' choices with explainability receipts, and verifies coursework with real evidence. Try asking about 'What-If simulator', 'Focus mode', or 'Proof verification'!`;
          }
          
          setChatMessages([...newMessages, { role: "assistant", content: reply }]);
        }, 300);
      };

      const handleSaveSmtp = async (e) => {
        if (e) e.preventDefault();
        if (!smtpSender.trim() || !smtpPass.trim()) {
          showNotification("⚠️ Please enter both your Gmail address and 16-character App Password.");
          return;
        }
        try {
          const res = await fetch("/api/auth/configure-smtp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              sender_email: smtpSender.trim(),
              sender_password: smtpPass.trim()
            })
          });
          const data = await res.json();
          if (res.ok) {
            showNotification("✓ Gmail SMTP credentials saved and verified successfully!");
            setSmtpStatus({ configured: true, sender_email: smtpSender.trim() });
          } else {
            showNotification(`⚠️ ${data.message || 'Failed to configure SMTP'}`);
          }
        } catch (err) {
          showNotification("Error saving SMTP credentials.");
        }
      };

      const handleResetTwinWeights = async () => {
        try {
          const res = await fetch("/api/twin/reset", { method: "POST" });
          const data = await res.json();
          if (res.ok) {
            showNotification("✓ Digital Twin reset to initial baseline weights.");
            await fetchTwinHealth();
          }
        } catch (e) {
          showNotification("Error resetting Twin.");
        }
      };

      const handleDeletePattern = async (patternId) => {
        try {
          const res = await fetch("/api/twin/pattern/delete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pattern_id: patternId })
          });
          const data = await res.json();
          if (res.ok) {
            showNotification("✓ Pattern archived from active simulation weighting.");
            await fetchTwinHealth();
          }
        } catch (e) {
          showNotification("Error deleting pattern.");
        }
      };

      const handleSaveCorrectPattern = async () => {
        if (!editingPattern) return;
        try {
          const res = await fetch("/api/twin/pattern/update", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(editingPattern)
          });
          const data = await res.json();
          if (res.ok) {
            showNotification("✓ Behavioral pattern updated successfully!");
            setShowCorrectPatternModal(false);
            setEditingPattern(null);
            await fetchTwinHealth();
          } else {
            showNotification(data.message || "Failed to update pattern.");
          }
        } catch (e) {
          showNotification("Error updating pattern.");
        }
      };

      const handleSubmitRealityFeedback = async () => {
        if (!feedbackDecision) return;
        try {
          const res = await fetch("/api/twin/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              decision_id: feedbackDecision.id,
              actual_outcome: feedbackOutcomeText,
              outcome_rating: feedbackRating,
              outcome_feedback: feedbackNotes
            })
          });
          const data = await res.json();
          if (res.ok) {
            showNotification("✓ Reality feedback logged! Prediction accuracy updated.");
            setShowFeedbackModal(false);
            setFeedbackDecision(null);
            await fetchTwinHealth();
          } else {
            showNotification(data.message || "Failed to log feedback.");
          }
        } catch (e) {
          showNotification("Error logging feedback.");
        }
      };

      const checkSmtpStatus = async () => {'''
    html = html.replace(func_anchor, new_functions, 1)

    # 3. In fetchState: Initialize settings state variables from active user and academic profile
    fetch_state_anchor = 'if (data.subjects) setSubjectsList(data.subjects);'
    fetch_state_inject = '''if (data.subjects) setSubjectsList(data.subjects);
          if (data.user) {
            if (data.user.name) setSettingsName(data.user.name);
            if (data.user.dob) setSettingsDob(data.user.dob);
            if (data.user.age) setSettingsAge(String(data.user.age));
            if (data.user.daily_study_hours) setSettingsHours(String(data.user.daily_study_hours));
          }
          if (data.academic_profile) {
            if (data.academic_profile.student_name) setSettingsName(data.academic_profile.student_name);
            if (data.academic_profile.course) setSettingsCourse(data.academic_profile.course);
            if (data.academic_profile.semester) setSettingsSemester(data.academic_profile.semester);
            if (data.academic_profile.college) setSettingsCollege(data.academic_profile.college);
          }
          if (data.parent_controls && data.parent_controls.guardian_email) {
            setSettingsGuardianEmail(data.parent_controls.guardian_email);
          }'''
    html = html.replace(fetch_state_anchor, fetch_state_inject, 1)

    # 4. In handleSendRegisterOtp & handleSendForgotOtp: handle demo_code
    send_otp_handle_old = '''if (res.ok) {
            setRegOtpSent(true);
            setRegCountdown(60);
            setAuthSuccess(data.message);
            showNotification(`Verification code dispatched to ${regEmail}!`);
          }'''
    send_otp_handle_new = '''if (res.ok) {
            setRegOtpSent(true);
            setRegCountdown(60);
            setAuthSuccess(data.message);
            if (data.demo_code) {
              setRegDemoOtp(data.demo_code);
              setRegOtp(data.demo_code);
            }
            showNotification(`Verification code dispatched to ${regEmail}!`);
          }'''
    html = html.replace(send_otp_handle_old, send_otp_handle_new, 1)

    forgot_otp_handle_old = '''if (res.ok) {
            setForgotOtpSent(true);
            setAuthSuccess(data.message);
            showNotification(`Password reset code sent to ${forgotEmail}`);
          }'''
    forgot_otp_handle_new = '''if (res.ok) {
            setForgotOtpSent(true);
            setAuthSuccess(data.message);
            if (data.demo_code) {
              setForgotDemoOtp(data.demo_code);
              setForgotOtp(data.demo_code);
            }
            showNotification(`Password reset code dispatched to ${forgotEmail}`);
          }'''
    html = html.replace(forgot_otp_handle_old, forgot_otp_handle_new, 1)

    # 5. In handleLogin: Ensure strict empty-field check so empty clicks cannot enter
    login_func_old = '''const handleLogin = async (e) => {
        if (e) e.preventDefault();
        setAuthError(null);
        setAuthSuccess(null);

        if (!loginIdentifier.trim()) return setAuthError("Please enter your registered email address.");
        if (!loginPassword) return setAuthError("Please enter your password.");'''

    login_func_new = '''const handleLogin = async (e) => {
        if (e) e.preventDefault();
        setAuthError(null);
        setAuthSuccess(null);

        const cleanEmail = (loginIdentifier || "").trim();
        const cleanPass = (loginPassword || "").trim();

        if (!cleanEmail) {
          setAuthError("Please enter your registered email address.");
          return;
        }
        if (!cleanPass) {
          setAuthError("Please enter your account password.");
          return;
        }'''
    html = html.replace(login_func_old, login_func_new, 1)

    # 6. Inject Demo OTP Autofill Card in Register Form UI
    reg_otp_ui_anchor = '{regOtpSent && ('
    reg_otp_ui_inject = '''{regOtpSent && (
                      <div className="space-y-3">
                        {regDemoOtp && (
                          <div className="p-3.5 rounded-2xl bg-cyanAccent/15 border-2 border-cyanAccent shadow-sm space-y-1.5">
                            <div className="flex justify-between items-center text-xs">
                              <span className="font-extrabold text-navySlate flex items-center gap-1.5">
                                <span>📬</span> Email Verification Code
                              </span>
                              <span className="text-[10px] text-cyanHover font-mono font-bold">Hackathon Dispatch</span>
                            </div>
                            <p className="text-xs text-navySlate font-medium">
                              Verification code for <strong>{regEmail}</strong> is: <strong className="font-mono text-base text-navySlate bg-white px-2 py-0.5 rounded border border-cyanAccent tracking-widest">{regDemoOtp}</strong>
                            </p>
                            <button
                              type="button"
                              onClick={() => setRegOtp(regDemoOtp)}
                              className="text-[11px] font-extrabold text-cyanHover hover:underline flex items-center gap-1"
                            >
                              <span>⚡</span> Tap to Auto-Fill Code ({regDemoOtp})
                            </button>
                          </div>
                        )}'''
    html = html.replace('{regOtpSent && (\n                      <div className="p-4 rounded-2xl bg-cyanAccent/10 border-2 border-cyanAccent/50 space-y-3">', reg_otp_ui_inject + '\n                        <div className="p-4 rounded-2xl bg-cyanAccent/10 border-2 border-cyanAccent/50 space-y-3">', 1)

    # 7. Add patternCategoryFilter toolbar in Twin Learning Engine
    pattern_list_old = '''<div className="space-y-3">
                          {behaviorPatterns.map((p) => ('''
    pattern_list_new = '''<div className="flex flex-wrap gap-2 pt-1 border-t border-navySlate/10 text-xs font-bold">
                          {[
                            { id: "all", label: `All (${behaviorPatterns.length})` },
                            { id: "productivity", label: "Productivity" },
                            { id: "prioritization", label: "Prioritization" },
                            { id: "deadline_habit", label: "Deadline Habit" },
                            { id: "fatigue", label: "Fatigue" }
                          ].map(tab => (
                            <button
                              key={tab.id}
                              type="button"
                              onClick={() => setPatternCategoryFilter(tab.id)}
                              className={`px-3 py-1.5 rounded-xl border transition ${patternCategoryFilter === tab.id ? 'bg-navySlate text-white border-navySlate shadow-sm' : 'bg-white text-navySlate/70 border-navySlate/20 hover:border-cyanAccent'}`}
                            >
                              {tab.label}
                            </button>
                          ))}
                        </div>

                        <div className="space-y-3">
                          {behaviorPatterns
                            .filter(p => patternCategoryFilter === "all" || p.pattern_type === patternCategoryFilter)
                            .map((p) => ('''
    html = html.replace(pattern_list_old, pattern_list_new, 1)

    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] public/index.html updated with missing functions, chatbot handler, settings, and twin toolbar")

update_frontend_components()
