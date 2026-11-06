# Project: Gift-Christmas Friendship & Holiday Upgrade

## Architecture
- Single-page application (`index.html`) with embedded styles, 3D WebGL scene (Three.js r128), and 2D canvas particle system.
- 3D WebGL Scene: Renders animated gift box, ribbons, and lighting.
- 2D Canvas Particle System (`#canvas-bg`): Renders holiday winter atmosphere (drifting snow, gold stardust bokeh).
- Interactive Festive Greeting Card: Unfolds upon gift box click, displays typewriter animation, and supports audio playback.
- Test Architecture: Automated multi-tier verification harness (`tests/verify_e2e.py`) combining static DOM/regex audits and headless Chrome multi-viewport visual rendering.

## Code Layout
- `index.html`: Core web application containing HTML DOM, CSS styling, and JavaScript logic. Owned sequentially by Implementation Track Workers.
- `music/`: Audio assets. Read-only.
- `images/`: Image assets. Read-only.
- `tests/`: Automated test suite and test artifacts. Owned by E2E Testing Track.
- `.agents/teamwork/`: Coordination metadata, plans, progress, handoffs, and audits.

## Feature Inventory
| # | Feature | Description | Milestone | Source | Status |
|---|---------|-------------|-----------|--------|--------|
| F1 | Title & Microcopy Friendship Update | Update `<title>`, `#tapHint`, `h1`, and settings modal copy to warm friendship greetings with no romantic phrases. | M1 | survey (Explorers 1, 2, 3) | DONE |
| F2 | Friendship Greeting Letter & Typewriter Tuning | Write warm, genuine friendship letter (4-5 paragraphs, 500-650 chars) and tune typewriter timing for smooth delivery. | M1 | survey (Explorers 1, 2, 3) | DONE |
| F3 | Card Architecture & Anti-Overflow Protection | Refactor card into header, scrollable body (`overflow-y: auto`, thin gold scrollbar, `overscroll-behavior: contain`), and footer. | M2 | survey (Explorers 2, 3) | DONE |
| F4 | Holiday Color Palette & Atmospheric Lighting | Transition pastel pinks to Midnight Winter Twilight (`#090e1a`–`#162a45`), warm amber gold glows, pine green accents, and holiday Three.js lighting. | M2 | survey (Explorers 1, 2, 3) | DONE |
| F5 | Holiday Particle System | Remove `HeartParticle` (pink hearts); implement multi-layer drifting snowflakes with sine sway and golden stardust bokeh. | M2 | survey (Explorers 1, 2, 3) | DONE |
| F6 | Interactive Audio Controls | Add floating glassmorphism music toggle button (mute/unmute, play/pause state indicator). | M2 | survey (Explorers 2, 3) | DONE |
| F7 | Multi-Device Responsive Design & Mobile Polish | Optimize card dimensions, font clamp (`0.88rem`–`1.02rem`), viewport `dvh` units, and touch interactions on 375px–1920px screens. | M2 | survey (Explorers 2, 3) | DONE |
| F8 | Syntax & Code Hygiene | Remove trailing markdown fence (````) at `index.html:1498` and ensure valid HTML structure. | M1 | survey (Explorers 1, 2, 3) | DONE |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Content Transformation & Text Integrity | F1, F2, F8 (Friendship text, title, hint, typewriter, syntax cleanup) | none | DONE |
| M2 | UI/UX Holiday Visuals, Particles & Anti-Overflow Layout | F3, F4, F5, F6, F7 (Card layout, color system, bokeh/snow particles, audio toggle, responsive) | M1 | DONE |
| M3 | Final Milestone: E2E Test Suite Pass & Adversarial Hardening | Pass 100% E2E test suite (Tiers 1-4) and Adversarial Coverage Hardening (Tier 5) | M2, E2E Test Suite | DONE |
| E2E | E2E Testing Track | Independent opaque-box test suite covering Tiers 1-4 across all features F1-F8 | none (parallel) | DONE (TEST_READY published) |

## Interface Contracts
### E2E Test Suite ↔ index.html
- Entry point: `index.html` served via `http://localhost:<port>` or `file://`.
- Title element: `<title>` must not match romantic regex and must contain Christmas/Friendship phrasing. (VERIFIED)
- Tap hint element: `#tapHint` must be present and contain friendly text. (VERIFIED)
- Card container: `.content` and `#cardBody` must not clip text; `#cardBody` must have `overflow-y: auto`. (VERIFIED)
- Typewriter container: `#typewriter` must receive full friendship greeting text upon opening. (VERIFIED)
- Music toggle: `#musicToggle` button must be present in DOM and toggle audio mute state. (VERIFIED)
- Particles: `#canvas-bg` must not instantiate `HeartParticle`. (VERIFIED)

### M1 ↔ M2
- M1 completed text strings, title, typewriter text variable, and removed trailing fence. (VERIFIED)
- M2 wrapped the friendship text into the new `.card-header`, `.card-body`, `.card-footer` layout, upgraded styles, particles, audio toggle, and lighting. (VERIFIED)
