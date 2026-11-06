#!/usr/bin/env python3
"""
Adversarial Probe 1: Covert & Obfuscated Romance Scanner
Scans index.html for:
- Explicit and covert Vietnamese romantic terms (with & without diacritics)
- Intimate couple pronouns in romantic contexts (anh/em/đôi ta/chúng mình/vợ/chồng/bé/cưng)
- Romance/Heart emojis (Unicode regex ranges and literal characters)
- HTML comments, inline scripts, meta tags, and data attributes
"""

import re
import sys
import unicodedata
from pathlib import Path
from bs4 import BeautifulSoup

def remove_diacritics(text: str) -> str:
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D')

def run_probe():
    index_path = Path("index.html")
    assert index_path.exists(), "index.html not found!"
    raw_content = index_path.read_text(encoding="utf-8")
    normalized_raw = remove_diacritics(raw_content).lower()

    # 1. Romantic Emojis Probe (Hearts, kiss, couple, wedding ring, rose)
    heart_emojis = [
        "❤️", "💖", "💝", "💘", "💓", "💕", "💗", "💞", "💌", "💟", "❣️", 
        "💑", "👩‍❤️‍👨", "👨‍❤️‍👨", "👩‍❤️‍👩", "💏", "💍", "💒", "🌹", "💋"
    ]
    
    emoji_hits = []
    for em in heart_emojis:
        count = raw_content.count(em)
        if count > 0:
            emoji_hits.append((em, count))

    # 2. Vietnamese Romance Vocabulary & Diminutives Probe
    romantic_patterns = [
        r"\banh\s+yeu\s+em\b",
        r"\byeu\s+em\b",
        r"\banh\s+yeu\b",
        r"\bcho\s+em\b",
        r"\bdanh\s+cho\s+em\b",
        r"\bdi\s+em\b",
        r"\bem\s+yeu\b",
        r"\bbe\s+yeu\b",
        r"\bnguoi\s+yeu\b",
        r"\bnguoi\s+tinh\b",
        r"\bnguoi\s+con\s+gai\s+anh\s+yeu\b",
        r"\btinh\s+yeu\s+tron\s+ven\b",
        r"\btrai\s+tim\s+va\s+tinh\s+yeu\b",
        r"\bbo\s+vai\s+am\s+ap\b",
        r"\bcho\s+dua\s+vung\s+chac\b",
        r"\bmai\s+mai\s+ve\s+sau\b",
        r"\bhon\s+em\b",
        r"\bnho\s+em\b",
        r"\bvo\s+yeu\b",
        r"\bchong\s+yeu\b",
        r"\bdoi\s+ta\b",
        r"\bhai\s+dua\s+minh\b",
        r"\blua\s+doi\b",
        r"\bcung\s+yeu\b",
        r"\bem\s+biet\s+khong\b",
        r"\bmoi\s+em\b"
    ]

    regex_hits = []
    for pat in romantic_patterns:
        matches = list(re.finditer(pat, normalized_raw))
        if matches:
            for m in matches:
                # Find context in raw_content
                start = max(0, m.start() - 30)
                end = min(len(raw_content), m.end() + 30)
                snippet = raw_content[start:end].replace("\n", " ")
                regex_hits.append((pat, snippet))

    # 3. HTML Comments Inspection
    soup = BeautifulSoup(raw_content, "html.parser")
    comments = soup.find_all(string=lambda text: isinstance(text, type(soup.Comment)))
    comment_hits = []
    for c in comments:
        c_norm = remove_diacritics(str(c)).lower()
        for pat in romantic_patterns:
            if re.search(pat, c_norm):
                comment_hits.append((pat, str(c)))

    # 4. Check pronouns in user-visible text
    visible_texts = []
    # Collect title, tap hint, headings, body texts, script message variable
    title = soup.title.string if soup.title else ""
    tap_hint = soup.find(id="tapHint").get_text() if soup.find(id="tapHint") else ""
    h1 = soup.h1.get_text() if soup.h1 else ""
    
    # Extract message variable from script
    msg_match = re.search(r"const\s+message\s*=\s*`([^`]+)`", raw_content)
    message_content = msg_match.group(1) if msg_match else ""

    print("=== ADVERSARIAL ROMANCE SCAN RESULTS ===")
    print(f"1. Romantic Emojis Found: {emoji_hits}")
    print(f"2. Romantic Regex Hits: {len(regex_hits)}")
    for hit in regex_hits:
        print(f"   MATCH [{hit[0]}]: ...{hit[1]}...")
    print(f"3. Comment Hits: {len(comment_hits)}")
    print(f"4. Scanned Components:")
    print(f"   - Title: {title}")
    print(f"   - Tap Hint: {tap_hint}")
    print(f"   - H1: {h1}")
    print(f"   - Message length: {len(message_content)} chars")
    
    # 5. Check if 'anh' or 'em' appear anywhere in user-facing text
    combined_user_text = f"{title} {tap_hint} {h1} {message_content}"
    combined_norm = remove_diacritics(combined_user_text).lower()
    
    couple_words = ["anh", "em", "yeu"]
    suspicious = []
    for word in couple_words:
        # Check standalone word
        found = re.findall(rf"\b{word}\b", combined_norm)
        if found:
            suspicious.append((word, len(found)))
            
    print(f"5. Suspicious couple keywords (anh/em/yeu) in user text: {suspicious}")

    return {
        "emoji_hits": emoji_hits,
        "regex_hits": regex_hits,
        "comment_hits": comment_hits,
        "suspicious_words": suspicious
    }

if __name__ == "__main__":
    res = run_probe()
    if res["emoji_hits"] or res["regex_hits"] or res["comment_hits"] or res["suspicious_words"]:
        print("\nPROBE FAILED: Covert romantic content detected!")
        sys.exit(1)
    else:
        print("\nPROBE PASSED: Absolutely zero romance detected!")
        sys.exit(0)
