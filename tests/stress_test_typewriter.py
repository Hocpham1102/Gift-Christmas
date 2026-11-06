#!/usr/bin/env python3
"""
Adversarial Probe 2: Typewriter & checkTag() Stress Test Harness
Executes step-by-step typewriter simulation in Playwright Chromium.
"""

import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def run_typewriter_stress_test():
    index_path = Path("index.html")
    assert index_path.exists(), "index.html not found!"
    raw_content = index_path.read_text(encoding="utf-8")

    # Extract message and speed from index.html
    msg_match = re.search(r"const\s+message\s*=\s*`([^`]+)`", raw_content)
    assert msg_match, "Could not find 'const message' in index.html"
    message = msg_match.group(1)

    speed_match = re.search(r"const\s+speed\s*=\s*(\d+);", raw_content)
    assert speed_match, "Could not find 'const speed' in index.html"
    speed = int(speed_match.group(1))

    print(f"Target message length: {len(message)} chars")
    print(f"Configured speed: {speed} ms")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content('<div id="typewriter"></div>')

        # Run step-by-step instrumentation in browser
        sim_result = page.evaluate('''(args) => {
            const { message, speed } = args;
            const el = document.getElementById("typewriter");
            const steps = [];
            let i = 0;
            let stepCount = 0;

            function checkTag() {
                let tag = "";
                while (message.charAt(i) !== ">") {
                    tag += message.charAt(i);
                    i++;
                }
                tag += ">";
                i++;
                return tag;
            }

            while (i < message.length) {
                const char = message.charAt(i);
                const chunk = char === "<" ? checkTag() : char;
                el.innerHTML += chunk;
                if (char !== "<") i++;
                stepCount++;

                // Sample validation on steps
                if (stepCount % 50 === 0 || i >= message.length || chunk.startsWith("<")) {
                    steps.push({
                        step: stepCount,
                        i: i,
                        chunk: chunk,
                        hasBrokenTag: /<[^>]*$/.test(el.innerHTML),
                        innerHTMLLen: el.innerHTML.length,
                        hasNaN: isNaN(speed)
                    });
                }
            }

            return {
                totalSteps: stepCount,
                finalI: i,
                messageLen: message.length,
                finalInnerHTML: el.innerHTML,
                finalInnerText: el.innerText,
                brCount: (el.innerHTML.match(/<br>/g) || []).length,
                steps: steps
            };
        }''', {"message": message, "speed": speed})

        browser.close()

    print("\n=== TYPEWRITER STEP-BY-STEP RESULTS ===")
    print(f"Total steps executed: {sim_result['totalSteps']}")
    print(f"Final pointer index: {sim_result['finalI']} / {sim_result['messageLen']}")
    print(f"Detected <br> count in DOM: {sim_result['brCount']}")
    print(f"Estimated duration: {sim_result['totalSteps'] * speed / 1000:.2f} seconds")

    # Invariants verification
    errors = []
    if sim_result['finalI'] != sim_result['messageLen']:
        errors.append(f"Pointer mismatch: final i={sim_result['finalI']} != len={sim_result['messageLen']}")

    expected_brs = len(re.findall(r"<br>", message))
    if sim_result['brCount'] != expected_brs:
        errors.append(f"BR count mismatch: expected {expected_brs}, got {sim_result['brCount']}")

    for s in sim_result['steps']:
        if s['hasBrokenTag']:
            errors.append(f"Broken tag detected at step {s['step']}: chunk={s['chunk']}")
        if s['hasNaN']:
            errors.append(f"NaN speed detected at step {s['step']}")

    # Check ampersand in final text
    if "Merry Christmas & Happy New Year!" not in sim_result['finalInnerText']:
        errors.append(f"Ampersand text corrupted in innerText: {sim_result['finalInnerText']}")

    # Check emojis in final text
    if "🎄🎁✨" not in sim_result['finalInnerText']:
        errors.append(f"Emojis missing or corrupted in innerText: {sim_result['finalInnerText']}")

    if errors:
        print("\nERRORS DETECTED:")
        for err in errors:
            print(f" - {err}")
        return False
    else:
        print("\nALL INVARIANTS PASSED: No tag splits, zero NaN timeouts, clean DOM rendering.")
        return True

if __name__ == "__main__":
    success = run_typewriter_stress_test()
    sys.exit(0 if success else 1)
