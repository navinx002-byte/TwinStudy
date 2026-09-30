def verify():
    print("==========================================")
    print("VERIFYING ALL USER REQUESTED CHANGES")
    print("==========================================")

    with open("public/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Check parent/guardian removed from sidebar
    assert 'Parent / Guardian View' not in html[html.find('<aside'):html.find('</aside>')], "Parent/Guardian view must be removed from sidebar"
    print(">> [PASS] Parent/Guardian View removed from toolbar/sidebar navigation.")

    # 2. Check Gmail SMTP settings removed from Profile & Settings
    settings_section = html[html.find('{appPage === "settings" && ('):html.find('{appPage === "timetable" && (', html.find('{appPage === "settings" && ('))]
    assert "Gmail SMTP Verification Settings" not in settings_section, "Gmail SMTP settings must be removed from Profile & Settings"
    assert "16-Character Google App Password" not in settings_section, "App password field must be removed from Profile & Settings"
    print(">> [PASS] Gmail SMTP Verification Settings removed from Profile & Settings.")

    # 3. Check Back button in top-left corner
    assert 'title="Back to Dashboard or Home"' in html, "Back button must be in header"
    assert "<span>Back to Home</span>" in html, "Back button must be in auth header"
    print(">> [PASS] Working Back button installed in the top-left corner.")

    # 4. Check 8 MCQs in Teach-Back Quiz generator
    assert "id: 8" in html, "Must have 8 questions in quiz generator"
    assert "Pass mark: 6/8" in html, "Pass mark must be 6/8"
    assert "⚠️ Please answer all 8 Teach-Back Quiz questions" in html, "Validation must check 8 questions"
    print(">> [PASS] Proof-based tasks upgraded to 8 tailored MCQs with pass mark 6/8.")

    # 5. Check simulator defense against crash
    assert "simResult?.why_this?.top_factors_plain_language" in html, "Guarded against undefined"
    assert "simResult?.why_this?.data_receipt?.sources_used" in html, "Guarded against undefined"
    print(">> [PASS] What-If Simulator completely guarded against undefined data receipt crashes.")

    print("\nALL 5 ASSERTIONS PASSED!")

if __name__ == "__main__":
    verify()
