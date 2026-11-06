import re
import sys

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    romantic_patterns = [
        r'\banh\s+yêu\b',
        r'\byêu\s+em\b',
        r'\bdành\s+cho\s+em\b',
        r'\bđi\s+em\b',
        r'\bngười\s+con\s+gái\b',
        r'\bbờ\s+vai\b',
        r'\btình\s+yêu\b',
        r'\bngười\s+yêu\b',
        r'\bngười\s+tình\b',
        r'\bhẹn\s+hò\b',
        r'\bhôn\s+em\b',
        r'\bôm\s+em\b',
        r'\bngười\s+thương\b',
        r'\byêu\s+dấu\b',
        r'\bmãi\s+mãi\s+về\s+sau\b',
        r'💝'
    ]

    findings = []
    lines = content.splitlines()
    for idx, line in enumerate(lines, 1):
        for pattern in romantic_patterns:
            matches = list(re.finditer(pattern, line, re.IGNORECASE))
            for m in matches:
                findings.append((idx, pattern, m.group(0), line.strip()))

    print("=== ROMANTIC PATTERN AUDIT ===")
    print(f"Total findings: {len(findings)}")
    for line_num, pat, match, line in findings:
        print(f"Line {line_num}: pattern '{pat}' matched '{match}' -> {line[:80]}")

    # Check for CSS hiding tricks
    print("\n=== CSS HIDING TRICKS AUDIT ===")
    css_hiding_patterns = [
        r'display\s*:\s*none',
        r'visibility\s*:\s*hidden',
        r'opacity\s*:\s*0',
        r'position\s*:\s*absolute;\s*left\s*:\s*-\d+px',
        r'font-size\s*:\s*0'
    ]
    for idx, line in enumerate(lines, 1):
        for pat in css_hiding_patterns:
            if re.search(pat, line, re.IGNORECASE):
                # Print context
                print(f"Line {idx}: {line.strip()[:100]}")

    # Check for comments that might contain hidden text
    print("\n=== HTML / JS COMMENT AUDIT ===")
    html_comments = re.findall(r'<!--(.*?)-->', content, re.DOTALL)
    for c in html_comments:
        c_clean = c.strip()
        for pat in romantic_patterns:
            if re.search(pat, c_clean, re.IGNORECASE):
                print(f"WARNING: Romantic keyword found in HTML comment: {c_clean[:80]}")

    js_comments = re.findall(r'//(.*)$', content, re.MULTILINE)
    for jsc in js_comments:
        for pat in romantic_patterns:
            if re.search(pat, jsc, re.IGNORECASE):
                print(f"WARNING: Romantic keyword found in JS line comment: {jsc.strip()[:80]}")

    js_block_comments = re.findall(r'/\*(.*?)\*/', content, re.DOTALL)
    for jsbc in js_block_comments:
        for pat in romantic_patterns:
            if re.search(pat, jsbc, re.IGNORECASE):
                print(f"WARNING: Romantic keyword found in JS block comment: {jsbc.strip()[:80]}")

    print("\n=== SCRIPT SYNTAX AND TAIL CHECK ===")
    print("Last 5 lines of index.html:")
    for l in lines[-5:]:
        print(f"  {repr(l)}")

    if any("```" in l for l in lines[-5:]):
        print("ERROR: Trailing markdown backticks detected!")
    else:
        print("PASS: No trailing markdown backticks.")

if __name__ == '__main__':
    main()
