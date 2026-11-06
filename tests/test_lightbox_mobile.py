import json
from pathlib import Path
from playwright.sync_api import sync_playwright

INDEX_URI = Path("index.html").resolve().as_uri()

def test_lightbox():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for vp in [{"w": 360, "h": 640}, {"w": 375, "h": 667}, {"w": 667, "h": 375}]:
            page = browser.new_page(viewport={"width": vp["w"], "height": vp["h"]})
            imgs = [f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><rect fill='gold' width='200' height='200'/></svg>"]
            page.add_init_script(f"localStorage.setItem('christmas_uploaded_images', JSON.stringify({json.dumps(imgs)}));")
            page.goto(INDEX_URI)
            
            # Open gift
            page.click("#three-canvas")
            page.wait_for_selector(".content.active")
            page.wait_for_selector(".floating-image")
            page.wait_for_timeout(1000)
            
            # Click floating image to open lightbox (force=True because GSAP continuous drift is active)
            page.locator(".floating-image").click(force=True)
            page.wait_for_selector("#photoLightbox.active")
            page.wait_for_timeout(400) # wait for lightboxZoom (300ms) to settle at scale(1)
            
            lightbox_box = page.locator(".lightbox-box").bounding_box()
            close_btn = page.locator("#closeLightbox").bounding_box()
            bottom_close_btn = page.locator("#bottomCloseLightbox").bounding_box()
            img_box = page.locator("#lightboxImg").bounding_box()
            
            print(f"\n=== Lightbox on {vp['w']}x{vp['h']} ===")
            print(f"  Box: {lightbox_box}")
            print(f"  Top Close Btn: {close_btn}")
            print(f"  Bottom Close Btn: {bottom_close_btn}")
            print(f"  Img: {img_box}")
            
            assert close_btn['width'] >= 44 and close_btn['height'] >= 44, "Top close button < 44px"
            assert bottom_close_btn['width'] >= 44 and bottom_close_btn['height'] >= 44, "Bottom close button too small (< 44px)"
            
            # Check bottom close button click
            page.locator("#bottomCloseLightbox").click()
            page.wait_for_timeout(300)
            is_active = page.evaluate("() => document.getElementById('photoLightbox').classList.contains('active')")
            assert not is_active, "Lightbox did not close on bottom button click"
            print("  [PASS] Closed via bottom close button")
            
            # Reopen and click image to close
            page.locator(".floating-image").click(force=True)
            page.wait_for_selector("#photoLightbox.active")
            page.locator("#lightboxImg").click()
            page.wait_for_timeout(300)
            is_active = page.evaluate("() => document.getElementById('photoLightbox').classList.contains('active')")
            assert not is_active, "Lightbox did not close on image click"
            print("  [PASS] Closed via image click")
            
            # Reopen and press Escape
            page.locator(".floating-image").click(force=True)
            page.wait_for_selector("#photoLightbox.active")
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
            is_active = page.evaluate("() => document.getElementById('photoLightbox').classList.contains('active')")
            assert not is_active, "Lightbox did not close on Escape key"
            print("  [PASS] Closed via Escape key")

            page.close()
        browser.close()
    print("\n>>> ALL LIGHTBOX TESTS PASSED 100%! <<<")

if __name__ == "__main__":
    test_lightbox()
