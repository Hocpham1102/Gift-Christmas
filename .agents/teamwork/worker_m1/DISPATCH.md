# Task Assignment: Worker Milestone M1 (Content Transformation & Text Integrity)

## Objective
Implement Milestone M1: transform all text and title from romantic couple vows to a warm, meaningful friendship Christmas greeting, and remove trailing syntax defects.

## Mandatory Reading
- Original Request: `e:\GitHub\Gift-Christmas\.agents\teamwork\ORIGINAL_REQUEST.md` (read verbatim)
- Project Master Plan: `e:\GitHub\Gift-Christmas\.agents\teamwork\PROJECT.md`
- Working Directory: `e:\GitHub\Gift-Christmas\.agents\teamwork\worker_m1\`
- Explorer 1 Report: `e:\GitHub\Gift-Christmas\.agents\teamwork\explorer_survey_1\handoff.md`

## MANDATORY INTEGRITY WARNING
> DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Scope & File Ownership
You exclusively own:
- `e:\GitHub\Gift-Christmas\index.html` (specifically text, metadata, typewriter variables, and trailing syntax cleanup).
DO NOT touch test files in `tests/`.

## Concrete Implementation Steps
1. **`<title>` (Line 7)**:
   - Replace `Món Quà Giáng Sinh Đặc Biệt Dành Cho Em ❤️` with a warm, festive friendship title, e.g.:
     `Merry Christmas - Món Quà Giáng Sinh Ấm Áp Dành Tặng Bạn 🎄✨`
2. **`.tap-hint#tapHint` (Line 746)**:
   - Replace `✨ Nhấn vào hộp quà đi em! ✨` with a friendly, welcoming prompt, e.g.:
     `✨ Chạm vào hộp quà để mở điều bất ngờ bạn nhé! ✨`
3. **`h1` Heading (Line 796)**:
   - Replace `Merry Christmas! 🎄💝` with `Merry Christmas! 🎄✨🎁` (remove romantic `💝`).
4. **Settings Modal Copy (Line 783)**:
   - Replace `3. Gửi link cho người thân yêu` with `3. Gửi link cho bạn bè và người thân`.
5. **Greeting Letter `const message` (Line 807)**:
   - Replace the romantic courtship vows with a heartfelt, genuine Vietnamese friendship letter (approx. 500-650 characters, 4-5 paragraphs separated by `<br><br>`):
   - Example structure:
     - Opening: Gửi người bạn thân mến của tôi,
     - Paragraph 1: Mùa Giáng sinh và những ngày cuối năm rộn ràng lại về mang theo những cơn gió lạnh, nhưng tôi tin rằng sự ấm áp từ những người bạn chân thành sẽ luôn sưởi ấm tâm hồn chúng ta.
     - Paragraph 2: Cảm ơn bạn vì đã luôn là một người bạn tuyệt vời trong suốt năm qua. Cảm ơn những câu chuyện sẻ chia, những nụ cười rạng rỡ và cả những khoảnh khắc chúng ta cùng nhau vượt qua áp lực bộn bề.
     - Paragraph 3: Chúc bạn và gia đình có một mùa Giáng sinh an lành, đầm ấm và ngập tràn niềm vui. Mong rằng mọi ước mơ, dự định trong năm mới của bạn đều thành công rực rỡ và thuận buồm xuôi gió.
     - Closing: Merry Christmas & Happy New Year! Chúc cho tình bạn của chúng ta luôn bền chặt và tràn đầy niềm vui! 🎄🎁✨
   - Ensure ZERO romantic words (`anh yêu`, `yêu em`, `dành cho em`, `đi em`, `người con gái`, `bờ vai ấm áp`, `trái tim và tình yêu`, `tình yêu trọn vẹn`, `mãi mãi về sau`).
6. **Typewriter Speed**:
   - Tune speed variable from `50` to `35` ms per character for smoother, more engaging reading (~18-20 seconds total).
7. **Syntax Cleanliness (Line 1498)**:
   - Remove trailing markdown fence (````) after `</html>`.

## Verification Commands
Run verification to ensure changes are clean and complete:
```powershell
# 1. Regex check for zero romantic terms
$forbidden = @("anh yêu", "yêu em", "dành cho em", "đi em", "người con gái", "bờ vai ấm áp", "trái tim và tình yêu", "💝")
foreach ($w in $forbidden) { if (Select-String -Path "index.html" -Pattern $w) { Write-Error "Found $w" } }

# 2. Syntax check
Get-Content index.html -Tail 5
```

## Output Requirements
Write your detailed report to `e:\GitHub\Gift-Christmas\.agents\teamwork\worker_m1\handoff.md`.
Maintain progress in `e:\GitHub\Gift-Christmas\.agents\teamwork\worker_m1\progress.md`.
Send a completion message back to the orchestrator.


## 2026-11-05T13:33:59Z
[Message] timestamp=2026-11-05T13:33:59Z sender=a3ecd048-76ad-4b80-b218-217734502789 priority=MESSAGE_PRIORITY_HIGH content=You are Worker M1 (Content Transformation & Text Integrity).
Your working directory is: e:\GitHub\Gift-Christmas\.agents\teamwork\worker_m1\
Please read:
1. ORIGINAL_REQUEST.md: e:\GitHub\Gift-Christmas\.agents\teamwork\ORIGINAL_REQUEST.md
2. PROJECT.md: e:\GitHub\Gift-Christmas\.agents\teamwork\PROJECT.md
3. DISPATCH.md: e:\GitHub\Gift-Christmas\.agents\teamwork\worker_m1\DISPATCH.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your scope is to update index.html with the warm friendship Christmas greetings, update title, tap hint, heading, settings copy, tune typewriter speed, remove trailing markdown backticks, run verification commands, write handoff.md, and notify the orchestrator via send_message.
