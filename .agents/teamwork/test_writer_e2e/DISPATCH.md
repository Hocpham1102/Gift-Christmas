# Task Assignment: E2E Test Writer

## Objective
Design and implement the complete, opaque-box, 4-tier E2E test suite for Gift-Christmas according to user requirements and `PROJECT.md`.

## Mandatory Reading
- Original Request: `e:\GitHub\Gift-Christmas\.agents\teamwork\ORIGINAL_REQUEST.md` (read verbatim)
- Project Plan: `e:\GitHub\Gift-Christmas\.agents\teamwork\PROJECT.md`
- Working Directory: `e:\GitHub\Gift-Christmas\.agents\teamwork\test_writer_e2e\`
- Explorer 3 Prototype: `e:\GitHub\Gift-Christmas\.agents\teamwork\explorer_survey_3\verify_suite.py`

## Scope & File Ownership
You exclusively own:
- `e:\GitHub\Gift-Christmas\tests\verify_e2e.py` (and any helper test scripts in `tests/`)
- `e:\GitHub\Gift-Christmas\.agents\teamwork\TEST_INFRA.md`
- `e:\GitHub\Gift-Christmas\.agents\teamwork\TEST_READY.md`
You MUST NOT edit `index.html` or implementation source code files.

## Test Suite Architecture & 4-Tier Requirements
Implement `tests/verify_e2e.py` using Python 3.12 (executable via `python tests/verify_e2e.py`):
1. **Tier 1 - Feature Coverage (>=5 test cases per feature for F1-F8)**:
   - F1 (Title & Microcopy): Verify title has no forbidden words, title has Christmas/friendship keywords, tapHint has no couple pronouns, tapHint is friendly, h1 has no romantic emojis, settings modal has friendly sharing text.
   - F2 (Friendship Letter & Typewriter): Verify greeting message variable exists, message contains gratitude/friendship keywords, message has zero forbidden romance words, length is balanced (450-700 chars), typewriter timing/speed is reasonable.
   - F3 (Card Architecture & Anti-Overflow): Verify card container has no overflow clipping, card body specifies `overflow-y: auto`, card body has `overscroll-behavior: contain`, card body has custom scrollbar styling, card splits into header/body/footer.
   - F4 (Holiday Palette & Lighting): Verify body background uses dark holiday twilight gradient, ambient radial glows use gold/pine, PointLight in Three.js is warm/amber/holiday (not pink #ff6b9d), text shadow is gold/neutral.
   - F5 (Holiday Particle System): Verify `HeartParticle` is completely removed, verify falling snow particles exist, verify sparkling bokeh/star particles exist.
   - F6 (Interactive Audio Controls): Verify `#musicToggle` element exists, verify it has accessible labels/title, verify click event toggles mute/pause, verify visual playing/muted styling exists.
   - F7 (Multi-Device Responsiveness): Verify viewport meta tag exists, verify dvh/responsive units, verify font clamp for readability, verify zero horizontal overflow on 375px, 768px, 1920px.
   - F8 (Syntax & Code Hygiene): Verify no trailing markdown fence (```) at end of file, verify valid HTML tags closure.
2. **Tier 2 - Boundary & Corner Cases (>=5 test cases)**:
   - Extreme long text wrapping without overflow.
   - Viewport boundary test (narrow mobile 320px/375px, landscape mobile 667x375, 4K 3840x2160).
   - Audio autoplay fallback and pause/resume safety.
   - Rapid double click on gift box (ensure no multiple animation instances).
3. **Tier 3 - Cross-Feature Combinations (Pairwise Interaction)**:
   - Card opening + audio start + music toggle interaction.
   - Typewriter animation running during window resize or scroll.
   - Modal settings open/close interaction while card is open.
4. **Tier 4 - Real-World Application Scenarios (Headless Chrome Multi-Viewport Snapshots)**:
   - Execute Chrome Headless (`C:\Program Files\Google\Chrome\Application\chrome.exe --headless=new --window-size=... --screenshot=...`) across Desktop (1920x1080), Tablet (768x1024), Mobile Portrait (375x667), and Mobile Landscape (667x375).
   - Verify screenshot capture succeeded and files exist.

## Output Requirements
1. Create `e:\GitHub\Gift-Christmas\.agents\teamwork\TEST_INFRA.md` following the template in Project Pattern.
2. Implement and run `python tests/verify_e2e.py` to establish the baseline score.
3. Publish `e:\GitHub\Gift-Christmas\.agents\teamwork\TEST_READY.md`.
4. Write your handoff report to `e:\GitHub\Gift-Christmas\.agents\teamwork\test_writer_e2e\handoff.md` and send a message back.


## 2026-11-05T13:33:59Z
You are the E2E Test Writer.
Your working directory is: e:\GitHub\Gift-Christmas\.agents\teamwork\test_writer_e2e\
Please read:
1. ORIGINAL_REQUEST.md: e:\GitHub\Gift-Christmas\.agents\teamwork\ORIGINAL_REQUEST.md
2. PROJECT.md: e:\GitHub\Gift-Christmas\.agents\teamwork\PROJECT.md
3. DISPATCH.md: e:\GitHub\Gift-Christmas\.agents\teamwork\test_writer_e2e\DISPATCH.md

Your scope is to design and implement the 4-tier E2E test suite in tests/verify_e2e.py, write TEST_INFRA.md, run the test suite, publish TEST_READY.md, write handoff.md, and notify the orchestrator via send_message.
