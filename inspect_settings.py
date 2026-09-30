import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("public/index.html", "r", encoding="utf-8") as f:
    text = f.read()

idx_set = text.find('{appPage === "settings" && (')
print("Index of settings view:", idx_set)
if idx_set != -1:
    print(text[idx_set:idx_set+1200])
