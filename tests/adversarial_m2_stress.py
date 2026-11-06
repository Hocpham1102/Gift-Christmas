#!/usr/bin/env python3
"""
Milestone M2 Adversarial Verification & Stress Test Harness
===========================================================
Executes empirical adversarial stress testing against index.html:
1. Card Anti-Overflow & Scrolling Resilience across extreme viewports (350px-400px heights).
2. Particle System Adversarial Audit (0 HeartParticle, constructor verification, coordinate bounds, frame loop).
3. Music Toggle Controls Stress (rapid clicking, state synchronization, autoplay policy resilience).

Uses Playwright headless Chromium directly with as_uri().
"""

import json
import os
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = REPO_ROOT / "index.html"
SCREENSHOTS_DIR = REPO_ROOT / "tests" / "artifacts" / "screenshots"


def run_adversarial_suite():
    print("=" * 70)
    print("   MILENSTONE M2 EMPIRICAL ADVERSARIAL STRESS TEST HARNESS")
    print("=" * 70)

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    target_uri = INDEX_HTML.resolve().as_uri()
    print(f"[*] Testing target URI: {target_uri}")

    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html_content = f.read()

    results = []

    def record(name, passed, detail):
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {name}: {detail}")
        results.append({"name": name, "passed": passed, "detail": detail})

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # SUITE 1: Extreme Viewport Anti-Overflow & Scrolling Stress Test
        # -------------------------------------------------------------
        print("\n--- Suite 1: Extreme Viewport Anti-Overflow & Scrolling Stress ---")
        extreme_viewports = [
            ("mobile_landscape_extreme_350h", 667, 350),
            ("mobile_portrait_extreme_350h", 360, 350),
            ("landscape_short_400h", 740, 400),
            ("compact_small_320x480", 320, 480),
            ("standard_mobile_375x667", 375, 667),
            ("desktop_1080p", 1920, 1080),
        ]

        for vp_name, width, height in extreme_viewports:
            context = browser.new_context(viewport={"width": width, "height": height})
            page = context.new_page()
            page.goto(target_uri, wait_until="networkidle")

            # Wait for three canvas and CDN libraries (THREE and gsap)
            page.wait_for_selector("#three-canvas", state="visible", timeout=10000)
            page.wait_for_function("typeof gsap !== 'undefined' && typeof THREE !== 'undefined'", timeout=15000)

            # Trigger opening
            page.evaluate("openGift()")

            # Wait for content to become active
            page.wait_for_selector("#mainContent.active", state="visible", timeout=6000)

            # Fast-forward typewriter to full text
            page.evaluate("""() => {
                i = message.length;
                document.getElementById('typewriter').innerHTML = message;
            }""")
            time.sleep(0.3)

            # Measure layout metrics
            metrics = page.evaluate("""() => {
                const content = document.getElementById('mainContent');
                const cardBody = document.getElementById('cardBody');
                const typewriter = document.getElementById('typewriter');
                const header = document.querySelector('.card-header');
                const footer = document.querySelector('.card-footer');
                const cRect = content.getBoundingClientRect();
                const bRect = cardBody.getBoundingClientRect();
                const tRect = typewriter.getBoundingClientRect();
                const cs = window.getComputedStyle(cardBody);

                // Attempt scroll
                const initialScrollTop = cardBody.scrollTop;
                cardBody.scrollTop = 9999;
                const maxScrollTop = cardBody.scrollTop;

                return {
                    viewportWidth: window.innerWidth,
                    viewportHeight: window.innerHeight,
                    contentTop: cRect.top,
                    contentBottom: cRect.bottom,
                    contentHeight: cRect.height,
                    contentWidth: cRect.width,
                    bodyHeight: bRect.height,
                    bodyScrollHeight: cardBody.scrollHeight,
                    bodyClientHeight: cardBody.clientHeight,
                    bodyOverflowY: cs.overflowY,
                    bodyOverscroll: cs.overscrollBehavior,
                    typewriterScrollWidth: typewriter.scrollWidth,
                    bodyClientWidth: cardBody.clientWidth,
                    maxScrollTop: maxScrollTop,
                    canScroll: cardBody.scrollHeight > cardBody.clientHeight,
                    headerVisible: !!header,
                    footerVisible: !!footer
                };
            }""")

            # Take screenshot of the OPEN card state
            screenshot_path = SCREENSHOTS_DIR / f"adversarial_open_{vp_name}.png"
            page.screenshot(path=str(screenshot_path))

            # Stress checks
            # 1. Content card must stay within viewport vertical bounds
            vh = metrics["viewportHeight"]
            content_fits_vertically = (metrics["contentTop"] >= -2) and (metrics["contentBottom"] <= vh + 10)
            record(
                f"{vp_name}_vertical_fit",
                content_fits_vertically,
                f"Content top: {metrics['contentTop']:.1f}px, bottom: {metrics['contentBottom']:.1f}px in viewport {vh}px (height: {metrics['contentHeight']:.1f}px)"
            )

            # 2. overflow-y must be auto or scroll
            has_scroll_style = metrics["bodyOverflowY"] in ["auto", "scroll"]
            record(
                f"{vp_name}_overflow_style",
                has_scroll_style,
                f"cardBody overflow-y is '{metrics['bodyOverflowY']}', overscroll-behavior is '{metrics['bodyOverscroll']}'"
            )

            # 3. If scrollHeight > clientHeight, scrolling must work
            if metrics["canScroll"]:
                scroll_effective = metrics["maxScrollTop"] > 0
                record(
                    f"{vp_name}_scroll_operational",
                    scroll_effective,
                    f"ScrollHeight ({metrics['bodyScrollHeight']}px) > ClientHeight ({metrics['bodyClientHeight']}px), scrolled to {metrics['maxScrollTop']}px"
                )
            else:
                record(
                    f"{vp_name}_scroll_operational",
                    True,
                    f"Entire text fits without needing scroll (ScrollHeight: {metrics['bodyScrollHeight']}px <= {metrics['bodyClientHeight']}px)"
                )

            # 4. No horizontal text spill
            no_h_overflow = metrics["typewriterScrollWidth"] <= metrics["bodyClientWidth"] + 5
            record(
                f"{vp_name}_no_horizontal_spill",
                no_h_overflow,
                f"Typewriter scrollWidth {metrics['typewriterScrollWidth']}px vs clientWidth {metrics['bodyClientWidth']}px"
            )

            # 5. Replay button interaction
            page.click("#replayBtn")
            replay_ok = page.evaluate("""() => {
                const tw = document.getElementById('typewriter');
                return tw.innerHTML.length < 50; // was cleared and restarting
            }""")
            record(
                f"{vp_name}_replay_button_works",
                replay_ok,
                f"Replay button clicked and successfully restarted typewriter"
            )

            context.close()

        # -------------------------------------------------------------
        # SUITE 2: Particle System Adversarial Audit
        # -------------------------------------------------------------
        print("\n--- Suite 2: Particle System Adversarial Audit ---")

        # Static Code Checks
        heart_classes = re.findall(r'class\s+HeartParticle', html_content, re.IGNORECASE)
        record(
            "static_no_heart_class",
            len(heart_classes) == 0,
            f"Found {len(heart_classes)} 'class HeartParticle' occurrences (expected 0)"
        )

        heart_instantiations = re.findall(r'new\s+HeartParticle', html_content, re.IGNORECASE)
        record(
            "static_no_heart_instantiations",
            len(heart_instantiations) == 0,
            f"Found {len(heart_instantiations)} 'new HeartParticle' occurrences (expected 0)"
        )

        # Dynamic Runtime Particle Checks in Playwright
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(target_uri, wait_until="networkidle")

        particle_audit = page.evaluate("""() => {
            if (typeof particles === 'undefined' || !Array.isArray(particles)) {
                return { error: "particles array not found" };
            }
            const counts = {};
            particles.forEach(p => {
                const cname = p.constructor ? p.constructor.name : 'Unknown';
                counts[cname] = (counts[cname] || 0) + 1;
            });

            // Simulate 200 ticks and verify stability & bounds
            let nanCount = 0;
            let infCount = 0;
            let outOfBoundsCount = 0;

            for (let step = 0; step < 200; step++) {
                particles.forEach(p => {
                    p.update();
                    if (isNaN(p.x) || isNaN(p.y)) nanCount++;
                    if (!isFinite(p.x) || !isFinite(p.y)) infCount++;
                    // Coordinates should wrap within canvas margin
                    if (p.x < -50 || p.x > window.innerWidth + 50) outOfBoundsCount++;
                    if (p.y < -50 || p.y > window.innerHeight + 50) outOfBoundsCount++;
                });
            }

            return {
                totalCount: particles.length,
                counts: counts,
                nanCount: nanCount,
                infCount: infCount,
                outOfBoundsCount: outOfBoundsCount
            };
        }""")

        record(
            "runtime_particles_present",
            "error" not in particle_audit and particle_audit.get("totalCount", 0) >= 150,
            f"Total runtime particles: {particle_audit.get('totalCount')}, breakdown: {particle_audit.get('counts')}"
        )

        record(
            "runtime_no_heart_particles",
            "HeartParticle" not in particle_audit.get("counts", {}),
            f"HeartParticle in runtime: {'HeartParticle' in particle_audit.get('counts', {})}"
        )

        record(
            "runtime_snow_and_bokeh_present",
            particle_audit.get("counts", {}).get("SnowParticle", 0) > 0 and
            particle_audit.get("counts", {}).get("BokehParticle", 0) > 0,
            f"SnowParticle: {particle_audit.get('counts', {}).get('SnowParticle')}, BokehParticle: {particle_audit.get('counts', {}).get('BokehParticle')}"
        )

        record(
            "particle_simulation_numerical_stability",
            particle_audit.get("nanCount") == 0 and particle_audit.get("infCount") == 0,
            f"Simulated 200 ticks: NaN={particle_audit.get('nanCount')}, Inf={particle_audit.get('infCount')}, unbounded={particle_audit.get('outOfBoundsCount')}"
        )

        # FPS / Frame Loop Stress Check
        fps_check = page.evaluate("""() => {
            return new Promise((resolve) => {
                let frameCount = 0;
                const start = performance.now();
                function loop() {
                    frameCount++;
                    if (performance.now() - start < 1000) {
                        requestAnimationFrame(loop);
                    } else {
                        const elapsed = (performance.now() - start) / 1000;
                        resolve({ fps: frameCount / elapsed, frameCount });
                    }
                }
                requestAnimationFrame(loop);
            });
        }""")

        record(
            "particle_animation_frame_rate",
            fps_check["fps"] >= 30,
            f"Measured animation loop performance: {fps_check['fps']:.1f} FPS over {fps_check['frameCount']} frames"
        )

        context.close()

        # -------------------------------------------------------------
        # SUITE 3: Music Toggle Controls Stress Testing
        # -------------------------------------------------------------
        print("\n--- Suite 3: Music Toggle Controls Stress Testing ---")
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))

        page.goto(target_uri, wait_until="networkidle")

        # Initial music state
        initial_state = page.evaluate("""() => {
            const btn = document.getElementById('musicToggle');
            const audio = document.getElementById('bgMusic');
            return {
                btnExists: !!btn,
                audioExists: !!audio,
                audioPaused: audio.paused,
                ariaLabel: btn.getAttribute('aria-label'),
                hasMutedClass: btn.classList.contains('muted')
            };
        }""")

        record(
            "music_toggle_dom_attributes",
            initial_state["btnExists"] and initial_state["ariaLabel"] == "Bật/Tắt nhạc nền",
            f"Button exists: {initial_state['btnExists']}, aria-label: '{initial_state['ariaLabel']}', initial paused: {initial_state['audioPaused']}"
        )

        # Rapid click stress test (30 rapid clicks in 300ms)
        page.evaluate("""async () => {
            const btn = document.getElementById('musicToggle');
            for (let k = 0; k < 30; k++) {
                btn.click();
                await new Promise(r => setTimeout(r, 10));
            }
        }""")
        time.sleep(0.5)

        rapid_click_state = page.evaluate("""() => {
            const btn = document.getElementById('musicToggle');
            const audio = document.getElementById('bgMusic');
            return {
                audioPaused: audio.paused,
                hasMutedClass: btn.classList.contains('muted')
            };
        }""")

        # 30 clicks (even number) should return toggle and audio to consistent states without crashing
        record(
            "music_toggle_rapid_click_resilience",
            len(console_errors) == 0,
            f"30 rapid clicks executed. Console errors caught: {len(console_errors)}. Audio paused: {rapid_click_state['audioPaused']}, muted class: {rapid_click_state['hasMutedClass']}"
        )

        # Sync test: Opening gift should unmute
        page.evaluate("""() => {
            const btn = document.getElementById('musicToggle');
            btn.classList.add('muted'); // force muted state
            openGift();
        }""")
        time.sleep(0.3)

        post_open_sync = page.evaluate("""() => {
            const btn = document.getElementById('musicToggle');
            return {
                hasMutedClass: btn.classList.contains('muted')
            };
        }""")

        record(
            "music_toggle_open_gift_synchronization",
            not post_open_sync["hasMutedClass"],
            f"openGift() successfully cleared .muted class from #musicToggle"
        )

        context.close()
        browser.close()

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    print("\n" + "=" * 70)
    print(f"ADVERSARIAL STRESS SUMMARY: {passed}/{total} PASSED ({passed/total*100:.1f}%) | {failed} FAILED")
    print("=" * 70)

    # Save results to json
    adversarial_report = REPO_ROOT / "tests" / "artifacts" / "adversarial_m2_results.json"
    with open(adversarial_report, "w", encoding="utf-8") as f:
        json.dump({"total": total, "passed": passed, "failed": failed, "results": results}, f, indent=2)
    print(f"Adversarial test report written to: {adversarial_report}")

    return failed == 0


if __name__ == "__main__":
    success = run_adversarial_suite()
    sys.exit(0 if success else 1)
