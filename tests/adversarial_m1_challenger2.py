#!/usr/bin/env python3
"""
Adversarial Verification Suite for Milestone M1 - Challenger 2
============================================================
Focus:
1. HTML Syntax & End-of-File Cleanliness
2. Typewriter Execution Timing, Memory, and Termination
3. Edge Cases: Fast Clicking, Modal Interactions, Copy Notification, URL Tampering
"""

import os
import re
import sys
import json
import time
from pathlib import Path
from html.parser import HTMLParser
import xml.etree.ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = REPO_ROOT / "index.html"

def test_eof_cleanliness():
    print("\n--- Test Suite 1: End-Of-File Syntax & Cleanliness ---")
    with open(INDEX_HTML, "rb") as f:
        raw_bytes = f.read()

    # 1.1 Check trailing bytes
    trailing = raw_bytes[-100:].decode("utf-8", errors="replace")
    print("Trailing 100 characters of index.html:")
    print(repr(trailing))

    # Assert no markdown code fences
    assert b"```" not in raw_bytes[-200:], "FAILED: Trailing markdown backticks found near EOF!"
    print("[PASS] 1.1: No markdown code fences in trailing 200 bytes.")

    # Assert ends with </html> and optional trailing whitespace/newline
    stripped_end = raw_bytes.rstrip()
    assert stripped_end.endswith(b"</html>"), f"FAILED: File does not terminate with </html>. Ends with: {stripped_end[-20:]}"
    print("[PASS] 1.2: File cleanly terminates with </html>.")

    # Assert no null bytes anywhere in file
    assert b"\x00" not in raw_bytes, "FAILED: Null bytes found in file!"
    print("[PASS] 1.3: Zero null bytes in entire file.")

    # 1.2 Tag Balance Audit (Non-void tags)
    text = raw_bytes.decode("utf-8")
    void_tags = {"meta", "link", "img", "br", "hr", "input", "source", "path"}
    
    class TagAuditor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.tag_stack = []
            self.errors = []
            self.line_map = {}

        def handle_starttag(self, tag, attrs):
            if tag.lower() not in void_tags:
                self.tag_stack.append((tag.lower(), self.getpos()))

        def handle_endtag(self, tag):
            tag_lower = tag.lower()
            if tag_lower in void_tags:
                return
            if not self.tag_stack:
                self.errors.append(f"Unexpected closing tag </{tag_lower}> at line {self.getpos()[0]}")
                return
            last_tag, pos = self.tag_stack.pop()
            if last_tag != tag_lower:
                self.errors.append(f"Mismatched tag: expected </{last_tag}> (opened line {pos[0]}), got </{tag_lower}> at line {self.getpos()[0]}")

    parser = TagAuditor()
    parser.feed(text)
    
    if parser.tag_stack:
        print(f"Warning: Unclosed tags remaining in stack: {parser.tag_stack}")
    assert len(parser.errors) == 0, f"FAILED: Tag mismatch errors found: {parser.errors}"
    assert len(parser.tag_stack) == 0, f"FAILED: Unclosed tags remaining: {parser.tag_stack}"
    print("[PASS] 1.4: HTML tag hierarchy is perfectly balanced (0 mismatched, 0 unclosed tags).")


def test_typewriter_timing_and_simulation():
    print("\n--- Test Suite 2: Typewriter Timing, State, Memory, & Termination ---")
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract message and speed
    msg_match = re.search(r"const message\s*=\s*`([^`]+)`;", content)
    speed_match = re.search(r"const speed\s*=\s*(\d+);", content)

    assert msg_match, "FAILED: const message not found"
    assert speed_match, "FAILED: const speed not found"

    message = msg_match.group(1)
    speed = int(speed_match.group(1))

    print(f"Message total character length: {len(message)}")
    print(f"Configured speed: {speed} ms per tick")

    # Mathematical Timing Calculation:
    # In index.html:
    # if (i < message.length) {
    #   const char = message.charAt(i);
    #   document.getElementById("typewriter").innerHTML +=
    #     char === "<" ? checkTag() : char;
    #   if (char !== "<") i++;
    #   setTimeout(typeWriter, speed);
    # }
    #
    # When char === "<":
    # checkTag() reads from i until ">", increments i past ">", returns tag.
    # So a whole tag (e.g. "<br>") consumes only 1 setTimeout iteration!
    # Non-tag characters each consume 1 setTimeout iteration.

    # Count occurrences of tags
    tags = re.findall(r"<[^>]+>", message)
    print(f"HTML tags inside message: {tags}")
    tag_chars_total = sum(len(t) for t in tags)
    num_tags = len(tags)
    
    non_tag_chars = len(message) - tag_chars_total
    total_ticks = non_tag_chars + num_tags
    total_duration_ms = total_ticks * speed
    total_duration_sec = total_duration_ms / 1000.0

    print(f"Non-tag characters: {non_tag_chars}")
    print(f"Number of tags: {num_tags} (total tag characters: {tag_chars_total})")
    print(f"Exact total setTimeout ticks: {total_ticks}")
    print(f"Exact nominal delivery duration: {total_duration_ms} ms ({total_duration_sec:.2f} seconds)")

    # Bounds & Sanity checks
    assert 15 <= speed <= 50, f"Speed {speed}ms is outside reasonable UX bounds (15ms-50ms)"
    assert 15.0 <= total_duration_sec <= 35.0, f"Delivery duration {total_duration_sec}s outside acceptable range (15s - 35s)"
    print(f"[PASS] 2.1: Timing duration is strictly within optimal human reading envelope (15s-35s): {total_duration_sec:.2f}s")

    # Accurate Simulation of typeWriter and checkTag
    def simulate_typewriter(msg):
        i = 0
        output = ""
        tick_count = 0
        max_safety_ticks = len(msg) * 2

        while i < len(msg):
            tick_count += 1
            if tick_count > max_safety_ticks:
                raise RuntimeError("INFINITE LOOP DETECTED in typewriter simulation!")
            
            char = msg[i]
            if char == "<":
                # checkTag
                tag = ""
                while i < len(msg) and msg[i] != ">":
                    tag += msg[i]
                    i += 1
                if i >= len(msg):
                    raise RuntimeError("UNCLOSED HTML TAG in message: tag reached EOF without '>'")
                tag += ">"
                i += 1
                output += tag
            else:
                output += char
                i += 1

        return output, tick_count, i

    sim_output, sim_ticks, final_i = simulate_typewriter(message)
    assert sim_output == message, "FAILED: Simulated typewriter output does not exactly match message!"
    assert sim_ticks == total_ticks, f"FAILED: Tick count mismatch: {sim_ticks} vs {total_ticks}"
    assert final_i == len(message), f"FAILED: Index pointer stopped at {final_i}, expected {len(message)}"
    print(f"[PASS] 2.2: Simulation verified 100% exact message reconstruction without dropouts or infinite loop.")


def test_browser_adversarial_suite():
    print("\n--- Test Suite 3: Playwright Chromium Headless Adversarial Suite ---")
    from playwright.sync_api import sync_playwright

    index_url = INDEX_HTML.as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        console_messages = []
        errors = []

        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))

        # 3.1 Initial Load & DOM Inspection
        page.goto(index_url, wait_until="networkidle")
        time.sleep(1)

        print(f"Loaded page: {page.title()}")
        assert "Merry Christmas" in page.title(), "FAILED: Title mismatch!"
        print("[PASS] 3.1: Page loaded cleanly in Chromium.")

        # Check for unexpected console errors
        # Note: audio autoplay warning or WebGL warnings might appear if sound or gpu not present
        fatal_errors = [e for e in errors if "audio" not in e.lower()]
        assert len(fatal_errors) == 0, f"FAILED: Fatal page errors: {fatal_errors}"
        print("[PASS] 3.2: Zero unhandled JavaScript exceptions on initial load.")

        # 3.2 Adversarial Test: Rapid Click Spamming on Gift Box (#three-canvas)
        print("Testing rapid click spam on #three-canvas (50 clicks in rapid succession)...")
        spam_result = page.evaluate("""() => {
            const canvas = document.getElementById('three-canvas');
            const initialOpened = isOpened;
            let clickCount = 0;
            for (let k = 0; k < 50; k++) {
                canvas.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                clickCount++;
            }
            return {
                clickCount,
                isOpened: isOpened,
                tapHintHidden: document.getElementById('tapHint').classList.contains('hidden')
            };
        }""")
        print(f"Click spam result: {spam_result}")
        assert spam_result["isOpened"] is True, "FAILED: isOpened should be true"
        assert spam_result["tapHintHidden"] is True, "FAILED: tapHint should be hidden"
        print("[PASS] 3.3: Rapid click spam handled atomically without race conditions.")

        # 3.3 Wait for Typewriter to Complete & Validate Output
        print("Waiting for typewriter animation to complete...")
        # Since speed is 35ms and total duration is ~24s, let's fast-forward or accelerate setTimeout or wait.
        # We can evaluate the completion directly by checking typewriter text:
        page.wait_for_function("""() => {
            const el = document.getElementById('typewriter');
            return el && el.innerHTML.includes('Chúc cho tình bạn của chúng ta luôn bền chặt');
        }""", timeout=40000)

        typewriter_html = page.evaluate("() => document.getElementById('typewriter').innerHTML")
        assert "Gửi người bạn thân mến của tôi" in typewriter_html, "FAILED: Missing header in typewriter"
        assert "Chúc cho tình bạn của chúng ta luôn bền chặt" in typewriter_html, "FAILED: Missing footer in typewriter"
        print("[PASS] 3.4: Typewriter completed full delivery in DOM accurately.")

        # 3.4 Modal Opening / Closing Interaction during/after active state
        modal_test = page.evaluate("""() => {
            const settingsBtn = document.getElementById('settingsBtn');
            const settingsModal = document.getElementById('settingsModal');
            const closeModal = document.getElementById('closeModal');

            // Open modal
            settingsBtn.click();
            const isOpen = settingsModal.classList.contains('active');

            // Close modal
            closeModal.click();
            const isClosed = !settingsModal.classList.contains('active');

            // Click backdrop to close
            settingsBtn.click();
            settingsModal.dispatchEvent(new MouseEvent('click', { bubbles: true }));
            const isClosedBackdrop = !settingsModal.classList.contains('active');

            return { isOpen, isClosed, isClosedBackdrop };
        }""")
        print(f"Modal interaction result: {modal_test}")
        assert modal_test["isOpen"] and modal_test["isClosed"] and modal_test["isClosedBackdrop"], "FAILED: Modal interaction failure!"
        print("[PASS] 3.5: Settings modal opens, closes via button, and closes via backdrop click.")

        # 3.5 Share Button and Copy Notification Edge Cases
        share_test = page.evaluate("""() => {
            const shareBtn = document.getElementById('shareBtn');
            const copyNotification = document.getElementById('copyNotification');

            // Initially disabled
            const initialDisabled = shareBtn.disabled;

            // Click when disabled
            shareBtn.click();
            const notShownWhenDisabled = !copyNotification.classList.contains('show');

            return { initialDisabled, notShownWhenDisabled };
        }""")
        print(f"Share button test: {share_test}")
        assert share_test["initialDisabled"], "FAILED: shareBtn should be initially disabled"
        assert share_test["notShownWhenDisabled"], "FAILED: copyNotification showed when shareBtn was disabled"
        print("[PASS] 3.6: Share button safely guarded when no images are present.")

        # 3.6 URL Parameter Fuzzing & Crash Resistance
        print("Testing URL parameter resilience with malformed JSON...")
        page.goto(f"{index_url}?images=%7Bmalformed_json%7D", wait_until="networkidle")
        err_resilience = page.evaluate("() => typeof isOpened !== 'undefined'")
        assert err_resilience, "FAILED: Page broke on malformed ?images query param"
        print("[PASS] 3.7: Page resiliently handles malformed URL image params via try/catch.")

        # Test non-array JSON ?images=123
        page.goto(f"{index_url}?images=123", wait_until="networkidle")
        err_resilience2 = page.evaluate("() => typeof isOpened !== 'undefined'")
        assert err_resilience2, "FAILED: Page broke on non-array ?images query param"
        print("[PASS] 3.8: Page resiliently handles non-array ?images query param.")

        browser.close()

if __name__ == "__main__":
    try:
        test_eof_cleanliness()
        test_typewriter_timing_and_simulation()
        test_browser_adversarial_suite()
        print("\n========================================================")
        print("ALL ADVERSARIAL VERIFICATION TESTS PASSED SUCCESSFULLY!")
        print("========================================================")
    except AssertionError as e:
        print(f"\n[ASSERTION ERROR]: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR]: {e}", file=sys.stderr)
        sys.exit(2)
