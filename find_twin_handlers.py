import re

with open("public/index.html", "r", encoding="utf-8") as f:
    text = f.read()

twin_start = text.find('{appPage === "twin_mind" && (')
twin_end = text.find('{appPage === "grades" && (', twin_start)
twin_code = text[twin_start:twin_end]

# Find all onClick={...} in twin_code
handlers = re.findall(r'onClick=\{([^\}]+)\}', twin_code)
print("Handlers in twin_mind:")
for h in set(handlers):
    print(" ", h.strip())
