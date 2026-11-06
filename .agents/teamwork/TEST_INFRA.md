# E2E Test Infrastructure & Verification Harness

## Overview
The Gift-Christmas verification harness (`tests/verify_e2e.py`) is an opaque-box, multi-tier automated test suite engineered to validate both functional integrity, visual aesthetics, responsive typography, and cross-feature interactions for the Christmas friendship card web application (`index.html`).

## Test Architecture (4 Tiers / 55 Test Cases)

### Tier 1: Feature Coverage (42 Tests across F1–F8)
- **F1: Title & Microcopy Friendship Transformation (6 tests)**:
  - `T1.F1.01`: Zero forbidden romantic vocabulary in `<title>` (`anh yêu em`, `yêu em`, `dành cho em`, `người yêu`, `❤️`, `💖`, `💝`).
  - `T1.F1.02`: Christmas and friendship/warmth keywords present in `<title>`.
  - `T1.F1.03`: `#tapHint` free of romantic couple pronouns (`đi em`, `anh yêu`, `em yêu`).
  - `T1.F1.04`: `#tapHint` presents a warm, friendly call-to-action invitation.
  - `T1.F1.05`: `<h1>` festive heading contains zero romantic emojis and retains holiday spirit.
  - `T1.F1.06`: Settings modal sharing microcopy addresses friends and family, not romantic partners.

- **F2: Friendship Greeting Letter & Typewriter Tuning (6 tests)**:
  - `T1.F2.01`: Greeting message variable (`message`) exists in JavaScript.
  - `T1.F2.02`: Greeting letter contains 0 forbidden romance phrases.
  - `T1.F2.03`: Greeting letter contains >= 3 authentic friendship/gratitude themes (`bạn`, `tình bạn`, `cảm ơn`, `đồng hành`, `tri kỷ`, `ấm áp`, `an lành`).
  - `T1.F2.04`: Letter length is balanced between 450 and 750 characters to prevent overflow.
  - `T1.F2.05`: Typewriter speed interval is configured between 15ms and 100ms.
  - `T1.F2.06`: Typewriter handles HTML `<br>` tags without rendering broken tag syntax.

- **F3: Card Architecture & Anti-Overflow Protection (5 tests)**:
  - `T1.F3.01`: Card container (`.content`) allows inner scrolling without rigid clipping.
  - `T1.F3.02`: Card scroll container explicitly defines `overflow-y: auto` or `scroll`.
  - `T1.F3.03`: Card body specifies `overscroll-behavior: contain` to prevent mobile scroll chaining.
  - `T1.F3.04`: Custom festive scrollbar styles (`::-webkit-scrollbar` or `scrollbar-width: thin`).
  - `T1.F3.05`: Card DOM splits into structured header, scrollable body, and footer.

- **F4: Holiday Palette & Atmospheric Lighting (5 tests)**:
  - `T1.F4.01`: Body background uses dark holiday winter twilight gradient, eliminating candy pink (`#f093fb`).
  - `T1.F4.02`: Ambient radial glows transition from hot pink to warm amber gold / pine accents.
  - `T1.F4.03`: Three.js PointLight illumination uses warm amber / holiday tones, eliminating pink (`0xff6b9d`).
  - `T1.F4.04`: Card box-shadow and glow accents do not use romantic pink (`rgba(255, 107, 157)`).
  - `T1.F4.05`: Card `<h1>` heading gradient uses festive holiday gold / winter palette instead of candy pink.

- **F5: Holiday Particle System (5 tests)**:
  - `T1.F5.01`: `HeartParticle` class definition is completely removed.
  - `T1.F5.02`: Zero `HeartParticle` instantiations in particle loops.
  - `T1.F5.03`: `SnowParticle` system is defined and instantiated with falling physics.
  - `T1.F5.04`: Sparkling bokeh / stardust particle system is active and twinkling.
  - `T1.F5.05`: Particle canvas dynamically synchronizes dimensions on window resize.

- **F6: Interactive Audio Controls (5 tests)**:
  - `T1.F6.01`: Music toggle control (`#musicToggle`) present in DOM.
  - `T1.F6.02`: Music toggle control includes accessible `aria-label` or `title`.
  - `T1.F6.03`: Background audio element (`<audio id="bgMusic">`) has loop attribute and valid audio source.
  - `T1.F6.04`: JavaScript binds click event handler to toggle music playback / mute state.
  - `T1.F6.05`: CSS defines visual active/muted styling states for music toggle.

- **F7: Multi-Device Responsiveness (5 tests)**:
  - `T1.F7.01`: Viewport meta tag configured with `width=device-width` and `initial-scale=1.0`.
  - `T1.F7.02`: CSS uses responsive viewport height units (`dvh` or `vh`).
  - `T1.F7.03`: CSS applies fluid typography using `clamp(...)`.
  - `T1.F7.04`: CSS contains responsive media queries covering mobile breakpoints (375px–768px).
  - `T1.F7.05`: Interactive controls meet minimum accessible touch target sizes (>= 36px).

- **F8: Syntax & Code Hygiene (5 tests)**:
  - `T1.F8.01`: Zero trailing markdown code fences (````) at end of file.
  - `T1.F8.02`: Valid `<!DOCTYPE html>` preamble and `lang="vi"` attribute.
  - `T1.F8.03`: Critical DOM tags paired and cleanly closed (balanced `<div>` count).
  - `T1.F8.04`: JavaScript tags contain clean code with no stray markdown syntax.
  - `T1.F8.05`: CSS `<style>` blocks have perfectly balanced curly braces.

---

### Tier 2: Boundary & Corner Cases (5 Tests)
- `T2.B01`: Card text enforces `word-break: break-word` or `overflow-wrap` boundary protection against blowout.
- `T2.B02`: Card width is responsive (`width: 90%-95%`) preventing overflow on narrow 320px–375px screens.
- `T2.B03`: Card height is constrained (`max-height: 85vh-90vh/dvh`) preventing vertical blowout in landscape orientation.
- `T2.B04`: Audio `play()` is safely guarded with `.catch()` to prevent unhandled promise rejections on strict browsers.
- `T2.B05`: Gift box click interaction implements a state guard (`isOpen`) preventing race conditions and rapid double clicks.

---

### Tier 3: Cross-Feature Combinations & Harmony (3 Tests)
- `T3.C01`: Box opening harmoniously triggers both audio playback and typewriter text delivery.
- `T3.C02`: Typewriter operates smoothly inside the scrollable card container hierarchy.
- `T3.C03`: Settings modal z-index (`z-index: 100`) strictly exceeds card and canvas z-indices.

---

### Tier 4: Real-World Scenarios (Chrome Headless Snapshots, 5 Tests)
- `T4.R01`: Desktop 1080p (`1920x1080`) headless Chrome snapshot capture.
- `T4.R02`: Tablet Portrait (`768x1024`) headless Chrome snapshot capture.
- `T4.R03`: Mobile Portrait (`375x667`) headless Chrome snapshot capture.
- `T4.R04`: Mobile Landscape (`667x375`) headless Chrome snapshot capture.
- `T4.R05`: Visual screenshot file validation: All 4 screenshots are verified valid PNGs with payload > 5,000 bytes.

---

## Execution Guide

### Standard Full Suite Execution
```bash
python tests/verify_e2e.py
```

### Selective Execution by Tier or Feature
```bash
# Run Tier 1 only (Feature Coverage)
python tests/verify_e2e.py --tier 1

# Run Tier 2 only (Boundary & Corner Cases)
python tests/verify_e2e.py --tier 2

# Run specific feature tests only (e.g. F1, F2, F3...)
python tests/verify_e2e.py --feature F1

# Run without launching Chrome (static checks only)
python tests/verify_e2e.py --skip-chrome

# Output strictly JSON to stdout
python tests/verify_e2e.py --json

# Run in diagnostic mode (returns exit code 0 even if defects exist)
python tests/verify_e2e.py --allow-fail
```

---

## Generated Artifacts
- **Test Summary & Defect Log**: `tests/artifacts/test_results.json`
- **Visual Screenshots**:
  - `tests/artifacts/screenshots/screenshot_desktop_1080p.png`
  - `tests/artifacts/screenshots/screenshot_tablet_portrait.png`
  - `tests/artifacts/screenshots/screenshot_mobile_portrait.png`
  - `tests/artifacts/screenshots/screenshot_mobile_landscape.png`

---

## Quality Gate Milestones
- **M1 Quality Gate**: Requires 100% pass on F1 (Title & Microcopy), F2 (Friendship Letter), and F8 (Syntax Hygiene).
- **M2 Quality Gate**: Requires 100% pass on F3 (Card Architecture), F4 (Holiday Palette), F5 (Holiday Particles), F6 (Audio Controls), and F7 (Responsive Polish).
- **Final M3 Gate**: Requires 100% pass across all 55 test cases (Tiers 1–4).
