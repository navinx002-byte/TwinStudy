import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("public/index.html", "r", encoding="utf-8") as f:
    text = f.read()

bot_ui_idx = text.find("{showFaqBot && (")
if bot_ui_idx != -1:
    print("Chatbot UI found at:", bot_ui_idx)
    print(text[bot_ui_idx:bot_ui_idx+2000])
else:
    print("showFaqBot UI not found")
