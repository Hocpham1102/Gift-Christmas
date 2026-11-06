import subprocess
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_content('<div id="test"></div>')
    
    # Test 1: innerHTML += charAt(i)
    result = page.evaluate('''() => {
        const el = document.getElementById("test");
        const msg = "🎄🎁✨";
        for (let i = 0; i < msg.length; i++) {
            el.innerHTML += msg.charAt(i);
        }
        return {
            innerHTML: el.innerHTML,
            innerText: el.innerText
        };
    }''')
    print("Result 1 (innerHTML += charAt):", repr(result))

    # Test 2: full message typewriter simulation
    full_msg_test = page.evaluate('''() => {
        const el = document.getElementById("test");
        el.innerHTML = "";
        const message = "Merry Christmas & Happy New Year! Chúc cho tình bạn của chúng ta luôn bền chặt và tràn đầy niềm vui! 🎄🎁✨";
        let i = 0;
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
            el.innerHTML += char === "<" ? checkTag() : char;
            if (char !== "<") i++;
        }
        return {
            innerHTML: el.innerHTML,
            innerText: el.innerText
        };
    }''')
    print("Result 2 (full typewriter):", repr(full_msg_test))

    browser.close()
