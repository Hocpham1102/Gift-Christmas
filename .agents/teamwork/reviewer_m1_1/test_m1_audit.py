import re
import subprocess

def run_checks():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Check title
    assert '<title>Merry Christmas - Món Quà Giáng Sinh Ấm Áp Dành Tặng Bạn 🎄✨</title>' in content, "Title check failed"
    print("[PASS] Title is correctly set to warm friendship greeting")

    # 2. Check tap hint
    assert '<div class="tap-hint" id="tapHint">✨ Chạm vào hộp quà để mở điều bất ngờ bạn nhé! ✨</div>' in content, "Tap hint check failed"
    print("[PASS] Tap hint is correctly set with friendship tone")

    # 3. Check h1 heading
    assert '<h1>Merry Christmas! 🎄✨🎁</h1>' in content, "h1 check failed"
    print("[PASS] h1 contains holiday emoji and no romantic heart")

    # 4. Check settings modal microcopy
    assert '3. Gửi link cho bạn bè và người thân<br>' in content, "Modal microcopy check failed"
    print("[PASS] Modal step 3 updated to friends and family")

    # 5. Check const message
    expected_msg_start = "const message = `Gửi người bạn thân mến của tôi,"
    assert expected_msg_start in content, "const message start check failed"
    assert "Chúc cho tình bạn của chúng ta luôn bền chặt và tràn đầy niềm vui! 🎄🎁✨`;" in content, "const message end check failed"
    print("[PASS] const message contains full genuine friendship message")

    # 6. Check speed
    assert 'const speed = 35;' in content, "speed check failed"
    print("[PASS] Typewriter speed set to 35ms")

    # 7. Check absence of trailing backticks
    tail_lines = content.strip().splitlines()[-5:]
    for line in tail_lines:
        assert '```' not in line, f"Found markdown fence in tail: {line}"
    assert content.strip().endswith('</html>'), "File does not end cleanly with </html>"
    print("[PASS] File syntax is clean, no trailing markdown fence")

    # 8. Check forbidden romantic words/hearts
    forbidden_terms = [
        r'\banh\s+yêu\b', r'\byêu\s+em\b', r'\bem\s+yêu\b', r'\bngười\s+yêu\b',
        r'\btình\s+yêu\b', r'\bngười\s+con\s+gái\b', r'\bbờ\s+vai\b', r'\btựa\s+vào\b',
        r'\btrái\s+tim\b', r'\bdành\s+cho\s+em\b', r'\bđi\s+em\b', r'\bnha\s+em\b',
        r'\bnhé\s+em\b', r'\bmãi\s+mãi\s+về\s+sau\b', r'\btrọn\s+đời\b', r'\bsuốt\s+kiếp\b',
        r'\bcrush\b', r'\bhẹn\s+hò\b'
    ]
    for term in forbidden_terms:
        matches = re.findall(term, content, re.IGNORECASE)
        assert len(matches) == 0, f"Found forbidden term '{term}': {matches}"
    print("[PASS] Zero forbidden romantic words found")

    romantic_hearts = ['❤️', '💝', '💖', '💗', '💘', '💓', '💕', '💞', '💌', '💟', '❣️']
    for h in romantic_hearts:
        assert h not in content, f"Found romantic heart emoji: {h}"
    print("[PASS] Zero romantic heart emojis found")

    # 9. Verify with Headless Chrome DOM dump
    chrome_cmd = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        '--headless',
        '--dump-dom',
        r'file:///e:/GitHub/Gift-Christmas/index.html'
    ]
    res = subprocess.run(chrome_cmd, capture_output=True, text=True, encoding='utf-8')
    assert res.returncode == 0, f"Chrome failed: {res.stderr}"
    dom = res.stdout

    assert '<title>Merry Christmas - Món Quà Giáng Sinh Ấm Áp Dành Tặng Bạn 🎄✨</title>' in dom
    assert '✨ Chạm vào hộp quà để mở điều bất ngờ bạn nhé! ✨' in dom
    assert '<h1>Merry Christmas! 🎄✨🎁</h1>' in dom
    assert '3. Gửi link cho bạn bè và người thân' in dom
    assert '```' not in dom, "Triple backticks found in DOM!"
    print("[PASS] Headless Chrome DOM rendering verified successfully")

    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_checks()
