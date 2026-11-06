import subprocess
import time
import json
import urllib.request
import asyncio
import websockets
import os

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9223  # use 9223 to avoid conflicts
CARD_URL = "file:///E:/GitHub/Gift-Christmas/index.html"

async def test_runtime():
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
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        ws_url = None
        for _ in range(25):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json") as resp:
                    tabs = json.loads(resp.read().decode())
                    if tabs:
                        ws_url = tabs[0]["webSocketDebuggerUrl"]
                        break
            except Exception:
                await asyncio.sleep(0.3)

        if not ws_url:
            print("ERROR: Could not get Chrome debugger WebSocket URL")
            return False

        print("Connected to Chrome:", ws_url)
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

            # Collect console messages & errors
            console_logs = []
            runtime_exceptions = []

            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")

            # Navigate to index.html
            print(f"Navigating to {CARD_URL}...")
            await send_cmd("Page.navigate", {"url": CARD_URL})
            await asyncio.sleep(2.0)

            # Evaluate initial state
            eval_res = await send_cmd("Runtime.evaluate", {
                "expression": "({ title: document.title, tapHint: document.getElementById('tapHint')?.innerText, h1: document.querySelector('h1')?.innerText, msgLen: typeof message !== 'undefined' ? message.length : -1, speed: typeof speed !== 'undefined' ? speed : -1 })",
                "returnByValue": True
            })
            val = eval_res.get("result", {}).get("value", {})
            print("Initial DOM & JS state:", val)

            # Check if typeWriter() can execute to completion
            # Speed up typewriter for test by setting speed = 1ms
            await send_cmd("Runtime.evaluate", {"expression": "speed = 1;"})
            await send_cmd("Runtime.evaluate", {"expression": "typeWriter();"})
            print("Invoked typeWriter()... waiting for typing to finish...")
            await asyncio.sleep(1.5)

            # Check rendered content in #typewriter
            tw_res = await send_cmd("Runtime.evaluate", {
                "expression": "({ twHtml: document.getElementById('typewriter')?.innerHTML, twText: document.getElementById('typewriter')?.innerText, i: i, targetLen: message.length })",
                "returnByValue": True
            })
            tw_val = tw_res.get("result", {}).get("value", {})
            print(f"Typewriter finished index i={tw_val.get('i')} / {tw_val.get('targetLen')}")
            print(f"Rendered HTML length: {len(tw_val.get('twHtml', ''))}")
            print(f"Sample rendered text: {tw_val.get('twText', '')[:120]}...")

            # Validate that innerHTML matches message exactly
            match_res = await send_cmd("Runtime.evaluate", {
                "expression": "document.getElementById('typewriter').innerHTML === message",
                "returnByValue": True
            })
            is_exact_match = match_res.get("result", {}).get("value")
            print("innerHTML === message in live Chrome:", is_exact_match)

            assert is_exact_match is True, "Live browser innerHTML does not match message variable!"
            print("CDP RUNTIME VERIFICATION SUCCESSFUL!")
            return True
    finally:
        proc.kill()
        proc.wait()

if __name__ == "__main__":
    asyncio.run(test_runtime())
