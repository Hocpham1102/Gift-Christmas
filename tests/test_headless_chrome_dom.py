#!/usr/bin/env python3
"""
Adversarial Probe 3: Headless Chrome DOM & Runtime Verification
Loads index.html in Chromium, monitors console errors, triggers box opening,
and validates typewriter and DOM lifecycle.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def run_headless_chrome_test():
    index_path = Path("index.html").resolve()
    assert index_path.exists(), f"File {index_path} not found"
    file_url = index_path.as_uri()

    console_errors = []
    page_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ["error"] else None)
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))

        print(f"Navigating to: {file_url}")
        page.goto(file_url, wait_until="load")

        # 1. Verify Static DOM Elements
        title = page.title()
        print(f"Loaded Page Title: {title}")
        assert "Merry Christmas - Món Quà Giáng Sinh Ấm Áp Dành Tặng Bạn 🎄✨" in title, f"Unexpected title: {title}"

        tap_hint = page.locator("#tapHint").inner_text()
        print(f"Tap Hint: {tap_hint}")
        assert "Chạm vào hộp quà để mở điều bất ngờ bạn nhé!" in tap_hint, f"Unexpected tap hint: {tap_hint}"

        h1 = page.locator("#mainContent h1").inner_text()
        print(f"Main Content H1: {h1}")
        assert "Merry Christmas! 🎄✨🎁" in h1, f"Unexpected H1: {h1}"

        # 2. Check 3D Canvas
        three_canvas = page.locator("#three-canvas")
        assert three_canvas.is_visible(), "three-canvas should be visible"

        # 3. Simulate Gift Box Click / Open
        print("Simulating interaction to open gift box...")
        # Since Three.js handles raycasting on click, we click center of canvas
        box = three_canvas.bounding_box()
        if box:
            center_x = box["x"] + box["width"] / 2
            center_y = box["y"] + box["height"] / 2
            page.mouse.click(center_x, center_y)

        # Wait for timeout (1000ms delay + some typing)
        page.wait_for_timeout(2500)

        # Check if mainContent activated
        main_content_class = page.locator("#mainContent").get_attribute("class")
        print(f"mainContent class: {main_content_class}")

        typewriter_text = page.locator("#typewriter").inner_text()
        print(f"Typewriter text after 2.5s: '{typewriter_text[:60]}...' (len: {len(typewriter_text)})")
        assert len(typewriter_text) > 0, "Typewriter should have started typing text!"
        assert "Gửi người bạn thân mến" in typewriter_text, "Typewriter should be typing friendship message!"

        # 4. Settings modal test
        settings_btn = page.locator("#settingsBtn")
        assert settings_btn.is_visible(), "Settings button should be visible"
        settings_btn.click()
        page.wait_for_timeout(300)
        
        modal_visible = page.locator("#settingsModal").is_visible()
        print(f"Settings modal visible after click: {modal_visible}")
        assert modal_visible, "Settings modal should be visible after clicking settingsBtn"

        # Close modal
        page.locator("#closeModal").click()
        page.wait_for_timeout(300)
        modal_visible_after = page.locator("#settingsModal").is_visible()
        print(f"Settings modal visible after close: {modal_visible_after}")
        assert not modal_visible_after, "Settings modal should be hidden after closing"

        browser.close()

    print("\n=== CONSOLE & RUNTIME ERRORS ===")
    print(f"Page errors: {page_errors}")
    print(f"Console errors: {console_errors}")

    # Note: Audio autoplay block or Three.js WebGL context without GPU in headless may log warnings or audio error.
    # We filter out expected headless media autoplay restriction
    critical_errors = [e for e in console_errors if "play() failed" not in e and "NotAllowedError" not in e]

    if page_errors or critical_errors:
        print("FAIL: Found critical JS runtime errors!")
        return False
    else:
        print("SUCCESS: Headless Chrome loaded and ran flawlessly without runtime errors!")
        return True

if __name__ == "__main__":
    success = run_headless_chrome_test()
    sys.exit(0 if success else 1)
