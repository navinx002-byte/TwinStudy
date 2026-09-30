import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("public/index.html", "r", encoding="utf-8") as f:
    text = f.read()

idx_set = text.find('{appPage === "settings" && (')
if idx_set != -1:
    print(text[idx_set+1200:idx_set+3500])
