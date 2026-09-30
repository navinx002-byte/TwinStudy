import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("public/index.html", "r", encoding="utf-8") as f:
    text = f.read()

idx_twin = text.find('{appPage === "twin_mind" && (')
if idx_twin != -1:
    print(text[idx_twin+2000:idx_twin+5000])
