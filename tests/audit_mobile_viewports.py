import tempfile
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

INDEX_URI = Path("index.html").resolve().as_uri()

def test_viewports():
    viewports = [
        {"name": "360x640 (Android small)", "w": 360, "h": 640},
        {"name": "375x667 (iPhone SE)", "w": 375, "h": 667},
        {"name": "390x844 (iPhone 12/13/14)", "w": 390, "h": 844},
        {"name": "412x915 (Pixel 7/Galaxy)", "w": 412, "h": 915},
        {"name": "430x932 (iPhone 14/15/16 Pro Max)", "w": 430, "h": 932},
        {"name": "667x375 (Mobile Landscape)", "w": 667, "h": 375},
        {"name": "844x390 (Mobile Landscape wide)", "w": 844, "h": 390},
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for vp in viewports:
            page = browser.new_page(viewport={"width": vp["w"], "height": vp["h"]})
            page.goto(INDEX_URI)
            
            # Initial state
            hint_box = page.locator("#tapHint").bounding_box()
            music_box = page.locator("#musicToggle").bounding_box()
            settings_box = page.locator("#settingsBtn").bounding_box()
            
            # Open gift
            page.click("#three-canvas")
            page.wait_for_selector(".content.active")
            
            # Full text
            page.evaluate("""() => {
                document.getElementById('typewriter').innerHTML = message;
            }""")
            page.wait_for_timeout(400)
            
            card_box = page.locator("#mainContent").bounding_box()
            body_box = page.locator("#cardBody").bounding_box()
            header_box = page.locator(".card-header").bounding_box()
            footer_box = page.locator(".card-footer").bounding_box()
            
            scroll_h = page.evaluate("() => document.getElementById('cardBody').scrollHeight")
            client_h = page.evaluate("() => document.getElementById('cardBody').clientHeight")
            
            print(f"=== {vp['name']} ===")
            print(f"  Controls: Music {music_box}, Settings {settings_box}")
            print(f"  TapHint: {hint_box}")
            print(f"  Card: top={card_box['y']:.1f}, bottom={card_box['y']+card_box['height']:.1f}, w={card_box['width']:.1f}, h={card_box['height']:.1f}")
            print(f"  Body: clientH={client_h}, scrollH={scroll_h}")
            
            # Check overlap between Controls and Card
            card_top = card_box["y"]
            music_bottom = music_box["y"] + music_box["height"]
            settings_bottom = settings_box["y"] + settings_box["height"]
            
            overlap_music = card_top < music_bottom and card_box["x"] < (music_box["x"] + music_box["width"])
            overlap_settings = card_top < settings_bottom and (card_box["x"] + card_box["width"]) > settings_box["x"]
            print(f"  Card overlaps music: {overlap_music}, overlaps settings: {overlap_settings}")
            
            Path("tests/artifacts").mkdir(parents=True, exist_ok=True)
            page.screenshot(path=f"tests/artifacts/audit_noimg_{vp['w']}x{vp['h']}.png")
            
            page.close()
        browser.close()

if __name__ == "__main__":
    test_viewports()
