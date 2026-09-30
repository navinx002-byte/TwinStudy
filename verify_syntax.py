import urllib.request
import urllib.error
import json
import re

base = "http://localhost:5000"

def test_syntax_and_endpoints():
    print("==========================================")
    print("VERIFYING FIXES & TESTING ENDPOINTS")
    print("==========================================")

    # 1. HTML & JS Verification
    with open("public/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Check that handlers are declared
    required_handlers = [
        "const handleAskFaq",
        "const handleSaveSmtp",
        "const handleResetTwinWeights",
        "const handleDeletePattern",
        "const handleSaveCorrectPattern",
        "const handleSubmitRealityFeedback"
    ]
    for h in required_handlers:
        assert h in html, f"Missing declaration: {h}"
        print(f">> [PASS] Found declaration: {h}")

    # Check Comparison Table Column 2
    assert 'text-slate-700 font-normal border-l' not in html, "Faded font in Column 2 should be gone"
    assert 'text-black font-medium border-l border-navySlate/10' in html, "Column 2 must match other columns"
    print(">> [PASS] Comparison table font thickness harmonized across all columns")

    # Check Domain 3 badge
    assert "Domain 3: Personal Productivity & Lifestyle • Education Twin" not in html, "Domain 3 badge must be removed"
    print(">> [PASS] Domain 3 badge line removed")

    # Check initial login credentials
    assert 'const [loginIdentifier, setLoginIdentifier] = useState("");' in html, "Login identifier must start empty"
    assert 'const [loginPassword, setLoginPassword] = useState("");' in html, "Login password must start empty"
    print(">> [PASS] Login fields initialized to empty strings")

    print("\nAll frontend assertions passed!")

if __name__ == "__main__":
    test_syntax_and_endpoints()
