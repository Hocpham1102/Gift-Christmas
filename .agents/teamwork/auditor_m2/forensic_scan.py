import re
import os
import sys
from bs4 import BeautifulSoup
from PIL import Image

def run_forensic_scan():
    print("=== FORENSIC SCAN START ===")
    index_path = "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. HeartParticle Check
    print("\n--- 1. HeartParticle & Romance Residue Check ---")
    heart_matches = re.findall(r'HeartParticle|class\s+\w*[Hh]eart\w*', content)
    print(f"HeartParticle references: {heart_matches}")
    assert len(heart_matches) == 0, f"Found HeartParticle references: {heart_matches}"

    # Search for heart emojis or romantic symbols
    heart_emojis = ["💝", "❤️", "💖", "💕", "💘", "💓", "💞"]
    found_emojis = [e for e in heart_emojis if e in content]
    print(f"Heart emojis found: {found_emojis}")
    assert len(found_emojis) == 0, f"Found romantic emojis: {found_emojis}"

    # Search for forbidden romantic words
    romantic_words = [
        "anh yêu em", "yêu em", "dành cho em", "đi em", "người con gái anh yêu",
        "người yêu", "bờ vai ấm áp", "trái tim và tình yêu", "tình yêu trọn vẹn",
        "mãi mãi về sau", "chỗ dựa vững chắc", "em biết không", "hôn em", "nhớ em"
    ]
    found_words = [w for w in romantic_words if w.lower() in content.lower()]
    print(f"Romantic words found: {found_words}")
    assert len(found_words) == 0, f"Found romantic words: {found_words}"

    # 2. Check #cardBody structure and CSS
    print("\n--- 2. #cardBody Structural and CSS Check ---")
    soup = BeautifulSoup(content, "html.parser")
    card_body = soup.find(id="cardBody")
    assert card_body is not None, "Element #cardBody not found in DOM!"
    print(f"#cardBody found: tag=<{card_body.name} id='{card_body.get('id')}'>, class={card_body.get('class')}")
    
    # Check parent and children
    parent = card_body.parent
    print(f"Parent of #cardBody: tag=<{parent.name} id='{parent.get('id')}'>, class={parent.get('class')}")
    assert "content" in parent.get("class", []) or parent.get("id") == "mainContent", "Parent is not .content / #mainContent"

    typewriter_el = card_body.find(id="typewriter")
    assert typewriter_el is not None, "Element #typewriter is NOT inside #cardBody!"
    print(f"#typewriter is properly nested inside #cardBody: tag=<{typewriter_el.name} id='{typewriter_el.get('id')}'>")

    # Check CSS for card-body / #cardBody
    assert "overflow-y: auto" in content or "overflow-y:auto" in content or "overflow-y: scroll" in content, "Missing overflow-y: auto for card body!"
    assert "overscroll-behavior: contain" in content, "Missing overscroll-behavior: contain!"
    assert "max-height" in content, "Missing max-height on cardBody!"
    assert "::-webkit-scrollbar" in content, "Missing custom scrollbar styling!"
    print("CSS for card body scrolling verified.")

    # 3. Check #musicToggle
    print("\n--- 3. #musicToggle Implementation Check ---")
    music_toggle = soup.find(id="musicToggle")
    assert music_toggle is not None, "Element #musicToggle not found in DOM!"
    print(f"#musicToggle found: tag=<{music_toggle.name} id='{music_toggle.get('id')}'>, aria-label='{music_toggle.get('aria-label')}'")
    assert music_toggle.get("aria-label") or music_toggle.get("title"), "Missing accessible label on #musicToggle"

    bg_music = soup.find("audio", id="bgMusic")
    assert bg_music is not None, "<audio id='bgMusic'> not found in DOM!"
    print(f"bgMusic found: tag=<{bg_music.name} id='{bg_music.get('id')}'>, loop={bg_music.has_attr('loop')}")

    # Check JS wiring
    assert "musicToggle.addEventListener" in content or "getElementById('musicToggle')" in content, "musicToggle not wired in JS!"
    assert "bgMusic.paused" in content, "bgMusic.paused check missing in toggle listener!"
    assert "bgMusic.play()" in content and "bgMusic.pause()" in content, "Genuine play/pause calls missing!"
    print("Music toggle genuine wiring verified.")

    # 4. Check Particles
    print("\n--- 4. Particle System Classes & Instantiation Check ---")
    assert "class SnowParticle" in content, "SnowParticle missing!"
    assert "class BokehParticle" in content or "class SparkleParticle" in content, "Festive particles missing!"
    assert "new SnowParticle" in content, "SnowParticle instantiation missing!"
    assert "new BokehParticle" in content or "new SparkleParticle" in content, "Festive particle instantiation missing!"
    print("Snow, Sparkle, and Bokeh particles active.")

    # 5. Check Palette
    print("\n--- 5. Color Palette & Lighting Check ---")
    assert "#090e1a" in content or "#0f1d33" in content, "Dark holiday twilight palette missing!"
    assert "0xff6b9d" not in content.lower(), "Pink PointLight (0xff6b9d) still present!"
    assert "rgba(255, 107, 157" not in content, "Pink radial glow (255, 107, 157) still present!"
    print("Holiday palette and lighting verified.")

    # 6. Check Screenshots
    print("\n--- 6. Screenshot Artifacts Inspection ---")
    screenshot_dir = "tests/artifacts/screenshots"
    for filename in os.listdir(screenshot_dir):
        if filename.endswith(".png"):
            filepath = os.path.join(screenshot_dir, filename)
            filesize = os.path.getsize(filepath)
            with Image.open(filepath) as img:
                width, height = img.size
                format_name = img.format
            print(f"Screenshot {filename}: {width}x{height}, format={format_name}, size={filesize} bytes")
            assert filesize > 50000, f"Screenshot {filename} is suspiciously small: {filesize} bytes"
            assert format_name == "PNG", f"Screenshot {filename} is not PNG format"

    print("\n=== ALL FORENSIC SCAN CHECKS PASSED CLEANLY ===")

if __name__ == "__main__":
    run_forensic_scan()
