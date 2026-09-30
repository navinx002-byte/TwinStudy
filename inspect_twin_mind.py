import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("public/index.html", "r", encoding="utf-8") as f:
    text = f.read()

idx_twin = text.find('{appPage === "twin_mind" && (')
print("appPage === 'twin_mind' at:", idx_twin)
if idx_twin != -1:
    print(text[idx_twin:idx_twin+2500])
