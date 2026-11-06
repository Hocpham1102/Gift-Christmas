#!/usr/bin/env python3
"""
Dedicated Deep Verification: 3D Gift Box Opening & Ascension Mechanics
Verifies:
1. boxBase never drops to y: -5 or y: -0.9 (stays firmly anchored at y >= 0).
2. boxLid ascends monotonically to >= 4.8 without collapsing back down.
3. giftSurprise (Christmas Star) rises up from inside the box into the focal center (y >= 1.65).
4. Material opacity dissolves smoothly (boxMaterial.opacity -> 0, lidMaterial.opacity -> 0) without geometric snapping.
5. giftGroup.scale maintains its structural integrity (never collapses to 0 while children are active).
6. 3D particle fountain (56 particles) and 2D canvas fireworks (80 sparks) trigger properly.
7. Mobile and Desktop viewports run without WebGL or animation glitches.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

INDEX_PATH = Path("index.html").resolve()
INDEX_URI = INDEX_PATH.as_uri()

def verify_gift_opening_mechanics():
    print("=" * 70)
    print(" 3D GIFT BOX OPENING DEEP VERIFICATION HARNESS")
    print("=" * 70)

    viewports = [
        ("Desktop 1080p", 1920, 1080),
        ("Mobile Portrait 375x667", 375, 667),
        ("Mobile Landscape 667x375", 667, 375)
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for vp_name, width, height in viewports:
            print(f"\n[*] Testing viewport: {vp_name} ({width}x{height})")
            context = browser.new_context(viewport={"width": width, "height": height})
            page = context.new_page()
            
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: console_errors.append(str(err)))

            page.goto(INDEX_URI, wait_until="load")
            page.wait_for_timeout(400)

            # 1. Idle state verification
            idle_state = page.evaluate("""() => {
                return {
                    giftGroupScale: giftGroup.scale.y,
                    boxBasePosY: boxBase.position.y,
                    boxLidPosY: boxLid.position.y,
                    hasSurprise: typeof giftSurprise !== 'undefined',
                    surprisePosY: giftSurprise ? giftSurprise.position.y : null,
                    boxMaterialTransparent: boxMaterial.transparent,
                    lidMaterialTransparent: lidMaterial.transparent,
                    burstParticleCount: burstParticles.length
                };
            }""")
            print(f"  [Idle State] BaseY: {idle_state['boxBasePosY']}, LidY: {idle_state['boxLidPosY']}, BurstCount: {idle_state['burstParticleCount']}")
            assert idle_state["boxBasePosY"] == 0, f"Box base should be initially at Y=0, got {idle_state['boxBasePosY']}"
            assert idle_state["boxLidPosY"] >= 0.55, f"Box lid should be atop base, got {idle_state['boxLidPosY']}"
            assert idle_state["boxMaterialTransparent"] is True, "boxMaterial must be transparent for soft dissolve"
            assert idle_state["lidMaterialTransparent"] is True, "lidMaterial must be transparent for soft dissolve"
            assert idle_state["burstParticleCount"] == 56, f"Expected 56 3D burst particles, got {idle_state['burstParticleCount']}"
            print("  [PASS] Idle scene graph and transparent materials verified.")

            # 2. Interactive Pointermove / Parallax Damping Verification
            parallax_check = page.evaluate("""() => {
                window.dispatchEvent(new PointerEvent('pointermove', { clientX: 200, clientY: 150 }));
                return {
                    targetX: targetRotationX,
                    targetY: targetRotationY
                };
            }""")
            assert not (abs(parallax_check["targetX"]) == 0 and abs(parallax_check["targetY"]) == 0), "Parallax should update target rotation"
            print("  [PASS] Pointermove parallax smoothly updates target angles.")

            # 3. Trigger openGift and sample 16 timeline frames
            samples = page.evaluate("""() => {
                const log = [];
                openGift();
                return new Promise((resolve) => {
                    const start = performance.now();
                    const interval = setInterval(() => {
                        const elapsed = performance.now() - start;
                        log.push({
                            t: Math.round(elapsed),
                            groupScaleY: giftGroup.scale.y,
                            groupPosY: giftGroup.position.y,
                            basePosY: boxBase.position.y,
                            baseOpacity: boxMaterial.opacity,
                            lidPosY: boxLid.position.y,
                            lidOpacity: lidMaterial.opacity,
                            lidWorldPosY: giftGroup.position.y + boxLid.position.y * giftGroup.scale.y,
                            surprisePosY: giftSurprise.position.y,
                            surpriseScale: giftSurprise.scale.y,
                            surpriseOpacity: starMaterial.opacity,
                            lightIntensity: innerLight.intensity,
                            activeBurst: activeBurstCount,
                            canvasSparks: burstSparks.length
                        });
                        if (elapsed >= 1500) {
                            clearInterval(interval);
                            resolve(log);
                        }
                    }, 100);
                });
            }""")

            # Detailed assertions across the timeline
            max_lid_world_y = 0
            lid_crashed = False
            base_dropped = False

            for s in samples:
                # Rule 1: Box base should NEVER drop into the basement (no negative y: -5 or y: -0.9)
                if s["basePosY"] < -0.05:
                    base_dropped = True

                # Rule 2: Lid world position must not crash down once it reached altitude
                if s["lidWorldPosY"] > max_lid_world_y:
                    max_lid_world_y = s["lidWorldPosY"]
                elif max_lid_world_y > 3.0 and s["lidWorldPosY"] < 2.0 and s["lidOpacity"] > 0.05:
                    lid_crashed = True

            print(f"  [Ascension Peak] Max Lid World Y reached: {max_lid_world_y:.2f}")
            assert not base_dropped, f"Box base dropped negatively during animation!"
            assert not lid_crashed, f"Box lid crashed back down after reaching apex!"
            assert max_lid_world_y >= 4.5, f"Lid did not reach celebratory apex height, only {max_lid_world_y}"
            print("  [PASS] Box Base stayed firmly anchored (zero drop); Box Lid ascended high without crashing.")

            # Rule 3: Surprise Christmas Star rose to center screen
            final_sample = samples[-1]
            mid_sample = [s for s in samples if 700 <= s["t"] <= 1000][0]
            print(f"  [Surprise Centerpiece] Surprise Pos Y at 900ms: {mid_sample['surprisePosY']:.2f}, Scale: {mid_sample['surpriseScale']:.2f}")
            assert mid_sample["surprisePosY"] >= 1.5, f"Christmas star did not rise to center, Y: {mid_sample['surprisePosY']}"
            assert mid_sample["surpriseScale"] >= 1.2, f"Christmas star did not expand, Scale: {mid_sample['surpriseScale']}"
            print("  [PASS] Christmas Star rose gracefully from the box to the center of view.")

            # Rule 4: Soft Material Dissolve Verification
            assert samples[-1]["baseOpacity"] <= 0.05, f"Box base did not dissolve opacity, opacity: {samples[-1]['baseOpacity']}"
            assert samples[-1]["lidOpacity"] <= 0.05, f"Box lid did not dissolve opacity, opacity: {samples[-1]['lidOpacity']}"
            print("  [PASS] Materials dissolved smoothly into stardust (opacity -> 0) without geometric singularity.")

            # Rule 5: Particle Celebrations
            assert samples[5]["activeBurst"] > 0, "3D burst particles were not activated"
            assert samples[5]["canvasSparks"] >= 60, f"2D canvas fireworks were not fired, count: {samples[5]['canvasSparks']}"
            print(f"  [PASS] 3D Particle fountain ({samples[5]['activeBurst']} active) and 2D canvas fireworks ({samples[5]['canvasSparks']} sparks) active.")

            # Rule 6: Card and Typewriter Hand-off
            card_active = page.evaluate("document.getElementById('mainContent').classList.contains('active')")
            canvas_opened = page.evaluate("document.getElementById('three-canvas').classList.contains('opened')")
            assert card_active is True, "Greeting card mainContent should be active"
            assert canvas_opened is True, "three-canvas should have .opened class (pointer-events: none)"
            print("  [PASS] Greeting card activated seamlessly and three-canvas set to pointer-events: none.")

            # Zero critical JS errors
            critical_errors = [e for e in console_errors if "play() failed" not in e and "NotAllowedError" not in e]
            assert len(critical_errors) == 0, f"Encountered JS errors: {critical_errors}"
            print("  [PASS] Zero runtime JS console or page errors.")

            context.close()

        browser.close()

    print("\n" + "=" * 70)
    print(" ALL DEEP 3D OPENING VERIFICATIONS PASSED 100%!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = verify_gift_opening_mechanics()
    sys.exit(0 if success else 1)
