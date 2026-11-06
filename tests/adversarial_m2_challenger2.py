#!/usr/bin/env python3
"""
Adversarial Verification Suite for Milestone M2 - Challenger 2
==============================================================
Empirical stress-testing of M2 interaction safety:
1. Audio edge cases & state machine (#musicToggle vs openGift)
2. Replay button concurrency & mid-typing race conditions (#replayBtn)
3. Reduced-motion graceful degradation (@media prefers-reduced-motion)
4. Layout resilience & scroll container bounds across mobile viewports
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

INDEX_PATH = Path("index.html").resolve()
INDEX_URI = INDEX_PATH.as_uri()

def print_header(title):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def test_audio_edge_cases():
    print_header("TEST 1: Audio Edge Cases & State Machine")
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(INDEX_URI)
        page.wait_for_load_state("load")

        # Initial state before any interaction
        bg_paused = page.evaluate("document.getElementById('bgMusic').paused")
        toggle_classes = page.evaluate("document.getElementById('musicToggle').className")
        print(f"Initial bgMusic.paused: {bg_paused}")
        print(f"Initial musicToggle.className: '{toggle_classes}'")

        # Edge Case 1.1: Click #musicToggle BEFORE opening gift box
        page.click("#musicToggle")
        page.wait_for_timeout(300)
        paused_after_toggle1 = page.evaluate("document.getElementById('bgMusic').paused")
        classes_after_toggle1 = page.evaluate("document.getElementById('musicToggle').className")
        print(f"After #musicToggle click (before openGift): paused={paused_after_toggle1}, class='{classes_after_toggle1}'")
        results["music_toggle_pre_open_play"] = (paused_after_toggle1 is False and "muted" not in classes_after_toggle1)

        # Edge Case 1.2: Click #musicToggle AGAIN before opening gift box (to mute/pause)
        page.click("#musicToggle")
        page.wait_for_timeout(300)
        paused_after_toggle2 = page.evaluate("document.getElementById('bgMusic').paused")
        classes_after_toggle2 = page.evaluate("document.getElementById('musicToggle').className")
        print(f"After 2nd #musicToggle click (muted): paused={paused_after_toggle2}, class='{classes_after_toggle2}'")
        results["music_toggle_pre_open_mute"] = (paused_after_toggle2 is True and "muted" in classes_after_toggle2)

        # Edge Case 1.3: Now open gift box while music was explicitly muted by user
        page.evaluate("openGift()")
        page.wait_for_timeout(500)
        paused_after_open = page.evaluate("document.getElementById('bgMusic').paused")
        classes_after_open = page.evaluate("document.getElementById('musicToggle').className")
        print(f"After openGift(): paused={paused_after_open}, class='{classes_after_open}'")
        results["open_gift_unmutes_music"] = (paused_after_open is False and "muted" not in classes_after_open)

        # Edge Case 1.4: Click #musicToggle after box opened (toggle pause)
        page.click("#musicToggle")
        page.wait_for_timeout(300)
        paused_after_post_toggle = page.evaluate("document.getElementById('bgMusic').paused")
        classes_after_post_toggle = page.evaluate("document.getElementById('musicToggle').className")
        print(f"After #musicToggle post-open click: paused={paused_after_post_toggle}, class='{classes_after_post_toggle}'")
        results["post_open_pause"] = (paused_after_post_toggle is True and "muted" in classes_after_post_toggle)

        # Edge Case 1.5: Rapid clicking #musicToggle 10 times
        print("Testing rapid clicking #musicToggle (10 clicks)...")
        for _ in range(10):
            page.click("#musicToggle")
            page.wait_for_timeout(50)
        rapid_paused = page.evaluate("document.getElementById('bgMusic').paused")
        rapid_classes = page.evaluate("document.getElementById('musicToggle').className")
        print(f"After 10 rapid clicks: paused={rapid_paused}, class='{rapid_classes}'")
        sync_ok = (rapid_paused and "muted" in rapid_classes) or (not rapid_paused and "muted" not in rapid_classes)
        print(f"Audio state & DOM class in sync: {sync_ok}")
        results["rapid_audio_toggle_sync"] = sync_ok

        browser.close()

    return results

def test_replay_button_concurrency():
    print_header("TEST 2: Replay Button & Typewriter Concurrency")
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(INDEX_URI)
        page.wait_for_load_state("load")

        # Scenario 2.1: Replay after mid-typing click
        print("Testing replayBtn clicked mid-typing...")
        res_mid = page.evaluate("""() => {
            return new Promise((resolve) => {
                openGift();
                const checkMid = setInterval(() => {
                    if (i >= 25) {
                        clearInterval(checkMid);
                        // Trigger mid-typing replay
                        document.getElementById('replayBtn').click();
                        
                        // Wait until typing completely finishes
                        const checkDone = setInterval(() => {
                            if (i >= message.length) {
                                clearInterval(checkDone);
                                const rendered = document.getElementById('typewriter').innerText;
                                const cleanMsg = message.replace(/<br>/g, '\\n');
                                resolve({
                                    match: rendered === cleanMsg,
                                    renderedLen: rendered.length,
                                    cleanMsgLen: cleanMsg.length
                                });
                            }
                        }, 100);
                    }
                }, 50);
            });
        }""")
        print(f"Mid-typing replay result: {res_mid}")
        results["mid_typing_replay_integrity"] = res_mid["match"]

        # Scenario 2.2: Replay after full completion
        print("Testing replayBtn clicked after completion...")
        res_post = page.evaluate("""() => {
            return new Promise((resolve) => {
                // Click replay when already complete
                document.getElementById('replayBtn').click();
                const checkDone = setInterval(() => {
                    if (i >= message.length) {
                        clearInterval(checkDone);
                        const rendered = document.getElementById('typewriter').innerText;
                        const cleanMsg = message.replace(/<br>/g, '\\n');
                        resolve({
                            match: rendered === cleanMsg,
                            renderedLen: rendered.length,
                            cleanMsgLen: cleanMsg.length
                        });
                    }
                }, 100);
            });
        }""")
        print(f"Post-completion replay result: {res_post}")
        results["post_completion_replay_integrity"] = res_post["match"]

        # Scenario 2.3: Rapid spam clicking replayBtn (5 clicks while typing)
        print("Testing rapid 5 clicks spam on replayBtn...")
        res_spam = page.evaluate("""() => {
            return new Promise((resolve) => {
                // Click 5 times in rapid succession
                for (let k = 0; k < 5; k++) {
                    document.getElementById('replayBtn').click();
                }
                const checkDone = setInterval(() => {
                    if (i >= message.length) {
                        clearInterval(checkDone);
                        const rendered = document.getElementById('typewriter').innerText;
                        const cleanMsg = message.replace(/<br>/g, '\\n');
                        resolve({
                            match: rendered === cleanMsg,
                            renderedLen: rendered.length,
                            cleanMsgLen: cleanMsg.length
                        });
                    }
                }, 100);
            });
        }""")
        print(f"Spam replay result: {res_spam}")
        results["rapid_replay_spam_integrity"] = res_spam["match"]

        browser.close()

    return results

def test_reduced_motion():
    print_header("TEST 3: Reduced Motion Graceful Degradation")
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Context with prefers-reduced-motion: reduce
        context = browser.new_context(reduced_motion="reduce")
        page = context.new_page()
        page.goto(INDEX_URI)
        page.wait_for_load_state("load")

        # 3.1 Check CSS media query matches
        matches_reduced_motion = page.evaluate("window.matchMedia('(prefers-reduced-motion: reduce)').matches")
        print(f"window.matchMedia('(prefers-reduced-motion: reduce)').matches: {matches_reduced_motion}")
        results["media_query_matched"] = matches_reduced_motion

        # 3.2 Check animation-duration on animated elements
        music_icon_duration = page.evaluate("""() => {
            const el = document.getElementById('musicIcon');
            return window.getComputedStyle(el).animationDuration;
        }""")
        print(f"#musicIcon computed animationDuration under reduced-motion: {music_icon_duration}")
        results["animation_duration_reduced"] = (music_icon_duration in ["0.00001s", "0.01ms", "1e-05s", "0s"])

        # 3.3 Check transition-duration
        music_btn_transition = page.evaluate("""() => {
            const el = document.getElementById('musicToggle');
            return window.getComputedStyle(el).transitionDuration;
        }""")
        print(f"#musicToggle computed transitionDuration under reduced-motion: {music_btn_transition}")
        results["transition_duration_reduced"] = (music_btn_transition in ["0.00001s", "0.01ms", "1e-05s", "0s"])

        # 3.4 Verify interaction still works under reduced motion (openGift + typewriter)
        page.evaluate("openGift()")
        page.wait_for_timeout(1500)
        typewriter_text = page.evaluate("document.getElementById('typewriter').innerHTML")
        print(f"Typewriter active under reduced-motion (len: {len(typewriter_text)}): '{typewriter_text[:40]}...'")
        results["functionality_intact_under_reduced_motion"] = (len(typewriter_text) > 0)

        browser.close()

    return results

def test_layout_resilience():
    print_header("TEST 4: Layout Resilience & Mobile Scroll Bounds")
    results = {}

    viewports = [
        ("Mobile 375x667", {"width": 375, "height": 667}),
        ("Tablet 768x1024", {"width": 768, "height": 1024}),
        ("Desktop 1920x1080", {"width": 1920, "height": 1080}),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, vp in viewports:
            context = browser.new_context(viewport=vp)
            page = context.new_page()
            page.goto(INDEX_URI)
            page.wait_for_load_state("load")

            page.evaluate("openGift()")
            page.wait_for_timeout(1500)

            # Check cardBody scroll properties
            card_metrics = page.evaluate("""() => {
                const cb = document.getElementById('cardBody');
                const content = document.getElementById('mainContent');
                const style = window.getComputedStyle(cb);
                return {
                    overflowY: style.overflowY,
                    overscrollBehavior: style.overscrollBehavior,
                    scrollHeight: cb.scrollHeight,
                    clientHeight: cb.clientHeight,
                    contentHeight: content.clientHeight,
                    windowHeight: window.innerHeight
                };
            }""")
            print(f"[{name}] cardBody metrics: {card_metrics}")
            
            # Constraints:
            # 1. overflow-y must be auto or scroll
            # 2. contentHeight <= windowHeight (no offscreen clipping)
            overflow_ok = card_metrics["overflowY"] in ["auto", "scroll"]
            height_bounded = card_metrics["contentHeight"] <= card_metrics["windowHeight"]
            results[f"{name}_overflow_scrollable"] = overflow_ok
            results[f"{name}_height_bounded"] = height_bounded

            context.close()
        browser.close()

    return results

if __name__ == "__main__":
    t1_res = test_audio_edge_cases()
    t2_res = test_replay_button_concurrency()
    t3_res = test_reduced_motion()
    t4_res = test_layout_resilience()

    print_header("FINAL ADVERSARIAL TEST SUMMARY")
    all_passed = True
    for group_name, group_res in [("Audio Edge Cases", t1_res), 
                                   ("Replay Concurrency", t2_res), 
                                   ("Reduced Motion", t3_res),
                                   ("Layout Resilience", t4_res)]:
        print(f"\n[{group_name}]")
        for k, v in group_res.items():
            status = "PASS" if v else "FAIL"
            print(f"  [{status}] {k}: {v}")
            if not v:
                all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("OVERALL VERDICT: ALL ADVERSARIAL TESTS PASSED (APPROVE)")
        sys.exit(0)
    else:
        print("OVERALL VERDICT: ADVERSARIAL FAILURES FOUND (REQUEST_CHANGES)")
        sys.exit(1)
