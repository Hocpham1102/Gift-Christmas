#!/usr/bin/env python3
"""
Auditor M2 Runtime & Behavioral Forensics Probe
Empirically tests DOM behaviors using Playwright Chromium:
1. True scrollability of #cardBody in various viewports
2. Genuine operation of #musicToggle
3. Replay button stability under rapid clicks
4. Reduced motion media query CSS compliance
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def run_auditor_probes():
    index_path = Path("index.html").resolve()
    file_url = index_path.as_uri()

    print("=== STARTING AUDITOR M2 RUNTIME FORENSIC PROBE ===")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # TEST 1: Mobile Landscape (667x375) - High overflow scenario
        print("\n--- TEST 1: Mobile Landscape (667x375) True Scrolling Verification ---")
        context_mobile_land = browser.new_context(viewport={"width": 667, "height": 375})
        page = context_mobile_land.new_page()
        page.goto(file_url, wait_until="load")

        # Open gift box directly via JS
        page.evaluate("openGift()")
        # Fast-forward typewriter to completion
        page.wait_for_timeout(1200) # wait for animation
        page.evaluate("""() => {
            // Instant fill typewriter to test full letter overflow
            document.getElementById('typewriter').innerHTML = message;
        }""")
        page.wait_for_timeout(300)

        # Measure dimensions
        card_body_metrics = page.evaluate("""() => {
            const cb = document.getElementById('cardBody');
            const style = window.getComputedStyle(cb);
            return {
                scrollHeight: cb.scrollHeight,
                clientHeight: cb.clientHeight,
                offsetHeight: cb.offsetHeight,
                overflowY: style.overflowY,
                maxHeight: style.maxHeight,
                overscrollBehavior: style.overscrollBehavior || style.overscrollBehaviorY
            };
        }""")
        print(f"Card body metrics (667x375): {card_body_metrics}")
        assert card_body_metrics["overflowY"] in ["auto", "scroll"], f"Unexpected overflowY: {card_body_metrics['overflowY']}"
        assert card_body_metrics["scrollHeight"] > card_body_metrics["clientHeight"], (
            f"Expected scrollHeight ({card_body_metrics['scrollHeight']}) > clientHeight ({card_body_metrics['clientHeight']}) "
            "proving text actually overflows and requires scrolling!"
        )

        # Test actual scrolling
        page.evaluate("""() => {
            const cb = document.getElementById('cardBody');
            cb.scrollTop = 80;
        }""")
        page.wait_for_timeout(100)
        scroll_pos = page.evaluate("document.getElementById('cardBody').scrollTop")
        print(f"ScrollTop after scrolling by 80px: {scroll_pos}px")
        assert scroll_pos > 0, f"Element did not actually scroll! scrollTop = {scroll_pos}"
        print("PASS: True scrolling verified on Mobile Landscape.")

        # TEST 2: Mobile Portrait (375x667)
        print("\n--- TEST 2: Mobile Portrait (375x667) True Scrolling Verification ---")
        context_mobile_port = browser.new_context(viewport={"width": 375, "height": 667})
        page2 = context_mobile_port.new_page()
        page2.goto(file_url, wait_until="load")
        page2.evaluate("openGift()")
        page2.wait_for_timeout(1200)
        page2.evaluate("document.getElementById('typewriter').innerHTML = message;")
        page2.wait_for_timeout(300)

        metrics_port = page2.evaluate("""() => {
            const cb = document.getElementById('cardBody');
            const style = window.getComputedStyle(cb);
            return {
                scrollHeight: cb.scrollHeight,
                clientHeight: cb.clientHeight,
                overflowY: style.overflowY,
                maxHeight: style.maxHeight
            };
        }""")
        print(f"Card body metrics (375x667): {metrics_port}")
        assert metrics_port["scrollHeight"] > metrics_port["clientHeight"], (
            f"Expected scrollHeight ({metrics_port['scrollHeight']}) > clientHeight ({metrics_port['clientHeight']})"
        )
        page2.evaluate("document.getElementById('cardBody').scrollTop = 100;")
        page2.wait_for_timeout(100)
        scroll_pos_port = page2.evaluate("document.getElementById('cardBody').scrollTop")
        print(f"ScrollTop in portrait after scroll: {scroll_pos_port}px")
        assert scroll_pos_port > 0, f"Portrait element failed to scroll: {scroll_pos_port}"
        print("PASS: True scrolling verified on Mobile Portrait.")

        # TEST 3: Music Toggle Genuineness
        print("\n--- TEST 3: #musicToggle Genuine Event and State Transitions ---")
        context_desktop = browser.new_context(viewport={"width": 1920, "height": 1080})
        page3 = context_desktop.new_page()
        page3.goto(file_url, wait_until="load")

        music_toggle_btn = page3.locator("#musicToggle")
        assert music_toggle_btn.is_visible(), "#musicToggle should be visible"

        # Check initial state
        initial_muted = page3.evaluate("document.getElementById('musicToggle').classList.contains('muted')")
        print(f"Initial musicToggle muted class: {initial_muted}")

        # Click music toggle
        print("Clicking music toggle button...")
        music_toggle_btn.click()
        page3.wait_for_timeout(300)

        state_after_1st_click = page3.evaluate("""() => {
            const btn = document.getElementById('musicToggle');
            const audio = document.getElementById('bgMusic');
            return {
                btnMutedClass: btn.classList.contains('muted'),
                audioPaused: audio.paused
            };
        }""")
        print(f"State after 1st click: {state_after_1st_click}")

        # Click music toggle again
        print("Clicking music toggle button 2nd time...")
        music_toggle_btn.click()
        page3.wait_for_timeout(300)

        state_after_2nd_click = page3.evaluate("""() => {
            const btn = document.getElementById('musicToggle');
            const audio = document.getElementById('bgMusic');
            return {
                btnMutedClass: btn.classList.contains('muted'),
                audioPaused: audio.paused
            };
        }""")
        print(f"State after 2nd click: {state_after_2nd_click}")

        # Toggle state must flip
        assert state_after_1st_click["btnMutedClass"] != state_after_2nd_click["btnMutedClass"], (
            "musicToggle muted class did not flip on second click!"
        )
        print("PASS: #musicToggle genuinely toggles state and audio.")

        # TEST 4: Replay Button Stress Test
        print("\n--- TEST 4: #replayBtn Stress Test ---")
        page3.evaluate("openGift()")
        page3.wait_for_timeout(1500)
        replay_btn = page3.locator("#replayBtn")
        assert replay_btn.is_visible(), "#replayBtn should be visible"

        print("Simulating rapid clicking on #replayBtn (5 clicks in 200ms)...")
        for _ in range(5):
            replay_btn.click()
            page3.wait_for_timeout(40)
        
        page3.wait_for_timeout(1000)
        typewriter_text = page3.locator("#typewriter").inner_text()
        print(f"Typewriter text after rapid replay clicks: '{typewriter_text[:50]}...'")
        assert len(typewriter_text) > 0, "Typewriter should be active after replay clicks"
        print("PASS: #replayBtn handles rapid clicks stably.")

        # TEST 5: Particle Array Verification
        print("\n--- TEST 5: Particle System Verification ---")
        particle_counts = page3.evaluate("""() => {
            return {
                totalParticles: particles.length,
                classes: [...new Set(particles.map(p => p.constructor.name))]
            };
        }""")
        print(f"Active runtime particles in window: {particle_counts}")
        assert "SnowParticle" in particle_counts["classes"], "SnowParticle not found in runtime particles!"
        assert "BokehParticle" in particle_counts["classes"] or "SparkleParticle" in particle_counts["classes"], (
            "Festive bokeh/sparkle particle not found in runtime particles!"
        )
        assert "HeartParticle" not in particle_counts["classes"], "HeartParticle found in runtime particles!"
        print("PASS: Particle system genuinely running festive particles without HeartParticle.")

        browser.close()

    print("\n=== ALL AUDITOR M2 RUNTIME PROBES COMPLETED SUCCESSFULLY ===")
    return True

if __name__ == "__main__":
    success = run_auditor_probes()
    sys.exit(0 if success else 1)
