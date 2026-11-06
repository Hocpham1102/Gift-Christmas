import json
import base64
from pathlib import Path
from PIL import Image
import tempfile
from playwright.sync_api import sync_playwright

INDEX_URI = Path("index.html").resolve().as_uri()

def test_settings_modal():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for vp in [{"w": 360, "h": 640}, {"w": 375, "h": 667}, {"w": 667, "h": 375}]:
            page = browser.new_page(viewport={"width": vp["w"], "height": vp["h"]})
            page.goto(INDEX_URI)
            
            # Open settings modal
            page.click("#settingsBtn")
            page.wait_for_selector("#settingsModal.active")
            
            modal_box = page.locator(".settings-content").bounding_box()
            upload_box = page.locator("#uploadArea").bounding_box()
            close_box = page.locator("#closeModal").bounding_box()
            
            print(f"\n=== Settings Modal on {vp['w']}x{vp['h']} ===")
            print(f"  Modal box: {modal_box}")
            print(f"  Close btn: {close_box}")
            print(f"  Upload area: {upload_box}")
            
            # Check touch targets for close button
            if close_box['width'] < 44 or close_box['height'] < 44:
                print(f"  [WARN] Close button touch target is small: {close_box['width']}x{close_box['height']}")
                
            # Add 6 images via evaluate to see how grid and buttons render
            dummy_imgs = [f"data:image/jpeg;base64,/9j/4AAQSkZJRg==" for _ in range(6)]
            page.evaluate(f"""(imgs) => {{
                uploadedImages = imgs;
                updatePreview();
                updateShareButton();
            }}""", dummy_imgs)
            page.wait_for_timeout(300)
            
            # Measure replace and remove buttons
            first_replace = page.locator(".replace-img").first.bounding_box()
            first_remove = page.locator(".remove-img").first.bounding_box()
            share_box = page.locator("#shareBtn").bounding_box()
            clear_all_box = page.locator("#clearAllImagesBtn").bounding_box()
            bottom_close_box = page.locator("#bottomCloseModal").bounding_box()
            
            print(f"  Replace btn: {first_replace}")
            print(f"  Remove btn: {first_remove}")
            print(f"  Clear All btn: {clear_all_box}")
            print(f"  Bottom Close btn: {bottom_close_box}")
            print(f"  Share btn: {share_box}")
            
            if first_replace and (first_replace['width'] < 36 or first_replace['height'] < 36):
                print(f"  [WARN] Replace button touch target is small: {first_replace['width']}x{first_replace['height']}")
            if first_remove and (first_remove['width'] < 36 or first_remove['height'] < 36):
                print(f"  [WARN] Remove button touch target is small: {first_remove['width']}x{first_remove['height']}")
            if clear_all_box and (clear_all_box['height'] < 36):
                print(f"  [WARN] Clear All button touch target is small: {clear_all_box['width']}x{clear_all_box['height']}")
            if bottom_close_box and (bottom_close_box['height'] < 44):
                print(f"  [WARN] Bottom Close button touch target is small: {bottom_close_box['width']}x{bottom_close_box['height']}")
            
            # Click share button to show share container
            page.click("#shareBtn")
            page.wait_for_selector("#shareResultContainer.active")
            
            copy_share_box = page.locator("#copyShareUrlBtn").bounding_box()
            test_share_box = page.locator("#testShareUrlBtn").bounding_box()
            input_box = page.locator("#shareUrlInput").bounding_box()
            
            print(f"  Share input: {input_box}")
            print(f"  Copy btn: {copy_share_box}")
            print(f"  Test btn: {test_share_box}")
            
            page.screenshot(path=f"tests/artifacts/settings_modal_{vp['w']}x{vp['h']}.png")
            page.close()
        browser.close()

if __name__ == "__main__":
    test_settings_modal()
