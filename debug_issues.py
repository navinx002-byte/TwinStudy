import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("public/index.html", "r", encoding="utf-8") as f:
    text = f.read()

print("1. Settings section occurrences:")
for m in re.finditer(r'appPage === "settings"', text):
    print("Found at:", m.start())
    print(text[m.start():m.start()+200])

print("\n2. Chatbot buttons:")
bot_idx = text.find("Scout AI")
if bot_idx != -1:
    print("Scout AI at:", bot_idx)
    print(text[bot_idx:bot_idx+1500])

print("\n3. Twin Learning Engine toolbar:")
twin_idx = text.find('appPage === "twin_mind"')
if twin_idx != -1:
    print("Twin Mind at:", twin_idx)
    print(text[twin_idx:twin_idx+1200])
