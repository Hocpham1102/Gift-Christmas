import json
import base64
from pathlib import Path
from PIL import Image
import tempfile
from playwright.sync_api import sync_playwright

INDEX_URI = Path("index.html").resolve().as_uri()

def generate_sample_images(count=12):
    images = []
    for i in range(count):
        # Create small test base64 jpeg
        img = Image.new("RGB", (120, 120), color=((i * 45) % 255, (i * 70) % 255, (i * 95) % 255))
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            img.save(f.name, format="JPEG", quality=80)
            f.seek(0)
            b64 = base64.b64encode(f.read()).decode("utf-8")
            images.append(f"data:image/jpeg;base64,{b64}")
    return images

def test_floating_on_viewports():
    images = generate_sample_images(12)
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
            # Inject images into localStorage before load so they load automatically
            page.add_init_script(f"""
                localStorage.setItem('christmas_uploaded_images', '{json.dumps(images)}');
            """)
            page.goto(INDEX_URI)
            page.wait_for_selector("#tapHint")
            
            # Open gift
            page.click("#three-canvas")
            page.wait_for_selector(".content.active")
            
            # Fill typewriter message to test realistic fully-populated card state
            page.evaluate("""() => {
                document.getElementById('typewriter').innerHTML = message;
            }""")
            page.wait_for_timeout(2000) # wait for GSAP animation to settle
            
            card_box = page.locator("#mainContent").bounding_box()
            music_box = page.locator("#musicToggle").bounding_box()
            settings_box = page.locator("#settingsBtn").bounding_box()
            
            floating_imgs = page.locator(".floating-image").all()
            print(f"\n=== {vp['name']} with {len(floating_imgs)} Floating Images ===")
            print(f"  Controls: Music {music_box['x']:.1f},{music_box['y']:.1f} ({music_box['width']:.1f}x{music_box['height']:.1f}), Settings {settings_box['x']:.1f},{settings_box['y']:.1f} ({settings_box['width']:.1f}x{settings_box['height']:.1f})")
            print(f"  Card: [{card_box['x']:.1f}, {card_box['y']:.1f}, {card_box['width']:.1f}, {card_box['height']:.1f}]")
            
            collisions = []
            out_of_bounds = []
            boxes = []
            for idx, img_loc in enumerate(floating_imgs):
                box = img_loc.bounding_box()
                boxes.append(box)
                if not box:
                    continue
                # Check out of bounds
                if box['x'] < 0 or box['y'] < 0 or (box['x'] + box['width']) > vp['w'] or (box['y'] + box['height']) > vp['h']:
                    out_of_bounds.append((idx, box))
                
                # Check collision with music
                if not (box['x'] + box['width'] <= music_box['x'] or box['x'] >= music_box['x'] + music_box['width'] or
                        box['y'] + box['height'] <= music_box['y'] or box['y'] >= music_box['y'] + music_box['height']):
                    collisions.append((f"img_{idx}", "music", box))
                
                # Check collision with settings
                if not (box['x'] + box['width'] <= settings_box['x'] or box['x'] >= settings_box['x'] + settings_box['width'] or
                        box['y'] + box['height'] <= settings_box['y'] or box['y'] >= settings_box['y'] + settings_box['height']):
                    collisions.append((f"img_{idx}", "settings", box))
                
                # Check collision with card
                if not (box['x'] + box['width'] <= card_box['x'] or box['x'] >= card_box['x'] + card_box['width'] or
                        box['y'] + box['height'] <= card_box['y'] or box['y'] >= card_box['y'] + card_box['height']):
                    collisions.append((f"img_{idx}", "card", box))

            # Check pairwise collisions between floating images
            pairwise_collisions = []
            for i in range(len(boxes)):
                for j in range(i + 1, len(boxes)):
                    b1, b2 = boxes[i], boxes[j]
                    if not b1 or not b2:
                        continue
                    if not (b1['x'] + b1['width'] <= b2['x'] or b2['x'] + b2['width'] <= b1['x'] or
                            b1['y'] + b1['height'] <= b2['y'] or b2['y'] + b2['height'] <= b1['y']):
                        pairwise_collisions.append((f"img_{i}", f"img_{j}", b1, b2))
            
            print(f"  Card & control collisions: {len(collisions)}")
            for c in collisions:
                print(f"    Collision: {c[0]} with {c[1]}: box={c[2]}")
            print(f"  Pairwise floating image collisions: {len(pairwise_collisions)}")
            for pc in pairwise_collisions:
                print(f"    Pairwise Collision: {pc[0]} with {pc[1]}")
            print(f"  Total out-of-bounds: {len(out_of_bounds)}")
            for ob in out_of_bounds:
                print(f"    Out of bounds: img_{ob[0]}: box={ob[1]}")

            assert len(collisions) == 0, f"Collisions found on {vp['name']}: {collisions}"
            assert len(pairwise_collisions) == 0, f"Pairwise collisions found on {vp['name']}: {pairwise_collisions}"
            assert len(out_of_bounds) == 0, f"Out of bounds found on {vp['name']}: {out_of_bounds}"
            
            page.screenshot(path=f"tests/artifacts/audit_images_{vp['w']}x{vp['h']}.png")
            page.close()
        browser.close()

if __name__ == "__main__":
    test_floating_on_viewports()
