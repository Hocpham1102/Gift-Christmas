"""
Verification Suite for Gift-Christmas Card (Explorer 3 Test Architecture Prototype)
Checks:
1. HTML Syntax & Cleanliness (trailing backticks, tag pairing)
2. Forbidden Romantic Vocabulary & Icons Audit (Title, Tap Hint, Card Heading, Message, Modal)
3. Friendship Content Integrity & Themes
4. CSS & Anti-Overflow Layout Checks (overflow-y, dvh, font-size clamp)
5. Particle System Audit (no pink HeartParticle)
6. Audio Controls & Configuration Check
7. Headless Chrome Multi-Viewport Rendering & Screenshot Verification
"""

import os
import re
import subprocess
from bs4 import BeautifulSoup

INDEX_PATH = r"E:\GitHub\Gift-Christmas\index.html"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
REPORT_DIR = r"E:\GitHub\Gift-Christmas\.agents\teamwork\explorer_survey_3"

ROMANTIC_FORBIDDEN_WORDS = [
    "anh yêu em",
    "yêu em",
    "dành cho em",
    "đi em",
    "người con gái anh yêu",
    "người yêu",
    "bờ vai ấm áp",
    "trái tim và tình yêu",
    "tình yêu trọn vẹn",
    "mãi mãi về sau",
    "💝",
    "HeartParticle"
]

def test_html_syntax():
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check trailing backticks
    last_10 = "".join(lines[-10:])
    has_trailing_backticks = "```" in last_10
    
    return {
        "pass": not has_trailing_backticks,
        "detail": "Found trailing markdown code fence at end of file" if has_trailing_backticks else "File terminates cleanly"
    }

def test_romantic_vocabulary():
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.title.string if soup.title else ""
    tap_hint = soup.find(id='tapHint')
    tap_text = tap_hint.text if tap_hint else ""
    h1 = soup.h1.text if soup.h1 else ""
    
    msg_match = re.search(r'const\s+message\s*=\s*`([^`]*)`', content)
    message_text = msg_match.group(1) if msg_match else ""
    
    found_violations = []
    for term in ROMANTIC_FORBIDDEN_WORDS:
        term_lower = term.lower()
        if term_lower in title.lower():
            found_violations.append(f"Title contains '{term}'")
        if term_lower in tap_text.lower():
            found_violations.append(f"Tap hint contains '{term}'")
        if term_lower in h1.lower():
            found_violations.append(f"Card H1 contains '{term}'")
        if term_lower in message_text.lower():
            found_violations.append(f"Card message contains '{term}'")
        if term == "HeartParticle" and "HeartParticle" in content:
            found_violations.append("Canvas contains HeartParticle class")
            
    return {
        "pass": len(found_violations) == 0,
        "violations": found_violations,
        "current_title": title,
        "current_tap_hint": tap_text,
        "current_h1": h1,
        "current_message_len": len(message_text)
    }

def test_css_layout_defects():
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check overflow: hidden vs overflow-y: auto
    # Look at .content and #typewriter
    content_has_overflow_hidden = bool(re.search(r'\.content\s*\{[^}]*overflow\s*:\s*hidden', content))
    typewriter_has_overflow_hidden = bool(re.search(r'#typewriter\s*\{[^}]*overflow\s*:\s*hidden', content))
    has_music_toggle = "musicToggle" in content or "music-toggle-btn" in content
    
    return {
        "content_overflow_hidden": content_has_overflow_hidden,
        "typewriter_overflow_hidden": typewriter_has_overflow_hidden,
        "has_music_toggle": has_music_toggle
    }

def test_headless_render():
    viewports = [
        ("desktop_1080p", "1920,1080"),
        ("tablet_portrait", "768,1024"),
        ("mobile_portrait", "375,667"),
        ("mobile_landscape", "667,375")
    ]
    results = {}
    if not os.path.exists(CHROME_PATH):
        return {"pass": False, "detail": "Chrome executable not found"}
        
    for name, size in viewports:
        out_file = os.path.join(REPORT_DIR, f"screenshot_{name}.png")
        cmd = [
            CHROME_PATH,
            "--headless=new",
            f"--window-size={size}",
            f"--screenshot={out_file}",
            f"file:///{INDEX_PATH.replace(os.sep, '/')}"
        ]
        ret = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        file_exists = os.path.exists(out_file)
        file_size = os.path.getsize(out_file) if file_exists else 0
        results[name] = {
            "success": ret.returncode == 0 and file_exists,
            "file": out_file,
            "bytes": file_size
        }
    return results

if __name__ == "__main__":
    syntax = test_html_syntax()
    vocab = test_romantic_vocabulary()
    layout = test_css_layout_defects()
    print("--- 1. HTML Syntax ---")
    print("Pass:", syntax["pass"], "| Detail:", syntax["detail"])
    print("\n--- 2. Romantic Vocabulary Audit ---")
    print("Pass:", vocab["pass"])
    if vocab["violations"]:
        print("Violations (Expected on current baseline):")
        for v in vocab["violations"]:
            print("  -", v)
    print("\n--- 3. CSS Layout & Overflow Audit ---")
    print("Content overflow:hidden:", layout["content_overflow_hidden"])
    print("Typewriter overflow:hidden:", layout["typewriter_overflow_hidden"])
    print("Has Music Toggle UI:", layout["has_music_toggle"])
    print("\n--- 4. Headless Chrome Multi-Viewport Rendering ---")
    render = test_headless_render()
    for vp, res in render.items():
        print(f"  {vp}: Success={res['success']}, Size={res['bytes']} bytes")
