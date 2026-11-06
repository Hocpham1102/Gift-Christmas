import subprocess
import time
import json
import urllib.request
import asyncio
import websockets
import os
import base64

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9222
CARD_URL = "file:///E:/GitHub/Gift-Christmas/index.html"

async def test_card_e2e():
    proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={PORT}",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--mute-audio",
        "--window-size=1280,720",
        "about:blank"
    ])

    try:
        # Wait for debugging port
        ws_url = None
        for _ in range(20):
            try:
                with urllib.request.urlopen(f"http://localhost:{PORT}/json") as resp:
                    tabs = json.loads(resp.read().decode())
                    if tabs:
                        ws_url = tabs[0]["webSocketDebuggerUrl"]
                        break
            except Exception:
                await asyncio.sleep(0.5)

        if not ws_url:
            print("Failed to get WebSocket debugger URL")
            return False

        print("Connected to Chrome CDP:", ws_url)
        async with websockets.connect(ws_url) as ws:
            msg_id = 1

            async def send_cmd(method, params=None):
                nonlocal msg_id
                cid = msg_id
                msg_id += 1
                payload = {"id": cid, "method": method, "params": params or {}}
                await ws.send(json.dumps(payload))
                while True:
                    resp = await ws.recv()
                    data = json.loads(resp)
                    if data.get("id") == cid:
                        return data.get("result", {})

            # Enable domains
            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")
            await send_cmd("DOM.enable")

            # Navigate to local file
            print("Navigating to:", CARD_URL)
            await send_cmd("Page.navigate", {"url": CARD_URL})

            # Wait 2.5 seconds for page & Three.js to initialize
            await asyncio.sleep(2.5)

            # Evaluate document.title
            res = await send_cmd("Runtime.evaluate", {"expression": "document.title", "returnByValue": True})
            title = res.get("result", {}).get("value")
            print("Evaluated title:", title)

            # Check tapHint text
            res = await send_cmd("Runtime.evaluate", {
                "expression": "document.getElementById('tapHint').innerText",
                "returnByValue": True
            })
            tap_hint = res.get("result", {}).get("value")
            print("Evaluated tapHint:", tap_hint)

            # Trigger openGift()
            res = await send_cmd("Runtime.evaluate", {
                "expression": "openGift(); isOpened;",
                "returnByValue": True
            })
            print("Triggered openGift result:", res.get("result", {}).get("value"))

            # Wait 3 seconds for GSAP animation + card reveal + typewriter start
            await asyncio.sleep(3.0)

            # Check mainContent active class
            res = await send_cmd("Runtime.evaluate", {
                "expression": "document.getElementById('mainContent').classList.contains('active')",
                "returnByValue": True
            })
            is_active = res.get("result", {}).get("value")
            print("MainContent is active:", is_active)

            # Check typewriter partial text
            res = await send_cmd("Runtime.evaluate", {
                "expression": "document.getElementById('typewriter').innerHTML",
                "returnByValue": True
            })
            tw_text = res.get("result", {}).get("value") or ""
            print("Typewriter current innerHTML (first 100 chars):", tw_text[:100])

            # Take screenshot of open card
            shot = await send_cmd("Page.captureScreenshot", {"format": "png"})
            img_data = base64.b64decode(shot["data"])
            out_path = r"E:\GitHub\Gift-Christmas\.agents\teamwork\explorer_survey_3\screenshot_opened.png"
            with open(out_path, "wb") as f:
                f.write(img_data)
            print("Saved opened card screenshot to:", out_path)
            return True

    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    asyncio.run(test_card_e2e())
