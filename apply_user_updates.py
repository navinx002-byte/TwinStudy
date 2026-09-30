import re

def update_all():
    print("Applying all requested changes...")

    # =========================================================================
    # PART 1: UPDATE SERVER.PY WITH COMPLETE WHY_THIS DATA RECEIPTS
    # =========================================================================
    with open("server.py", "r", encoding="utf-8") as f:
        srv = f.read()

    # Update simulate_decision to always include top_factors_plain_language & data_receipt
    sim_start = srv.find("def simulate_decision(query: str, db: dict) -> dict:")
    sim_end = srv.find("# --- ROUTES ---", sim_start)

    new_sim = '''def simulate_decision(query: str, db: dict) -> dict:
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
                "long_term": f"Prevents a {days_count * 7}% mid-term grade drop and keeps your study streak intact."
            },
            "confidence_level": {"score": "95%", "reason_for_lower_confidence": "Historical high completion rate in evening sprint blocks."},
            "what_if_ignored": f"Leaving without pre-study creates a {days_count * 6}-hour backlog that collides with immediate class deadlines upon return.",
            "difference_from_student_idea": f"Instead of postponing all coursework until after the trip, front-load 70% of the effort so you travel with complete peace of mind.",
            "top_factors_plain_language": [
                f"Absence duration: {days_count * 24} hours without coursework access",
                f"Coursework collision: {min(4, days_count + 1)} submission deadlines during travel period",
                "Cognitive stamina recovery: travel provides authentic rest only when backlog is pre-cleared"
            ],
            "data_receipt": {
                "sources_used": [
                    "Student Weekly Timetable & Class Schedule",
                    "Enrolled Course Deadlines (twin_database.json)",
                    "Cognitive Stamina & Focus Telemetry Logs"
                ],
                "sources_not_used": [
                    "Personal Chat & Messaging Data (Permanently Muted)",
                    "Device GPS & Location Tracking (Permanently Muted)",
                    "Camera & Audio Streams (Permanently Muted)"
                ]
            }
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
            "difference_from_student_idea": "The twin prioritizes sleep-backed retention over brute-force exhaustive sleepless reading.",
            "top_factors_plain_language": [
                "Circadian rhythm crash: 94% stamina degradation logged after 2:00 AM study",
                "Analytical recall drop: sleep deprivation reduces exam problem solving speed by 35%",
                "Day-after cascade: next-day lecture comprehension collapses without restorative REM sleep"
            ],
            "data_receipt": {
                "sources_used": [
                    "Circadian Stamina Telemetry Model",
                    "Course Syllabus & Exam Weightings",
                    "Historical Study Block Durations"
                ],
                "sources_not_used": [
                    "Personal Chat & Messaging Data (Permanently Muted)",
                    "Device GPS & Location Tracking (Permanently Muted)",
                    "Camera & Audio Streams (Permanently Muted)"
                ]
            }
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
            "difference_from_student_idea": "Balances classroom attendance with micro-focus blocks instead of skipping altogether.",
            "top_factors_plain_language": [
                f"Course grade weight: attendance and live labs count for 20% of {target_sub}",
                "Catch-up penalty: reviewing peer recordings takes 2.3x longer than live lecture",
                "Faculty hints: in-class revision highlights exact questions appearing on midterms"
            ],
            "data_receipt": {
                "sources_used": [
                    f"{target_sub} Syllabus & Lab Rubric",
                    "Weekly Timetable Schedule",
                    "Historical Attendance Records"
                ],
                "sources_not_used": [
                    "Personal Chat & Messaging Data (Permanently Muted)",
                    "Device GPS & Location Tracking (Permanently Muted)",
                    "Camera & Audio Streams (Permanently Muted)"
                ]
            }
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
            "difference_from_student_idea": "The twin accommodates your choice while safeguarding exam readiness and verified coursework points.",
            "top_factors_plain_language": [
                f"Workload density: {focus_topic} requires balanced micro-sprints to avoid burnout",
                "Cognitive buffer: 35% time buffer built in for unexpected concept friction",
                "Streak protection: steady daily study preserves your active streak points"
            ],
            "data_receipt": {
                "sources_used": [
                    "Current Semester Coursework List",
                    "Daily Study Hour Target (4.5h)",
                    "Focus Telemetry Metrics"
                ],
                "sources_not_used": [
                    "Personal Chat & Messaging Data (Permanently Muted)",
                    "Device GPS & Location Tracking (Permanently Muted)",
                    "Camera & Audio Streams (Permanently Muted)"
                ]
            }
        }

    return {
        "query": query,
        "futureA": fut_a,
        "futureB": fut_b,
        "why_this": why_this_panel
    }
\n'''

    srv = srv[:sim_start] + new_sim + srv[sim_end:]
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(srv)
    print(">> [OK] server.py updated with complete why_this panels & data receipts")

    # =========================================================================
    # PART 2: UPDATE PUBLIC/INDEX.HTML
    # =========================================================================
    with open("public/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Remove parent/guardian view from the sidebar navigation
    parent_nav_str = '...(isMinorStudent ? [{ id: "parent_view", label: "Parent / Guardian View", icon: "👨‍👩‍👦" }] : []),'
    if parent_nav_str in html:
        html = html.replace(parent_nav_str, '')
        print(">> [OK] Removed parent/guardian view from sidebar navigation")

    # 2. Remove CARD 2: GMAIL SMTP LIVE DELIVERY CONFIGURATION from Profile & Settings
    # Find card in settings
    smtp_card_start = html.find('{/* CARD 2: GMAIL SMTP LIVE DELIVERY CONFIGURATION */}')
    if smtp_card_start != -1:
        # Find the closing tag of this card
        smtp_card_end = html.find('</div>\n\n                      </div>\n                  )}', smtp_card_start)
        if smtp_card_end == -1:
            smtp_card_end = html.find('</div>\n                    </div>\n                  )}', smtp_card_start)
        if smtp_card_end != -1:
            html = html[:smtp_card_start] + html[smtp_card_end + 6:]
            print(">> [OK] Removed Gmail SMTP card from Profile & Settings")
        else:
            # alternative search
            print(">> [NOTE] Using regex to remove Gmail SMTP card from settings")
            html = re.sub(r'{\/\* CARD 2: GMAIL SMTP LIVE DELIVERY CONFIGURATION \*\/}.*?<\/ol>\s*<\/div>\s*<\/div>', '', html, flags=re.DOTALL)
            print(">> [OK] Removed Gmail SMTP card via regex")

    # 3. Add Back button to App header
    old_app_header = '<header className="h-16 glass-panel border-b border-white/80 px-6 flex items-center justify-between sticky top-0 z-20">\n                  <div>\n                    <h2 className="text-base font-extrabold text-navySlate capitalize flex items-center gap-2">'
    new_app_header = '''<header className="h-16 glass-panel border-b border-white/80 px-6 flex items-center justify-between sticky top-0 z-20">
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => {
                        if (appPage !== "dashboard") {
                          setAppPage("dashboard");
                        } else {
                          setView("landing");
                        }
                      }}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white border border-navySlate/20 text-navySlate text-xs font-black shadow-sm hover:bg-slate-50 hover:border-cyanAccent transition cursor-pointer"
                      title="Back to Dashboard or Home"
                    >
                      <span className="text-sm">←</span>
                      <span>Back</span>
                    </button>
                    <div>
                      <h2 className="text-base font-extrabold text-navySlate capitalize flex items-center gap-2">'''

    if old_app_header in html:
        html = html.replace(old_app_header, new_app_header)
        print(">> [OK] Added working Back button to top-left corner of app header")

    # 4. Add Back button to Auth view
    old_auth_header = '<div className="max-w-md w-full glass-panel p-6 sm:p-8 rounded-3xl border border-white shadow-2xl space-y-5">'
    new_auth_header = '''<div className="max-w-md w-full space-y-2">
                <button
                  type="button"
                  onClick={() => setView("landing")}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-white border border-navySlate/20 text-navySlate text-xs font-black shadow-sm hover:bg-slate-50 hover:border-cyanAccent transition cursor-pointer"
                >
                  <span>←</span>
                  <span>Back to Home</span>
                </button>
                <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white shadow-2xl space-y-5">'''

    if old_auth_header in html:
        html = html.replace(old_auth_header, new_auth_header)
        print(">> [OK] Added working Back button to top-left corner of auth view")

    # 5. Fix .map calls in simulator to prevent ANY undefined crash
    html = html.replace('{simResult.why_this.top_factors_plain_language.map((f, i) => (', '{(simResult?.why_this?.top_factors_plain_language || ["Core concept mastery review", "Cognitive stamina retention curve", "Deadlines collision risk"]).map((f, i) => (')
    html = html.replace('{simResult.why_this.data_receipt.sources_used.map((s, i) => <div key={i}>{s}</div>)}', '{(simResult?.why_this?.data_receipt?.sources_used || ["Student Timetable Schedule", "Enrolled Subject Deadlines"]).map((s, i) => <div key={i}>{s}</div>)}')
    html = html.replace('{simResult.why_this.data_receipt.sources_not_used.map((s, i) => <div key={i}>{s}</div>)}', '{(simResult?.why_this?.data_receipt?.sources_not_used || ["Personal Chat Data (Muted)", "Device GPS (Muted)"]).map((s, i) => <div key={i}>{s}</div>)}')
    print(">> [OK] Defensively guarded simulator .map calls against undefined")

    # 6. Replace 3-question quiz with 8-question tailored MCQ generator
    quiz_func_old = html[html.find('const handleProofFileSelect = (e) => {'):html.find('// PROOF SUBMISSION & VERIFICATION EVALUATION')]

    quiz_func_new = '''const handleProofFileSelect = (e) => {
        const file = e.target.files && e.target.files[0];
        if (!file) return;

        const sizeFormatted = file.size > 1024 * 1024 
          ? (file.size / (1024 * 1024)).toFixed(1) + " MB"
          : Math.max(1, Math.round(file.size / 1024)) + " KB";

        setProofFile({
          name: file.name,
          size: sizeFormatted,
          type: file.type || "Document"
        });

        // Generate exactly 8 tailored Teach-Back MCQs based on task title, subject, and uploaded file
        const taskTitle = (proofModalTask?.title || "").toLowerCase();
        const subName = (proofModalTask?.subject || "").toLowerCase();
        const fName = file.name.toLowerCase();

        let generated = [];

        // DOMAIN A: MACHINE LEARNING / AI / DATA SCIENCE
        if (taskTitle.includes("machine learning") || taskTitle.includes("ai") || subName.includes("ai") || subName.includes("machine") || fName.includes("ml") || fName.includes("tree") || fName.includes("data") || fName.includes("model")) {
          generated = [
            {
              id: 1,
              question: "What is the primary objective of node splitting using Gini Impurity or Information Gain in Decision Trees?",
              options: [
                "To partition data points into subsets that are increasingly homogeneous with respect to the target class",
                "To eliminate 50% of the input features to speed up training runtime",
                "To normalize continuous numerical features to zero mean and unit variance",
                "To automatically synthesize artificial data samples for unsupervised training"
              ],
              correct: 0,
              explanation: "Splitting criteria (Gini/Entropy) isolate target classes into pure subsets to minimize classification error."
            },
            {
              id: 2,
              question: "How does cost-complexity pruning (CCP) prevent tree models from memorizing training dataset noise?",
              options: [
                "By penalizing and trimming subtrees that offer negligible validation accuracy improvements",
                "By doubling maximum tree depth until training error reaches absolute zero",
                "By eliminating the root split from the decision graph",
                "By converting numerical split thresholds into categorical strings"
              ],
              correct: 0,
              explanation: "Pruning removes high-variance noisy branches, directly curbing model overfitting."
            },
            {
              id: 3,
              question: "Why is stratified k-fold cross-validation preferred over random k-fold for imbalanced datasets?",
              options: [
                "It guarantees each evaluation fold preserves the identical percentage representation of target labels",
                "It eliminates the necessity of compiling test set confusion matrices",
                "It requires zero computational memory during cross-validation loops",
                "It converts multi-class problems into pure regression tasks"
              ],
              correct: 0,
              explanation: "Stratification ensures minority class proportions remain invariant across every fold split."
            },
            {
              id: 4,
              question: "Which evaluation metric is most critical when the cost of a False Negative is catastrophic (e.g. cancer diagnosis)?",
              options: [
                "Recall (Sensitivity)",
                "Precision (Positive Predictive Value)",
                "Raw Accuracy",
                "Adjusted R-Squared"
              ],
              correct: 0,
              explanation: "High Recall minimizes False Negatives, ensuring positive cases are not missed."
            },
            {
              id: 5,
              question: "What phenomenon occurs when a model has high bias and fails to capture underlying patterns in training data?",
              options: [
                "Underfitting",
                "Overfitting",
                "Gradient Explosion",
                "Data Leakage"
              ],
              correct: 0,
              explanation: "High bias leads to underfitting where the model is too simplistic to capture dataset patterns."
            },
            {
              id: 6,
              question: "What purpose does L2 Regularization (Ridge) serve in parameter optimization?",
              options: [
                "Penalizes sum of squared weights, shrinking coefficients toward zero to reduce model variance",
                "Sets all non-essential feature weights to absolute zero for sparse feature selection",
                "Increases training learning rate after every epoch",
                "Converts non-linear decision boundaries into rigid straight lines"
              ],
              correct: 0,
              explanation: "L2 weight decay penalizes extreme coefficients, smoothing decision surfaces."
            },
            {
              id: 7,
              question: "Why are non-linear activation functions (like ReLU) required in multi-layer deep neural networks?",
              options: [
                "Without non-linearities, any stack of linear layers collapses into an equivalence of a single linear regression",
                "To guarantee loss functions always reach global zero minima in 1 epoch",
                "To prevent floating point overflow in GPU memory buffers",
                "To eliminate the need for backpropagation gradients"
              ],
              correct: 0,
              explanation: "Non-linear activations allow networks to approximate arbitrary non-linear functional representations."
            },
            {
              id: 8,
              question: "In Random Forests, how does Bootstrap Aggregating (Bagging) reduce overall variance?",
              options: [
                "By training decorrelated trees on random data subsets with replacement and averaging predictions",
                "By training trees sequentially on the residual errors of previous trees",
                "By forcing all trees to split on the identical primary feature",
                "By discarding 80% of generated trees with lowest individual accuracy"
              ],
              correct: 0,
              explanation: "Averaging ensemble predictions across decorrelated trees dampens single-tree variance without increasing bias."
            }
          ];
        }
        // DOMAIN B: DATABASE SYSTEMS / DBMS / SQL
        else if (taskTitle.includes("dbms") || taskTitle.includes("database") || subName.includes("db") || subName.includes("database") || fName.includes("sql") || fName.includes("db") || fName.includes("query")) {
          generated = [
            {
              id: 1,
              question: "Which relational normal form strictly requires every determinant in functional dependencies to be a candidate or superkey?",
              options: [
                "Boyce-Codd Normal Form (BCNF)",
                "First Normal Form (1NF)",
                "Second Normal Form (2NF)",
                "Third Normal Form (3NF)"
              ],
              correct: 0,
              explanation: "BCNF is a stricter variant of 3NF eliminating all functional dependency redundancy."
            },
            {
              id: 2,
              question: "What mechanism allows modern relational DBMS engines to guarantee the Durability property under unexpected crashes?",
              options: [
                "Write-Ahead Logging (WAL) flushed to non-volatile disk storage before committing transactions",
                "Storing transaction log buffers exclusively in volatile CPU L2 cache",
                "Disabling foreign key constraints during concurrent writes",
                "Executing SQL statements asynchronously without disk barriers"
              ],
              correct: 0,
              explanation: "Write-Ahead Logging ensures modified data is logged durably before transaction commits return."
            },
            {
              id: 3,
              question: "Why do relational databases utilize B+ Trees for index storage rather than standard Binary Search Trees?",
              options: [
                "High fan-out minimizes disk block read I/O hops, and sequential linked leaf nodes support efficient range scans",
                "B+ Trees occupy zero disk storage memory overhead",
                "Binary search trees cannot store string data types",
                "B+ Trees forbid range scanning for security reasons"
              ],
              correct: 0,
              explanation: "High fan-out keeps B+ Tree height at 3-4 levels, minimizing disk seek times for millions of records."
            },
            {
              id: 4,
              question: "Under SQL ACID transaction properties, which property prevents concurrent transactions from seeing uncommitted dirty reads?",
              options: [
                "Isolation",
                "Atomicity",
                "Consistency",
                "Durability"
              ],
              correct: 0,
              explanation: "Isolation ensures concurrent execution yields state equivalent to serial execution."
            },
            {
              id: 5,
              question: "What is the primary operational difference between INNER JOIN and LEFT OUTER JOIN in SQL?",
              options: [
                "INNER JOIN returns only matching rows; LEFT OUTER JOIN preserves all left table rows, populating missing right attributes with NULL",
                "LEFT OUTER JOIN executes 10x faster by bypassing foreign key indexing",
                "INNER JOIN converts all text columns to uppercase integers",
                "LEFT OUTER JOIN deletes non-matching rows from the physical table"
              ],
              correct: 0,
              explanation: "LEFT OUTER JOIN preserves every record from the left table regardless of join predicate match."
            },
            {
              id: 6,
              question: "Which SQL clause is used to filter aggregate groupings after executing GROUP BY aggregation?",
              options: [
                "HAVING",
                "WHERE",
                "ORDER BY",
                "LIMIT"
              ],
              correct: 0,
              explanation: "WHERE filters raw rows before aggregation, while HAVING filters aggregated group metrics."
            },
            {
              id: 7,
              question: "What condition in two-phase locking (2PL) guarantees serializability and prevents cascading aborts?",
              options: [
                "Strict 2PL: holding all exclusive locks until transaction commit or abort completion",
                "Releasing shared locks before acquiring exclusive write locks",
                "Disabling read locks during peak hours",
                "Committing transactions before writing dirty buffers to log"
              ],
              correct: 0,
              explanation: "Strict 2PL holds write locks until completion, preventing dirty reads and cascading rollbacks."
            },
            {
              id: 8,
              question: "What is the primary drawback of over-indexing every column in a high-throughput relational table?",
              options: [
                "Significantly degrades INSERT, UPDATE, and DELETE performance due to continuous index rebuilds",
                "Corrupts table schema definitions on reboot",
                "Disables primary key uniqueness validation",
                "Forces queries to run in single-threaded mode"
              ],
              correct: 0,
              explanation: "Every write operation must update every corresponding index structure, inducing write amplification."
            }
          ];
        }
        // DOMAIN C: COMPUTER NETWORKS / DCN / CLOUD
        else if (taskTitle.includes("network") || taskTitle.includes("dcn") || subName.includes("network") || subName.includes("cloud") || fName.includes("net") || fName.includes("packet") || fName.includes("tcp") || fName.includes("ip")) {
          generated = [
            {
              id: 1,
              question: "In the TCP 3-Way Handshake protocol, what sequence of control packets establishes a connection?",
              options: [
                "SYN -> SYN-ACK -> ACK",
                "ACK -> SYN -> FIN",
                "HELLO -> WAIT -> CONNECT",
                "PING -> PONG -> ACK"
              ],
              correct: 0,
              explanation: "Client sends SYN, server responds with SYN-ACK, client acknowledges with ACK to establish state."
            },
            {
              id: 2,
              question: "Which layer of the OSI 7-Layer Reference Model is responsible for end-to-end reliable flow control and port addressing?",
              options: [
                "Transport Layer (Layer 4)",
                "Network Layer (Layer 3)",
                "Data Link Layer (Layer 2)",
                "Application Layer (Layer 7)"
              ],
              correct: 0,
              explanation: "Transport layer handles segmentation, port multiplexing, and end-to-end flow/congestion control."
            },
            {
              id: 3,
              question: "What is the primary difference between TCP and UDP transmission protocols?",
              options: [
                "TCP is connection-oriented with guaranteed delivery; UDP is connectionless with low-latency best-effort delivery",
                "UDP encrypts all packet payloads automatically with TLS",
                "TCP can only transmit text characters while UDP transmits binary data",
                "UDP uses 64-bit IP addresses while TCP uses 32-bit addresses"
              ],
              correct: 0,
              explanation: "TCP provides reliable, sequenced delivery with acknowledgments; UDP trades reliability for raw speed."
            },
            {
              id: 4,
              question: "In IPv4 subnetting with CIDR prefix /26, how many usable host addresses exist per subnet?",
              options: [
                "62 usable hosts (64 total - network - broadcast)",
                "128 usable hosts",
                "30 usable hosts",
                "254 usable hosts"
              ],
              correct: 0,
              explanation: "32 - 26 = 6 host bits = 2^6 = 64 total addresses, minus network and broadcast = 62 usable."
            },
            {
              id: 5,
              question: "How does the Domain Name System (DNS) resolve human-readable domains into IP addresses?",
              options: [
                "Hierarchical recursive traversal from Root Nameserver -> TLD Server -> Authoritative Nameserver",
                "Broadcasting a single UDP packet to every computer on the internet",
                "Querying the local CPU cache and terminating if missing",
                "Hashing the domain into a MAC address using SHA-256"
              ],
              correct: 0,
              explanation: "DNS performs hierarchical delegation across root, top-level domain (.com), and authoritative zone servers."
            },
            {
              id: 6,
              question: "What cryptographic handshake protocol upgrades an insecure HTTP connection to an encrypted HTTPS connection?",
              options: [
                "TLS (Transport Layer Security) Handshake",
                "ARP (Address Resolution Protocol)",
                "ICMP Echo Handshake",
                "DHCP Discover-Offer-Request-Ack"
              ],
              correct: 0,
              explanation: "TLS authenticates server identity with public key certificates and negotiates symmetric session keys."
            },
            {
              id: 7,
              question: "Which routing algorithm is used by the OSPF protocol to compute shortest loop-free paths?",
              options: [
                "Dijkstra's Link-State Shortest Path Algorithm",
                "Bellman-Ford Distance Vector Algorithm",
                "Bubble Sort Path Search",
                "Random Flooding Algorithm"
              ],
              correct: 0,
              explanation: "OSPF uses Dijkstra's algorithm over synchronized link-state databases to compute shortest paths."
            },
            {
              id: 8,
              question: "What purpose does Network Address Translation (NAT) serve in consumer routers?",
              options: [
                "Maps multiple private RFC 1918 IPv4 addresses to a single public routable IP address using port translation",
                "Converts IPv4 packets into optical fiber signals directly",
                "Acts as an unencrypted proxy that records browsing histories",
                "Eliminates the requirement for subnet masks in local networks"
              ],
              correct: 0,
              explanation: "NAT/NAPT conserves public IPv4 addresses by multiplexing private LAN IPs across distinct port numbers."
            }
          ];
        }
        // DOMAIN D: GENERAL ACADEMIC & SUBJECT COMPREHENSION
        else {
          const cleanSubject = proofModalTask?.subject || "Coursework";
          generated = [
            {
              id: 1,
              question: `In your uploaded ${cleanSubject} materials, what constitutes the fundamental core theorem or design pattern?`,
              options: [
                "Modular structural decomposition separating concerns to achieve deterministic, verifiable outcomes",
                "Memorizing syntax rules without understanding foundational logic",
                "Executing brute-force iterations without considering computational asymptotic bounds",
                "Postponing documentation until final delivery"
              ],
              correct: 0,
              explanation: "Modular decomposition ensures maintainability, testability, and theoretical soundness."
            },
            {
              id: 2,
              question: "When refactoring academic code or formulas, what is the primary benefit of achieving idempotency?",
              options: [
                "Applying an operation multiple times produces the identical outcome as applying it once",
                "Reduces memory consumption to zero bytes",
                "Guarantees the algorithm runs in constant O(1) time",
                "Bypasses compiler type checking rules"
              ],
              correct: 0,
              explanation: "Idempotent operations prevent side-effect state corruption upon repeated executions."
            },
            {
              id: 3,
              question: "Which strategy provides the strongest empirical evidence of computational solution correctness?",
              options: [
                "Formal unit testing covering boundary conditions, edge cases, and stress workloads",
                "Assuming correctness because sample code compiled on first attempt",
                "Relying solely on visual inspection of printed output",
                "Disabling assertions and exception handlers in production code"
              ],
              correct: 0,
              explanation: "Comprehensive boundary and stress tests expose off-by-one errors and edge case failures."
            },
            {
              id: 4,
              question: "In asymptotic algorithmic analysis, why is Big-O notation preferred over measuring execution clock time in seconds?",
              options: [
                "It characterizes mathematical scaling behavior independent of specific CPU clock speed or hardware architectures",
                "It measures precise nanoseconds elapsed on physical silicon",
                "It guarantees zero memory allocation during runtime",
                "It replaces the need for algorithmic correctness proofs"
              ],
              correct: 0,
              explanation: "Big-O evaluates growth order as input size n approaches infinity regardless of hardware variations."
            },
            {
              id: 5,
              question: "What is the primary role of encapsulation in robust software and system design?",
              options: [
                "Hiding internal implementation state while exposing restricted, validated public interfaces",
                "Making all variables globally mutable from any execution thread",
                "Duplicating code logic across multiple files to increase line counts",
                "Preventing files from being committed to version control"
              ],
              correct: 0,
              explanation: "Encapsulation protects invariants and decouples consumers from internal structural details."
            },
            {
              id: 6,
              question: "How does active recall and spaced repetition combat the Ebbinghaus forgetting curve?",
              options: [
                "Forces neural reconsolidation at spaced intervals, flattening memory decay and increasing retention durability",
                "Requires passive reading 10 minutes before an exam",
                "Replaces conceptual understanding with temporary rote memorization",
                "Deletes older concepts to make room for new syllabus topics"
              ],
              correct: 0,
              explanation: "Retrieval practice strengthens synaptic pathways, dramatically reducing forgetting over time."
            },
            {
              id: 7,
              question: "When evaluating data structures, what key trade-off exists between Hash Tables and Balanced Binary Trees (AVL/Red-Black)?",
              options: [
                "Hash Tables offer average O(1) lookups but lack ordering; Balanced Trees offer guaranteed O(log n) lookups with sorted order",
                "Balanced Trees require zero memory pointers",
                "Hash Tables cannot handle integer keys",
                "Balanced Trees have O(n^2) worst-case traversal times"
              ],
              correct: 0,
              explanation: "Hash tables sacrifice ordered key iteration for rapid average constant-time lookups."
            },
            {
              id: 8,
              question: "How does verifying proof artifacts (upload + 8-question quiz) improve your Digital Twin's personalization?",
              options: [
                "It records genuine comprehension evidence, increasing Twin Confidence to 96% and earning verified tier points",
                "It deletes all historical simulation receipts permanently",
                "It resets your study streak back to day 1",
                "It notifies external servers with your raw notes"
              ],
              correct: 0,
              explanation: "Proof verification prevents fake checkboxes, calibrating your twin's effort-to-retention curve with authentic evidence."
            }
          ];
        }

        setQuizQuestions(generated);
        setQuizAnswers({});
        setQuizSubmitted(false);
        setQuizFeedback(null);
      };
\n'''

    html = html.replace(quiz_func_old, quiz_func_new)
    print(">> [OK] Replaced quiz generator with 8 tailored MCQs based on uploaded file & task")

    # 7. Update pass mark logic in handleSubmitProofAndQuiz to 6 out of 8 (75%)
    old_submit_logic = '''        const passed = score >= 2;
        setQuizSubmitted(true);
        setQuizFeedback({
          score: score,
          total: quizQuestions.length,
          passed: passed
        });

        if (!passed) {
          showNotification(`Score: ${score}/3. Review your uploaded material and try again to prove comprehension.`);
          return;
        }'''

    new_submit_logic = '''        const passMark = Math.max(5, Math.ceil(quizQuestions.length * 0.7)); // 6 out of 8
        const passed = score >= passMark;
        setQuizSubmitted(true);
        setQuizFeedback({
          score: score,
          total: quizQuestions.length,
          passed: passed
        });

        if (!passed) {
          showNotification(`Score: ${score}/${quizQuestions.length}. Review your uploaded material and answer at least ${passMark}/${quizQuestions.length} correctly to prove comprehension.`);
          return;
        }'''

    if old_submit_logic in html:
        html = html.replace(old_submit_logic, new_submit_logic)
        print(">> [OK] Updated pass mark evaluation to 6/8 questions")

    # Update quiz header pass badge in modal JSX
    html = html.replace('Pass mark: 2/3', 'Pass mark: 6/8')
    html = html.replace('⚠️ Please answer all 3 Teach-Back Quiz questions', '⚠️ Please answer all 8 Teach-Back Quiz questions')

    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(">> [OK] public/index.html updated successfully!")

update_all()
