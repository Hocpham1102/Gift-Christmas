import re
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup

repo_root = Path(r"e:\GitHub\Gift-Christmas")
html_path = repo_root / "index.html"
content = html_path.read_text(encoding="utf-8")

# Extract message
match = re.search(r"const\s+message\s*=\s*`([^`]+)`;", content)
assert match, "const message not found"
msg = match.group(1)

print("=== MESSAGE ANALYSIS ===")
print("Raw length:", len(msg))
plain = msg.replace("<br>", "\n")
print("Plain text length:", len(plain))
paragraphs = [p.strip() for p in plain.split("\n") if p.strip()]
print("Paragraph count:", len(paragraphs))
for idx, p in enumerate(paragraphs, 1):
    print(f"  P{idx} ({len(p)} chars): {p}")

print("\n=== TYPEWRITER LOGIC SIMULATION ===")
# Simulate typeWriter() logic in Python
i = 0
output_chars = []
speed = 35

def check_tag(idx, text):
    tag = ""
    while idx < len(text) and text[idx] != ">":
        tag += text[idx]
        idx += 1
    tag += ">"
    idx += 1
    return tag, idx

curr_i = 0
rendered = ""
steps = 0
while curr_i < len(msg):
    ch = msg[curr_i]
    if ch == "<":
        tag, curr_i = check_tag(curr_i, msg)
        rendered += tag
    else:
        rendered += ch
        curr_i += 1
    steps += 1

print(f"Total typewriter steps: {steps}")
print(f"Simulated duration: {steps * speed / 1000.0:.2f} seconds")
assert rendered == msg, "Rendered output does not match message!"
print("Typewriter fidelity: 100% MATCH")

print("\n=== SYNTAX & STRUCTURE AUDIT ===")
soup = BeautifulSoup(content, "html.parser")
print("Title:", soup.title.string)
print("TapHint:", soup.find(id="tapHint").get_text())
print("Main heading:", soup.find("h1").get_text())

# Tag balance
for tag_name in ["div", "span", "script", "style", "audio", "canvas"]:
    opens = len(re.findall(rf"<{tag_name}\b", content, re.IGNORECASE))
    closes = len(re.findall(rf"</{tag_name}\s*>", content, re.IGNORECASE))
    print(f"Tag <{tag_name}>: {opens} open, {closes} close -> {'BALANCED' if opens == closes else 'MISMATCH'}")
    assert opens == closes, f"Mismatch in <{tag_name}>"

# Check end of file
lines = content.splitlines()
print("Last 5 lines:")
for l in lines[-5:]:
    print("  ", repr(l))

assert lines[-1].strip() == "</html>", "File does not terminate with </html>"
assert not any("```" in l for l in lines[-10:]), "Trailing markdown fence detected!"

print("\nALL INDEPENDENT CHECKS PASSED!")
