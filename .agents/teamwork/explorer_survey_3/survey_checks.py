# Test script for Explorer 3 survey
import re
from bs4 import BeautifulSoup

def analyze_index_html():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    
    title = soup.title.string.strip() if soup.title else ""
    h1 = soup.h1.text.strip() if soup.h1 else ""
    tap_hint = soup.find(id='tapHint')
    tap_text = tap_hint.text.strip() if tap_hint else ""

    # Extract JS message variable
    match = re.search(r'const\s+message\s*=\s*`([^`]*)`', html)
    message_text = match.group(1) if match else ""

    # Romance word dictionary
    romantic_keywords = [
        "anh yêu em",
        "dành cho em",
        "người con gái anh yêu",
        "em yêu",
        "anh yêu",
        "trái tim và tình yêu",
        "bờ vai ấm áp",
        "đi em",
        "bên em",
        "❤️",
        "💖",
        "💝"
    ]

    found_in_title = [k for k in romantic_keywords if k.lower() in title.lower()]
    found_in_tap = [k for k in romantic_keywords if k.lower() in tap_text.lower()]
    found_in_h1 = [k for k in romantic_keywords if k.lower() in h1.lower()]
    found_in_msg = [k for k in romantic_keywords if k.lower() in message_text.lower()]

    return {
        "title": title,
        "title_romantic": found_in_title,
        "tap_hint": tap_text,
        "tap_hint_romantic": found_in_tap,
        "h1": h1,
        "h1_romantic": found_in_h1,
        "message_preview": message_text[:100] + "...",
        "message_romantic": found_in_msg,
        "particles": {
            "has_heart_particle": "HeartParticle" in html,
            "heart_color": "#ff6b9d" in html
        }
    }

if __name__ == '__main__':
    results = analyze_index_html()
    import json
    print(json.dumps(results, indent=2, ensure_ascii=False))
