# Task Assignment: Sub-Orchestrator Milestone M1 (Content Transformation & Text Integrity)

## Objective
Lead Milestone M1 implementation: completely transform all text content from romantic couple vows to a warm, genuine, high-spirited friendship Christmas greeting, and fix HTML syntax integrity.

## Scope (Features F1, F2, F8)
1. **F1 (Title & Microcopy)**:
   - `<title>`: Update to friendly holiday greeting (e.g. `Merry Christmas - Món Quà Giáng Sinh Ấm Áp Dành Tặng Bạn 🎄✨`). Zero romantic phrasing.
   - `#tapHint`: Update from `✨ Nhấn vào hộp quà đi em! ✨` to warm friendly prompt (e.g. `✨ Chạm vào hộp quà để mở điều bất ngờ bạn nhé! ✨`).
   - `h1`: Update from `Merry Christmas! 🎄💝` to festive icons (e.g. `Merry Christmas! 🎄✨🎁`).
   - Settings modal: Update step 3 to `Gửi link cho bạn bè và người thân`.
2. **F2 (Friendship Greeting & Typewriter)**:
   - Rewrite `const message`: Compose a natural, touching, and warm friendship Christmas letter celebrating companionship, gratitude for memories of the past year, and heartfelt wishes for peace and success in the new year.
   - Zero occurrences of forbidden romantic vocabulary (`"anh yêu"`, `"yêu em"`, `"dành cho em"`, `"đi em"`, `"người con gái"`, `"bờ vai ấm áp"`, `"trái tim và tình yêu"`, `"mãi mãi về sau"`, `"💝"`).
   - Tune typewriter speed (`30-40ms`) for smooth delivery in ~15-20 seconds.
3. **F8 (Syntax Hygiene)**:
   - Remove trailing markdown fence (````) at `index.html:1498`.

## Context & Inputs
- Original Request: `e:\GitHub\Gift-Christmas\.agents\teamwork\ORIGINAL_REQUEST.md`
- Project Plan: `e:\GitHub\Gift-Christmas\.agents\teamwork\PROJECT.md`
- Working Directory: `e:\GitHub\Gift-Christmas\.agents\teamwork\sub_orch_m1\`
- Explorer 1 Report: `e:\GitHub\Gift-Christmas\.agents\teamwork\explorer_survey_1\handoff.md`
- Explorer 3 Report: `e:\GitHub\Gift-Christmas\.agents\teamwork\explorer_survey_3\handoff.md`
- Parent ID: `a3ecd048-76ad-4b80-b218-217734502789`

## Execution Loop
- Apply Project Pattern Iteration Loop: Explorer -> Worker -> Reviewers (2) -> Challengers (2) -> Forensic Auditor -> Gate.
- Include mandatory integrity warning to Worker.
- Write your progress to `e:\GitHub\Gift-Christmas\.agents\teamwork\sub_orch_m1\progress.md`.
- Deliver `handoff.md` and report completion back to parent orchestrator when the gate passes cleanly.
