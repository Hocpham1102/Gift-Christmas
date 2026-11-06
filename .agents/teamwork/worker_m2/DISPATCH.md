# Task Assignment: Worker Milestone M2 (UI/UX Holiday Visuals, Particles & Anti-Overflow Layout)

## Objective
Implement Milestone M2: transform the visual styling and card architecture of `index.html` to an exquisite, modern holiday Christmas theme with anti-overflow card scrolling, festive particle system (removing pink hearts), warm lighting, and interactive audio toggle controls.

## Mandatory Reading
- Original Request: `e:\GitHub\Gift-Christmas\.agents\teamwork\ORIGINAL_REQUEST.md` (read verbatim)
- Project Plan: `e:\GitHub\Gift-Christmas\.agents\teamwork\PROJECT.md`
- Working Directory: `e:\GitHub\Gift-Christmas\.agents\teamwork\worker_m2\`
- Explorer 2 Report: `e:\GitHub\Gift-Christmas\.agents\teamwork\explorer_survey_2\handoff.md` (detailed CSS/HTML architecture)
- Test Suite: `e:\GitHub\Gift-Christmas\tests\verify_e2e.py` and `TEST_READY.md`

## MANDATORY INTEGRITY WARNING
> DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Scope & File Ownership
You exclusively own:
- `e:\GitHub\Gift-Christmas\index.html`
DO NOT modify test files in `tests/`.

## Concrete Implementation Requirements (Features F3, F4, F5, F6, F7)

### 1. F3: Card Architecture & Anti-Overflow Protection
- Refactor `.content` structure into:
  ```html
  <div class="content festive-card" id="mainContent">
    <div class="card-header">
      <div class="festive-badge">🎄 MÙA GIÁNG SINH & NĂM MỚI ❄️</div>
      <h1>Merry Christmas! 🎄✨🎁</h1>
    </div>
    <div class="card-body" id="cardBody">
      <div id="typewriter" class="typewriter-text"></div>
    </div>
    <div class="card-footer">
      <button class="replay-btn" id="replayBtn" title="Đọc lại lời chúc">
        <span>✨ Đọc lại lời chúc</span>
      </button>
      <div class="festive-seal">Warmest Wishes ❤️</div>
    </div>
  </div>
  ```
- CSS for `.content`:
  - `max-height: calc(88dvh - 20px);`
  - `background: rgba(15, 23, 42, 0.72);`
  - `backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);`
  - `border-radius: 24px;`
  - `border: 1px solid rgba(251, 191, 36, 0.35);`
  - `box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 40px rgba(251, 191, 36, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.15);`
- CSS for `.card-body#cardBody`:
  - `overflow-y: auto;`
  - `overscroll-behavior: contain;`
  - `max-height: 52vh;` (or similar responsive proportion)
  - `word-break: break-word;`
  - Custom thin gold scrollbar:
    - `scrollbar-width: thin; scrollbar-color: rgba(251, 191, 36, 0.5) transparent;`
    - `::-webkit-scrollbar { width: 6px; }`
    - `::-webkit-scrollbar-thumb { background: rgba(251, 191, 36, 0.4); border-radius: 10px; }`
- CSS for `.typewriter-text`:
  - `font-size: clamp(0.88rem, 1.8vw, 1.02rem);`
  - `line-height: 1.68;`
  - `white-space: pre-wrap; word-break: break-word;`

### 2. F4: Holiday Color Palette & Atmospheric Lighting
- Body background:
  - Change gradient from pastel pink (`#f093fb`) to Midnight Winter Twilight:
    `linear-gradient(135deg, #090e1a 0%, #0f1d33 40%, #162a45 75%, #102334 100%)`
- Body radial glows (`body::before`):
  - Replace magenta `rgba(255, 107, 157, 0.3)` with Warm Amber Gold `rgba(251, 191, 36, 0.18)` and Forest Evergreen `rgba(16, 185, 129, 0.15)`.
- Three.js lighting (`initThreeJS()`):
  - Change `pointLight2` color from pink `0xff6b9d` to warm holiday amber `0xffd7aa` or `0xffd700`.
- Text & Card glows:
  - Replace pink shadows (`rgba(255, 107, 157)`) with warm gold/festive glows (`rgba(251, 191, 36, 0.5)` or dark contrast drop shadows).

### 3. F5: Holiday Particle System
- Remove the entire `class HeartParticle` definition and the loop `for (let j = 0; j < 20; j++) particles.push(new HeartParticle());`.
- Implement `BokehParticle` (or `StarParticle`) rendering twinkling golden stardust particles.
- Enhance `SnowParticle` to render realistic drifting snowflakes with sine wave horizontal oscillation.

### 4. F6: Interactive Audio Controls
- Add a floating music toggle button in the HTML (e.g. top-left):
  ```html
  <button class="music-toggle-btn" id="musicToggle" aria-label="Bật/Tắt nhạc nền" title="Bật/Tắt nhạc nền">
    <span class="music-icon spin-playing" id="musicIcon">🎵</span>
    <span class="music-label" id="musicLabel">Nhạc Noel</span>
  </button>
  ```
- CSS for `.music-toggle-btn`:
  - Fixed position, glassmorphism dark-slate background, gold border, smooth hover transitions.
  - Spinning animation when playing, paused/opacity 0.5 when muted/paused.
- JavaScript logic:
  - Click event on `#musicToggle` toggles music playback / mute state:
    ```javascript
    const musicToggle = document.getElementById('musicToggle');
    if (musicToggle) {
      musicToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        if (music.paused) {
          music.play().then(() => {
            musicToggle.classList.remove('muted');
          }).catch(console.error);
        } else {
          music.pause();
          musicToggle.classList.add('muted');
        }
      });
    }
    ```
  - When `openGift()` triggers `music.play()`, also remove `.muted` class from `musicToggle`.

### 5. F7: Responsive & Polish
- Replay button event handler: clicking `#replayBtn` re-runs `typeWriter()` from character 0 so users can re-read the animation.
- Add `@media (prefers-reduced-motion: reduce)` rules for accessibility.
- Ensure typewriter `checkTag()` safe boundary: `while (i < message.length && message.charAt(i) !== ">")`.

## Verification Instructions
Execute the complete E2E test suite:
```powershell
python tests/verify_e2e.py
```
Target: **100% of the 55 tests must pass (55/55 PASSED)**.

## Output Requirements
Write your detailed report to `e:\GitHub\Gift-Christmas\.agents\teamwork\worker_m2\handoff.md`.
Maintain progress in `e:\GitHub\Gift-Christmas\.agents\teamwork\worker_m2\progress.md`.
Send a completion message back to the orchestrator.

## 2026-11-05T13:47:06Z
You are Worker M2 (UI/UX Holiday Visuals, Particles & Anti-Overflow Layout).
Your working directory is: e:\GitHub\Gift-Christmas\.agents\teamwork\worker_m2\
Please read:
1. ORIGINAL_REQUEST.md: e:\GitHub\Gift-Christmas\.agents\teamwork\ORIGINAL_REQUEST.md
2. PROJECT.md: e:\GitHub\Gift-Christmas\.agents\teamwork\PROJECT.md
3. DISPATCH.md: e:\GitHub\Gift-Christmas\.agents\teamwork\worker_m2\DISPATCH.md
4. Explorer 2 Handoff: e:\GitHub\Gift-Christmas\.agents\teamwork\explorer_survey_2\handoff.md
5. Test Suite: tests/verify_e2e.py and TEST_READY.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your scope is to implement features F3, F4, F5, F6, F7 in index.html, run python tests/verify_e2e.py to verify 55/55 tests pass, write handoff.md, and notify the orchestrator via send_message.

## 2026-11-05T13:57:34Z
**Context**: Status check on Worker Milestone M2 (UI/UX Holiday Visuals, Particles & Anti-Overflow Layout).
**Content**: 10 minutes have elapsed since dispatch.
**Action**: Please report your current progress, update progress.md with steps completed, or deliver handoff.md if ready.
