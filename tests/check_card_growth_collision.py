import json
from pathlib import Path
from playwright.sync_api import sync_playwright

INDEX_URI = Path("index.html").resolve().as_uri()

viewports = [
    {"name": "360x640 (Android small)", "w": 360, "h": 640},
    {"name": "375x667 (iPhone SE)", "w": 375, "h": 667},
    {"name": "390x844 (iPhone 12/13/14)", "w": 390, "h": 844},
    {"name": "412x915 (Pixel 7/Galaxy)", "w": 412, "h": 915},
    {"name": "430x932 (iPhone Pro Max)", "w": 430, "h": 932},
    {"name": "667x375 (Landscape)", "w": 667, "h": 375},
    {"name": "844x390 (Landscape Wide)", "w": 844, "h": 390},
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    for vp in viewports:
        page = browser.new_page(viewport={"width": vp["w"], "height": vp["h"]})
        imgs = [f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'><rect fill='red' width='100' height='100'/></svg>" for _ in range(12)]
        page.add_init_script(f"localStorage.setItem('christmas_uploaded_images', JSON.stringify({json.dumps(imgs)}));")
        page.goto(INDEX_URI)
        page.click("#three-canvas")
        page.wait_for_selector(".content.active")
        # Wait for full text or set full text
        page.evaluate("() => { document.getElementById('typewriter').innerHTML = message; }")
        page.wait_for_timeout(1500)

        card_box = page.locator("#mainContent").bounding_box()
        music_box = page.locator("#musicToggle").bounding_box()
        settings_box = page.locator("#settingsBtn").bounding_box()
        floating_imgs = page.locator(".floating-image").all()
        
        card_collisions = []
        control_collisions = []
        for idx, img_loc in enumerate(floating_imgs):
            box = img_loc.bounding_box()
            if not box: continue
            
            # Card overlap
            overlap_card = not (
                box['x'] + box['width'] <= card_box['x'] or
                card_box['x'] + card_box['width'] <= box['x'] or
                box['y'] + box['height'] <= card_box['y'] or
                card_box['y'] + card_box['height'] <= box['y']
            )
            if overlap_card:
                card_collisions.append((idx, box))
                
            # Control overlap
            for ctrl_name, ctrl_box in [("music", music_box), ("settings", settings_box)]:
                overlap_ctrl = not (
                    box['x'] + box['width'] <= ctrl_box['x'] or
                    ctrl_box['x'] + ctrl_box['width'] <= box['x'] or
                    box['y'] + box['height'] <= ctrl_box['y'] or
                    ctrl_box['y'] + ctrl_box['height'] <= box['y']
                )
                if overlap_ctrl:
                    control_collisions.append((idx, ctrl_name, box))

        print(f"\n=== {vp['name']} with FULL typewriter message ===")
        print(f"  Card bounds: top={card_box['y']:.1f}, bottom={card_box['y']+card_box['height']:.1f}, height={card_box['height']:.1f}")
        print(f"  Card collisions: {len(card_collisions)}")
        for idx, b in card_collisions:
            print(f"    Img {idx}: y={b['y']:.1f}..{b['y']+b['height']:.1f} vs card={card_box['y']:.1f}..{card_box['y']+card_box['height']:.1f}")
        print(f"  Control collisions: {len(control_collisions)}")
        for idx, name, b in control_collisions:
            print(f"    Img {idx} collides with {name}!")

        page.close()
    browser.close()
