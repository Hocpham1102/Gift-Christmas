import json
from pathlib import Path
from playwright.sync_api import sync_playwright

INDEX_URI = Path("index.html").resolve().as_uri()

viewports = [
    {"name": "360x640", "w": 360, "h": 640},
    {"name": "375x667", "w": 375, "h": 667},
    {"name": "390x844", "w": 390, "h": 844},
    {"name": "412x915", "w": 412, "h": 915},
    {"name": "430x932", "w": 430, "h": 932},
    {"name": "667x375", "w": 667, "h": 375},
    {"name": "844x390", "w": 844, "h": 390},
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
        page.wait_for_timeout(1500)

        elements = page.locator(".floating-image").all()
        boxes = [el.bounding_box() for el in elements]
        pairwise_collisions = []
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                b1, b2 = boxes[i], boxes[j]
                if not b1 or not b2:
                    continue
                overlap = not (
                    b1["x"] + b1["width"] <= b2["x"] or
                    b2["x"] + b2["width"] <= b1["x"] or
                    b1["y"] + b1["height"] <= b2["y"] or
                    b2["y"] + b2["height"] <= b1["y"]
                )
                if overlap:
                    pairwise_collisions.append((i, j, b1, b2))
        print(f"=== {vp['name']} ===")
        print(f"Total pairwise floating image collisions: {len(pairwise_collisions)}")
        for c in pairwise_collisions:
            print(f"  Img {c[0]} overlaps Img {c[1]}: ({c[2]['x']:.1f}, {c[2]['y']:.1f}) size {c[2]['width']:.0f} vs ({c[3]['x']:.1f}, {c[3]['y']:.1f}) size {c[3]['width']:.0f}")
        page.close()
    browser.close()
