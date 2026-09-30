import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("public/index.html", "r", encoding="utf-8") as f:
    text = f.read()

idx1 = text.find("{showCorrectPatternModal && editingPattern && (")
print("CorrectPatternModal at:", idx1)
if idx1 != -1:
    print(text[idx1:idx1+1500])

idx2 = text.find("{showFeedbackModal && feedbackDecision && (")
print("\nFeedbackModal at:", idx2)
if idx2 != -1:
    print(text[idx2:idx2+1500])
