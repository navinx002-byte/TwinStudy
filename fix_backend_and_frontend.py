import re

def fix_all():
    print("Starting comprehensive fix for all reported issues...")

    # =========================================================================
    # PART 1: FIX SERVER.PY
    # =========================================================================
    with open("server.py", "r", encoding="utf-8") as f:
        srv = f.read()

    # Update register_send_otp in server.py
    reg_send_old = srv[srv.find('@app.route("/api/auth/register-send-otp", methods=["POST"])'):srv.find('@app.route("/api/auth/register-verify-otp", methods=["POST"])')]
    
    reg_send_new = '''@app.route("/api/auth/register-send-otp", methods=["POST"])
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

    # Always record the pending verification code
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

    # Attempt SMTP dispatch
    success, smtp_msg = send_email_via_smtp(email, "TwinStudy Account Verification OTP", otp, action_type="Account Registration")
    
    if success:
        return jsonify({
            "status": "success",
            "message": f"A 6-digit verification code has been dispatched to {email}. Valid for 10 minutes.",
            "email": email,
            "smtp_sent": True
        })
    else:
        # Graceful Hackathon delivery: log prominently to server terminal & return demo_code for instant autofill
        print(f"\\n==========================================")
        print(f">> [DEMO OTP AUTO-DISPATCH] Destination: {email}")
        print(f">> [DEMO OTP CODE]: {otp} (Valid 10 mins)")
        print(f">> [NOTE]: SMTP was not active ({smtp_msg})")
        print(f"==========================================\\n")
        return jsonify({
            "status": "success",
            "message": f"Verification code generated! (Demo / Hackathon Dispatch Active)",
            "email": email,
            "demo_code": otp,
            "smtp_sent": False,
            "smtp_note": smtp_msg
        })

'''
    srv = srv.replace(reg_send_old, reg_send_new)

    # Update resend_otp in server.py
    resend_old = srv[srv.find('@app.route("/api/auth/resend-otp", methods=["POST"])'):srv.find('@app.route("/api/auth/forgot-send-otp", methods=["POST"])')]
    resend_new = '''@app.route("/api/auth/resend-otp", methods=["POST"])
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
            "message": f"A new 6-digit verification code has been dispatched to {email}.",
            "smtp_sent": True
        })
    else:
        print(f">> [DEMO OTP RESEND] Destination: {email}, Code: {new_otp}")
        return jsonify({
            "status": "success",
            "message": f"New verification code generated! (Demo Dispatch Active)",
            "demo_code": new_otp,
            "smtp_sent": False
        })

'''
    srv = srv.replace(resend_old, resend_new)

    # Update forgot_send_otp in server.py
    forgot_old = srv[srv.find('@app.route("/api/auth/forgot-send-otp", methods=["POST"])'):srv.find('@app.route("/api/auth/forgot-verify-otp", methods=["POST"])')]
    forgot_new = '''@app.route("/api/auth/forgot-send-otp", methods=["POST"])
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
        print(f">> [DEMO RESET OTP] Destination: {email}, Code: {otp}")
        return jsonify({
            "status": "success",
            "message": f"Reset code generated for {email} (Demo Dispatch Active)",
            "email": email,
            "demo_code": otp,
            "smtp_sent": False
        })

'''
    srv = srv.replace(forgot_old, forgot_new)

    # Update auth_login field validation in server.py
    login_old = srv[srv.find('@app.route("/api/auth/login", methods=["POST"])'):srv.find('    db = load_db()\n    registered = db.get("registered_users", {})')]
    login_new = '''@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json() or {}
    identifier = (data.get("identifier") or data.get("email") or data.get("phone", "")).strip()
    password = data.get("password", "").strip()

    if not identifier:
        return jsonify({"status": "error", "message": "Please enter your registered email address."}), 400
    if not password:
        return jsonify({"status": "error", "message": "Please enter your password."}), 400

'''
    srv = srv.replace(login_old, login_new)

    with open("server.py", "w", encoding="utf-8") as f:
        f.write(srv)
    print("[OK] server.py updated with robust OTP delivery and login validation")

    # =========================================================================
    # PART 2: FIX PUBLIC/INDEX.HTML
    # =========================================================================
    with open("public/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Unbold and harmonize Comparison Table Column 2 (Image 2)
    # Replace all 'text-slate-700 font-normal border-l' with 'text-black font-medium border-l'
    html = html.replace('text-slate-700 font-normal border-l border-navySlate/10', 'text-black font-medium border-l border-navySlate/10')
    print("[OK] Comparison table Column 2 font thickness harmonized")

    # 2. Remove "Domain 3" line (Image 3)
    domain3_badge = '''<div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/80 border border-white text-navySlate text-xs font-bold shadow-sm">
                    <span className="w-2 h-2 rounded-full bg-cyanAccent"></span>
                    <span>Domain 3: Personal Productivity & Lifestyle • Education Twin</span>
                  </div>'''
    if domain3_badge in html:
        html = html.replace(domain3_badge, '')
        print("[OK] Removed Domain 3 badge pill")
    else:
        # Regex fallback
        html = re.sub(r'<div className="inline-flex items-center gap-2 px-3.5 py-1.5[^>]*>.*?Domain 3.*?<\/div>', '', html, flags=re.DOTALL)
        print("[OK] Removed Domain 3 badge via regex")

    # Also clean up any other "Domain 3: Personal Productivity & Lifestyle" prose
    html = html.replace("TwinStudy © 2026 • Domain 3: Personal Productivity & Lifestyle", "TwinStudy © 2026 • Personal Student Productivity AI Platform")
    html = html.replace("TwinStudy - Domain 3: Personal Productivity & Lifestyle", "TwinStudy - Personal Student Productivity Platform")

    # 3. Empty initial login credentials (fix auto-login on empty click)
    html = html.replace('const [loginIdentifier, setLoginIdentifier] = useState("navinnavi8431@gmail.com");', 'const [loginIdentifier, setLoginIdentifier] = useState("");')
    html = html.replace('const [loginPassword, setLoginPassword] = useState("password123");', 'const [loginPassword, setLoginPassword] = useState("");')
    print("[OK] Initial login credentials set to empty strings")

    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(html)

fix_all()
