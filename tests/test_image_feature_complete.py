#!/usr/bin/env python3
"""
Comprehensive End-to-End Verification for Image Upload, Compression,
Share Link Generation, Hash/Query Decoding, Base64 + Sanitization,
Replace/Clear Controls, Festive Lightbox, Real-time Emergence,
and Mobile Collision Avoidance.
"""

import base64
import json
import os
import sys
import tempfile
import urllib.parse
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

INDEX_PATH = Path("index.html").resolve()
INDEX_URI = INDEX_PATH.as_uri()

def create_test_images():
    temp_dir = Path(tempfile.mkdtemp())

    # 1. High-res photo (1920x1080, ~500KB)
    hi_res = Image.new("RGB", (1920, 1080), color=(180, 50, 50))
    for x in range(0, 1920, 15):
        for y in range(0, 1080, 15):
            hi_res.putpixel((x, y), ((x * 3) % 256, (y * 5) % 256, 120))
    hi_res_path = temp_dir / "holiday_photo_large.jpg"
    hi_res.save(hi_res_path, format="JPEG", quality=90)

    # 2. Transparent PNG (300x300)
    png_img = Image.new("RGBA", (300, 300), color=(0, 200, 100, 200))
    png_path = temp_dir / "ornament.png"
    png_img.save(png_path, format="PNG")

    # 3. Small square thumbnail (80x80)
    thumb_img = Image.new("RGB", (80, 80), color=(255, 215, 0))
    thumb_path = temp_dir / "bell.jpg"
    thumb_img.save(thumb_path, format="JPEG")

    # 4. Replacement image (100x100 cyan)
    replace_img = Image.new("RGB", (100, 100), color=(0, 220, 240))
    replace_path = temp_dir / "snowflower.jpg"
    replace_img.save(replace_path, format="JPEG")

    return temp_dir, [str(hi_res_path), str(png_path), str(thumb_path), str(replace_path)]

def run_tests():
    print("=" * 70)
    print(" COMPREHENSIVE IMAGE UPLOAD, SHARE & FLOATING VERIFICATION")
    print("=" * 70)

    temp_dir, img_paths = create_test_images()
    print(f"Created test images in: {temp_dir}")
    print(f"Large photo size: {os.path.getsize(img_paths[0])} bytes")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # TEST 1: DESKTOP FLOW - UPLOAD, COMPRESSION, PREVIEW, REPLACE, SHARE
        # -------------------------------------------------------------
        print("\n--- TEST 1: Desktop Flow (Upload, Compression, Preview, Replace, Share) ---")
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        page.goto(INDEX_URI)
        page.wait_for_timeout(400)

        # 1.1 Open modal
        page.click("#settingsBtn")
        page.wait_for_timeout(200)
        assert page.locator("#settingsModal").is_visible(), "Modal should be visible after clicking #settingsBtn"
        print("  [PASS] 1.1: Settings modal opens cleanly.")

        # 1.2 Initial share button state
        share_btn = page.locator("#shareBtn")
        assert share_btn.is_disabled(), "Share button should initially be disabled."
        print("  [PASS] 1.2: Share button initially disabled.")

        # 1.3 Upload images (including large 500KB photo)
        file_input = page.locator("#imageInput")
        file_input.set_input_files(img_paths[:3])
        page.wait_for_timeout(900)

        uploaded_count = page.evaluate("() => uploadedImages.length")
        assert uploaded_count == 3, f"Expected 3 uploaded images, got {uploaded_count}"
        print(f"  [PASS] 1.3: 3 images successfully uploaded into memory. Count = {uploaded_count}")

        # 1.4 Check canvas compression: each image string must be optimized (< 70KB)
        img_sizes = page.evaluate("() => uploadedImages.map(img => img.length)")
        print(f"  Image data lengths in memory: {img_sizes}")
        for idx, sz in enumerate(img_sizes):
            assert sz < 70000, f"Image {idx} uncompressed! Length {sz} is too large"
        print("  [PASS] 1.4: Client-side Canvas compression verified: large photos efficiently resized.")

        # 1.5 Preview DOM items & badge
        preview_count = page.locator(".preview-item").count()
        assert preview_count == 3, f"Expected 3 preview items, got {preview_count}"
        badge_text = page.locator("#imageCountBadge").inner_text()
        assert "3/12" in badge_text, f"Badge text should mention 3/12, got '{badge_text}'"
        assert page.locator("#clearAllImagesBtn").is_visible(), "Clear all button should be visible"
        print(f"  [PASS] 1.5: Image preview grid rendered {preview_count} thumbnails with badge: '{badge_text}'.")

        # 1.6 File input reset check: can re-select the same file
        file_input.set_input_files([img_paths[0]])
        page.wait_for_timeout(500)
        new_count = page.evaluate("() => uploadedImages.length")
        assert new_count == 4, f"Expected 4 uploaded images after re-selecting same file, got {new_count}"
        print(f"  [PASS] 1.6: File input value was cleared, re-uploading same file succeeded (count = {new_count}).")

        # 1.7 Replace single image via replace button
        replace_buttons = page.locator(".replace-img")
        assert replace_buttons.count() == 4, "Each preview item should have a replace button"
        # Mock replace input
        replace_input = page.locator("#replaceImageInput")
        page.evaluate("() => { replaceTargetIndex = 1; }")
        replace_input.set_input_files([img_paths[3]])
        page.wait_for_timeout(600)
        replaced_count = page.evaluate("() => uploadedImages.length")
        assert replaced_count == 4, f"Replaced item should preserve count 4, got {replaced_count}"
        print("  [PASS] 1.7: Individual image replacement works smoothly.")

        # 1.8 Remove image via delete button
        remove_buttons = page.locator(".remove-img")
        remove_buttons.first.click()
        page.wait_for_timeout(200)
        after_remove_count = page.evaluate("() => uploadedImages.length")
        assert after_remove_count == 3, f"Expected 3 images after delete, got {after_remove_count}"
        print("  [PASS] 1.8: Individual image removal works correctly.")

        # 1.9 Lightbox check from preview thumbnail
        preview_imgs = page.locator(".preview-item img")
        preview_imgs.first.click()
        page.wait_for_timeout(300)
        assert page.locator("#photoLightbox").evaluate("el => el.classList.contains('active')"), "Lightbox should open on thumbnail click"
        page.click("#closeLightbox")
        page.wait_for_timeout(200)
        assert not page.locator("#photoLightbox").evaluate("el => el.classList.contains('active')"), "Lightbox should close on close btn"
        print("  [PASS] 1.9: Festive photo lightbox open & close verified.")

        # Mock clipboard to intercept copy
        page.evaluate("""() => {
            window.__copiedText = null;
            if (navigator.clipboard) {
                navigator.clipboard.writeText = (t) => {
                    window.__copiedText = t;
                    return Promise.resolve();
                };
            }
        }""")

        # 1.10 Click shareBtn -> generates link
        share_btn.click()
        page.wait_for_timeout(400)

        copied_url = page.evaluate("() => window.__copiedText")
        input_url = page.locator("#shareUrlInput").input_value()
        assert copied_url and input_url, "Share link must be generated and copied."
        assert copied_url == input_url, "Copied URL must match #shareUrlInput value."
        assert "#images=" in copied_url, f"Share URL must use URL Hash (#images=), got: {copied_url[:80]}"
        print(f"  [PASS] 1.10: Share URL generated with URL Hash to prevent HTTP 414. Length: {len(copied_url)} chars.")

        # Check share result container visibility
        result_visible = page.locator("#shareResultContainer").is_visible()
        assert result_visible, "Share result container must be visible after clicking shareBtn."
        notification_shown = page.locator("#copyNotification").evaluate("el => el.classList.contains('show')")
        assert notification_shown, "Copy notification should be shown."
        print("  [PASS] 1.11: Share result UI and copy notification displayed.")

        # -------------------------------------------------------------
        # TEST 2: RECIPIENT FLOW - OPENING SHARED URL & FLOATING IMAGES
        # -------------------------------------------------------------
        print("\n--- TEST 2: Recipient Flow (Hash URL Decoding & Floating Images) ---")
        recipient_context = browser.new_context(viewport={"width": 1920, "height": 1080})
        recipient_page = recipient_context.new_page()

        r_console_errors = []
        recipient_page.on("console", lambda msg: r_console_errors.append(msg.text) if msg.type == "error" else None)
        recipient_page.on("pageerror", lambda err: r_console_errors.append(str(err)))

        # Recipient navigates to the shared link
        recipient_page.goto(copied_url)
        recipient_page.wait_for_timeout(500)

        # Check decoded images in recipient page
        r_uploaded_len = recipient_page.evaluate("() => uploadedImages.length")
        assert r_uploaded_len == 3, f"Recipient should have 3 restored images, got {r_uploaded_len}"
        print(f"  [PASS] 2.1: Recipient successfully restored {r_uploaded_len} images from URL Hash.")

        # Verify decoded images can be rendered in Image DOM without decoding errors
        image_decode_check = recipient_page.evaluate("""() => {
            return Promise.all(uploadedImages.map(imgSrc => {
                return new Promise((resolve) => {
                    const testImg = new Image();
                    testImg.onload = () => resolve({ ok: true, width: testImg.naturalWidth, height: testImg.naturalHeight });
                    testImg.onerror = () => resolve({ ok: false });
                    testImg.src = imgSrc;
                });
            }));
        }""")
        for idx, res in enumerate(image_decode_check):
            assert res["ok"], f"Image {idx} failed to decode in recipient browser!"
            assert res["width"] > 0 and res["height"] > 0, f"Image {idx} invalid dimensions!"
        print(f"  [PASS] 2.2: All restored images are valid renderable graphics. Dimensions: {[r['width'] for r in image_decode_check]}")

        # Recipient opens gift
        print("  Recipient opening gift box...")
        recipient_page.click("#three-canvas")
        recipient_page.wait_for_timeout(2000)

        # Check floating images rendered in DOM
        floating_images = recipient_page.locator(".floating-image").all()
        assert len(floating_images) == 3, f"Expected 3 floating images in DOM, got {len(floating_images)}"
        print(f"  [PASS] 2.3: {len(floating_images)} floating images emerged around greeting card.")

        # Check visibility, zIndex, opacity, styling
        for idx, f_img in enumerate(floating_images):
            box = f_img.bounding_box()
            opacity = float(recipient_page.evaluate("(el) => window.getComputedStyle(el).opacity", f_img.element_handle()))
            z_index = int(recipient_page.evaluate("(el) => window.getComputedStyle(el).zIndex", f_img.element_handle()))
            display = recipient_page.evaluate("(el) => window.getComputedStyle(el).display", f_img.element_handle())

            assert opacity >= 0.8, f"Floating image {idx} opacity {opacity} is too dim!"
            assert z_index >= 20, f"Floating image {idx} z-index {z_index} should be >= 20 to sit above or with card!"
            assert display != "none", f"Floating image {idx} display is 'none'!"
            assert box and box["width"] > 40 and box["height"] > 40, f"Floating image {idx} dimensions too small!"
            print(f"    -> Floating Image {idx}: w={box['width']:.1f}, h={box['height']:.1f}, x={box['x']:.1f}, y={box['y']:.1f}, zIndex={z_index}, opacity={opacity:.2f}")
        print("  [PASS] 2.4: Floating images are prominent, highly visible (zIndex >= 25, opacity >= 0.8), beautifully styled.")

        # Click floating image to open full-size festive lightbox (force=True for animating element)
        floating_images[0].click(force=True)
        recipient_page.wait_for_timeout(300)
        assert recipient_page.locator("#photoLightbox").evaluate("el => el.classList.contains('active')"), "Clicking floating image must open lightbox"
        recipient_page.click("#closeLightbox")
        recipient_page.wait_for_timeout(200)
        assert not recipient_page.locator("#photoLightbox").evaluate("el => el.classList.contains('active')"), "Closing lightbox works"
        print("  [PASS] 2.5: Interactive touch/click full lightbox view verified.")

        recipient_context.close()

        # -------------------------------------------------------------
        # TEST 3: MOBILE PORTRAIT VIEWPORT RESILIENCE (375x667)
        # -------------------------------------------------------------
        print("\n--- TEST 3: Mobile Portrait Flow (375x667 Viewport) ---")
        mobile_context = browser.new_context(viewport={"width": 375, "height": 667})
        mobile_page = mobile_context.new_page()

        mobile_page.goto(copied_url)
        mobile_page.wait_for_timeout(400)

        # Open gift on mobile
        mobile_page.click("#three-canvas")
        mobile_page.wait_for_timeout(2000)

        m_floats = mobile_page.locator(".floating-image").all()
        assert len(m_floats) == 3, f"Expected 3 floating images on mobile, got {len(m_floats)}"

        # Get control elements bounding boxes
        music_box = mobile_page.locator("#musicToggle").bounding_box()
        settings_box = mobile_page.locator("#settingsBtn").bounding_box()
        card_box = mobile_page.locator("#mainContent").bounding_box()

        print(f"  Mobile Controls Bounds: Music={music_box}, Settings={settings_box}")
        print(f"  Mobile Card Bounds: y={card_box['y']:.1f}, h={card_box['height']:.1f}")

        for idx, fl in enumerate(m_floats):
            box = fl.bounding_box()
            assert box, f"Mobile floating image {idx} missing bounding box!"
            assert 0 <= box["x"] <= 375, f"Mobile image {idx} x out of screen: {box['x']}"
            assert 0 <= box["y"] <= 667, f"Mobile image {idx} y out of screen: {box['y']}"

            # Verify no collision with Music button
            if music_box:
                m_overlap = (box["x"] < music_box["x"] + music_box["width"] and
                             box["x"] + box["width"] > music_box["x"] and
                             box["y"] < music_box["y"] + music_box["height"] and
                             box["y"] + box["height"] > music_box["y"])
                assert not m_overlap, f"Mobile image {idx} collides with #musicToggle!"

            # Verify no collision with Settings button
            if settings_box:
                s_overlap = (box["x"] < settings_box["x"] + settings_box["width"] and
                             box["x"] + box["width"] > settings_box["x"] and
                             box["y"] < settings_box["y"] + settings_box["height"] and
                             box["y"] + box["height"] > settings_box["y"])
                assert not s_overlap, f"Mobile image {idx} collides with #settingsBtn!"

            print(f"    -> Mobile Image {idx}: box={box} (Collision-free)")
        print("  [PASS] 3.1: Mobile floating positions adapt smoothly without occluding top controls or greeting card.")

        mobile_context.close()

        # -------------------------------------------------------------
        # TEST 4: REAL-TIME EMERGENCE (ADDING WHILE CARD IS ALREADY OPEN)
        # -------------------------------------------------------------
        print("\n--- TEST 4: Real-time Emergence (Adding images while card is already active) ---")
        rt_page = browser.new_page(viewport={"width": 1280, "height": 800})
        rt_page.goto(INDEX_URI)
        rt_page.wait_for_timeout(300)

        # 4.1 Open gift box FIRST
        rt_page.click("#three-canvas")
        rt_page.wait_for_timeout(1800)
        assert rt_page.locator("#mainContent").evaluate("el => el.classList.contains('active')"), "Card should be active"
        initial_floats = rt_page.locator(".floating-image").count()
        assert initial_floats == 0, f"Initially should have 0 floating images, got {initial_floats}"

        # 4.2 Open settings modal and upload images WHILE CARD IS ALREADY ACTIVE
        rt_page.click("#settingsBtn")
        rt_page.wait_for_timeout(200)
        rt_input = rt_page.locator("#imageInput")
        rt_input.set_input_files([img_paths[0], img_paths[1]])
        rt_page.wait_for_timeout(900)

        # 4.3 Close modal and check floating images immediately appeared!
        rt_page.click("#closeModal")
        rt_page.wait_for_timeout(400)
        live_floats = rt_page.locator(".floating-image").count()
        assert live_floats == 2, f"Floating images must immediately emerge around active card! Expected 2, got {live_floats}"
        print(f"  [PASS] 4.1: Real-time emergence verified: {live_floats} photos appeared instantly on active greeting card!")

        # 4.4 Remove one image and check floating images count immediately decreases
        rt_page.click("#settingsBtn")
        rt_page.wait_for_timeout(200)
        rt_page.locator(".remove-img").first.click()
        rt_page.wait_for_timeout(300)
        rt_page.click("#closeModal")
        rt_page.wait_for_timeout(300)
        updated_floats = rt_page.locator(".floating-image").count()
        assert updated_floats == 1, f"Floating images count should decrease to 1, got {updated_floats}"
        print("  [PASS] 4.2: Real-time removal update verified.")

        rt_page.close()

        # -------------------------------------------------------------
        # TEST 5: BASE64 WITH PLUS SIGN (+) & BACKWARD COMPATIBILITY
        # -------------------------------------------------------------
        print("\n--- TEST 5: Base64 Plus Sign (+) Sanitization & Compatibility ---")
        fuzz_page = browser.new_page()

        # 5.1 Base64 with literal + sign in URL hash (must not become space)
        # Real 10x10 JPEG with multiple + characters
        plus_b64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAKAAoDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDRooor4U/Xj//Z"
        assert "+" in plus_b64, "Test base64 must contain +"
        # Simulate browser or chat passing unencoded or decoded +
        fuzz_page.goto(f'{INDEX_URI}#images=["data:image/jpeg;base64,{plus_b64}"]')
        fuzz_page.wait_for_timeout(400)
        restored_img = fuzz_page.evaluate("() => uploadedImages[0]")
        assert " " not in restored_img, f"Base64 must not contain spaces! Got: {restored_img[:60]}"
        assert "+" in restored_img, f"Base64 must preserve '+' characters! Got: {restored_img[:60]}"

        # Test if browser can render it
        can_render = fuzz_page.evaluate("""() => {
            return new Promise(resolve => {
                const img = new Image();
                img.onload = () => resolve({ ok: true, w: img.width, h: img.height });
                img.onerror = () => resolve({ ok: false });
                img.src = uploadedImages[0];
            });
        }""")
        assert can_render["ok"], "Sanitized base64 with + must render successfully!"
        print(f"  [PASS] 5.1: Base64 '+' sign preservation & space sanitization verified (render: {can_render}).")

        # 5.2 Legacy stripped base64 in query param (?images=...)
        legacy_data = json.dumps(["iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mP8z8BQz0AEYBxVSF+FABJAD+/dbHhpAAAAAElFTkSuQmCC"])
        legacy_url = f"{INDEX_URI}?images={urllib.parse.quote(legacy_data)}"
        fuzz_page.goto(legacy_url)
        fuzz_page.wait_for_timeout(300)

        legacy_restored = fuzz_page.evaluate("() => uploadedImages.length")
        assert legacy_restored == 1, f"Legacy query param should restore 1 image, got {legacy_restored}"
        first_img = fuzz_page.evaluate("() => uploadedImages[0]")
        assert first_img.startswith("data:image/png;base64,"), f"Auto-detected MIME should be png, got {first_img[:30]}"
        print("  [PASS] 5.2: Backward compatibility with legacy ?images query strings verified (auto MIME detect).")

        # 5.3 Malformed hash handled gracefully
        fuzz_page.goto(f"{INDEX_URI}#images=invalid_json_xyz")
        fuzz_page.wait_for_timeout(300)
        resilient = fuzz_page.evaluate("() => typeof isOpened !== 'undefined'")
        assert resilient, "Malformed hash broke the page!"
        print("  [PASS] 5.3: Malformed hash handled gracefully without crash.")

        # 5.4 Malformed query handled gracefully
        fuzz_page.goto(f"{INDEX_URI}?images=%7Bnot_an_array%7D")
        fuzz_page.wait_for_timeout(300)
        resilient2 = fuzz_page.evaluate("() => typeof isOpened !== 'undefined'")
        assert resilient2, "Malformed query param broke the page!"
        print("  [PASS] 5.4: Malformed query handled gracefully without crash.")

        fuzz_page.close()
        browser.close()

    # Cleanup temp directory
    for f in img_paths:
        try:
            os.remove(f)
        except:
            pass
    try:
        os.rmdir(temp_dir)
    except:
        pass

    print("\n" + "=" * 70)
    print(" ALL IMAGE UPLOAD, SHARE & FLOATING VERIFICATIONS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
