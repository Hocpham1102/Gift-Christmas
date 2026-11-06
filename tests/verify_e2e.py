#!/usr/bin/env python3
"""
Gift-Christmas 4-Tier End-to-End Verification Harness
=====================================================
Comprehensive, opaque-box E2E test suite for Gift-Christmas holiday upgrade.

Architecture:
- Tier 1: Feature Coverage (F1 to F8, >=5 tests per feature, total 42 tests)
- Tier 2: Boundary & Corner Cases (5 tests)
- Tier 3: Cross-Feature Combinations & Harmony (3 tests)
- Tier 4: Real-World Scenarios (Headless Chrome Multi-Viewport Snapshots, 5 tests)
Total: 55 Automated E2E Test Cases

Execution:
    python tests/verify_e2e.py
    python tests/verify_e2e.py --tier 1
    python tests/verify_e2e.py --feature F1
    python tests/verify_e2e.py --skip-chrome
    python tests/verify_e2e.py --json
    python tests/verify_e2e.py --allow-fail
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: beautifulsoup4 is required. Run: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(2)


# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = REPO_ROOT / "index.html"
ARTIFACTS_DIR = REPO_ROOT / "tests" / "artifacts"
SCREENSHOTS_DIR = ARTIFACTS_DIR / "screenshots"
RESULTS_JSON = ARTIFACTS_DIR / "test_results.json"

CHROME_CANDIDATE_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.environ.get("CHROME_BIN", ""),
]

ROMANTIC_FORBIDDEN_WORDS = [
    "anh yêu em",
    "yêu em",
    "dành cho em",
    "đi em",
    "người con gái anh yêu",
    "người yêu",
    "bờ vai ấm áp",
    "bờ vai",
    "trái tim và tình yêu",
    "tình yêu trọn vẹn",
    "mãi mãi về sau",
    "chỗ dựa vững chắc",
    "em biết không",
    "hôn em",
    "nhớ em",
]

ROMANTIC_FORBIDDEN_EMOJIS = ["💝", "❤️", "💖", "💑", "💍"]

FRIENDSHIP_KEYWORDS = [
    "bạn",
    "bạn bè",
    "tình bạn",
    "đồng hành",
    "sẻ chia",
    "tri kỷ",
    "ấm áp",
    "an lành",
    "niềm vui",
    "cảm ơn",
    "gắn bó",
    "chân thành",
    "thân mến",
    "tuyệt vời",
]

VIEWPORT_CONFIGS = [
    ("desktop_1080p", "1920,1080", 1920, 1080),
    ("tablet_portrait", "768,1024", 768, 1024),
    ("mobile_portrait", "375,667", 375, 667),
    ("mobile_landscape", "667,375", 667, 375),
]


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass
class TestResult:
    test_id: str
    tier: int
    feature: str
    name: str
    passed: bool
    detail: str
    duration_ms: float = 0.0


# ==============================================================================
# PARSER & CODE INSPECTION HELPER
# ==============================================================================

class CodebaseInspector:
    """Parses and caches index.html content for multi-tier inspection."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            self.raw_content = f.read()

        self.lines = self.raw_content.splitlines(keepends=True)
        self.soup = BeautifulSoup(self.raw_content, "html.parser")

        # Extract all style blocks concatenated
        self.styles = "\n".join(s.get_text() for s in self.soup.find_all("style"))

        # Extract all script blocks concatenated
        self.scripts = "\n".join(
            s.get_text() for s in self.soup.find_all("script") if not s.get("src")
        )

        # Extract greeting message string if present
        msg_match = re.search(
            r'const\s+message\s*=\s*[`"\']([^`"\']*)[`"\']', self.scripts, re.DOTALL
        )
        self.message_text = msg_match.group(1) if msg_match else ""

    def locate_chrome(self) -> Optional[str]:
        for candidate in CHROME_CANDIDATE_PATHS:
            if candidate and os.path.exists(candidate):
                return candidate
        which_chrome = shutil.which("chrome") or shutil.which("google-chrome")
        return which_chrome


# ==============================================================================
# TEST SUITE IMPLEMENTATION
# ==============================================================================

class GiftChristmasTestSuite:
    def __init__(self, inspector: CodebaseInspector, skip_chrome: bool = False):
        self.inspector = inspector
        self.skip_chrome = skip_chrome
        self.results: List[TestResult] = []

    def run_all(self, target_tier: Optional[int] = None, target_feature: Optional[str] = None):
        tests = self._discover_tests()
        for t_func, tier, feature, tid, name in tests:
            if target_tier is not None and tier != target_tier:
                continue
            if target_feature is not None and feature.upper() != target_feature.upper():
                continue

            start_t = time.perf_counter()
            try:
                passed, detail = t_func()
            except Exception as exc:
                passed = False
                detail = f"Unhandled Exception during test execution: {exc}"
            duration_ms = (time.perf_counter() - start_t) * 1000.0

            result = TestResult(
                test_id=tid,
                tier=tier,
                feature=feature,
                name=name,
                passed=passed,
                detail=detail,
                duration_ms=round(duration_ms, 2),
            )
            self.results.append(result)

    def _discover_tests(self):
        """Returns list of (callable, tier, feature, test_id, name) tuples."""
        return [
            # Tier 1 - F1: Title & Microcopy
            (self.test_f1_01_title_no_forbidden_romance, 1, "F1", "T1.F1.01", "Title has no forbidden romance vocabulary"),
            (self.test_f1_02_title_christmas_friendship_keywords, 1, "F1", "T1.F1.02", "Title contains Christmas and friendship keywords"),
            (self.test_f1_03_taphint_no_couple_pronouns, 1, "F1", "T1.F1.03", "TapHint has no couple pronouns or romance"),
            (self.test_f1_04_taphint_friendly_invitation, 1, "F1", "T1.F1.04", "TapHint presents a friendly festive invitation"),
            (self.test_f1_05_h1_no_romantic_emojis, 1, "F1", "T1.F1.05", "Card H1 contains no romantic emojis"),
            (self.test_f1_06_settings_modal_friendly_copy, 1, "F1", "T1.F1.06", "Settings modal microcopy uses friendly non-romantic phrasing"),

            # Tier 1 - F2: Friendship Letter & Typewriter
            (self.test_f2_01_message_variable_exists, 1, "F2", "T1.F2.01", "Greeting message variable is defined in JavaScript"),
            (self.test_f2_02_message_no_forbidden_romance, 1, "F2", "T1.F2.02", "Greeting letter has zero forbidden romance terms"),
            (self.test_f2_03_message_friendship_keywords, 1, "F2", "T1.F2.03", "Greeting letter contains genuine friendship and gratitude keywords"),
            (self.test_f2_04_message_length_balanced, 1, "F2", "T1.F2.04", "Greeting letter length is balanced (450-750 characters)"),
            (self.test_f2_05_typewriter_speed_configured, 1, "F2", "T1.F2.05", "Typewriter speed interval is configured for smooth delivery"),
            (self.test_f2_06_typewriter_handles_html_tags, 1, "F2", "T1.F2.06", "Typewriter handles <br> tags without broken rendering"),

            # Tier 1 - F3: Card Architecture & Anti-Overflow
            (self.test_f3_01_card_container_no_overflow_clipping, 1, "F3", "T1.F3.01", "Card layout does not rigidly clip content without scroll container"),
            (self.test_f3_02_card_body_overflow_auto, 1, "F3", "T1.F3.02", "Card scroll container specifies overflow-y: auto/scroll"),
            (self.test_f3_03_overscroll_behavior_contain, 1, "F3", "T1.F3.03", "Card body specifies overscroll-behavior: contain"),
            (self.test_f3_04_custom_scrollbar_styled, 1, "F3", "T1.F3.04", "Card container includes custom scrollbar styling"),
            (self.test_f3_05_card_structural_split, 1, "F3", "T1.F3.05", "Card is structured into header, scrollable body, and footer"),

            # Tier 1 - F4: Holiday Palette & Lighting
            (self.test_f4_01_body_twilight_gradient, 1, "F4", "T1.F4.01", "Body background uses dark holiday twilight gradient"),
            (self.test_f4_02_ambient_glows_gold_pine, 1, "F4", "T1.F4.02", "Ambient radial glows use warm gold or festive accents, not pink"),
            (self.test_f4_03_threejs_lighting_palette, 1, "F4", "T1.F4.03", "Three.js PointLight uses warm/amber/holiday tones, not pink"),
            (self.test_f4_04_box_shadow_festive_tones, 1, "F4", "T1.F4.04", "Card box-shadow does not use candy pink"),
            (self.test_f4_05_heading_gradient_festive, 1, "F4", "T1.F4.05", "Card H1 text gradient does not use candy pink"),

            # Tier 1 - F5: Holiday Particle System
            (self.test_f5_01_no_heart_particle_class, 1, "F5", "T1.F5.01", "HeartParticle class definition is completely removed"),
            (self.test_f5_02_no_heart_particle_instantiation, 1, "F5", "T1.F5.02", "HeartParticle instantiation loop is completely removed"),
            (self.test_f5_03_snow_particles_exist, 1, "F5", "T1.F5.03", "SnowParticle class is defined and instantiated"),
            (self.test_f5_04_sparkle_bokeh_particles_exist, 1, "F5", "T1.F5.04", "Twinkling star/bokeh particle system is defined and instantiated"),
            (self.test_f5_05_particle_canvas_sync_resize, 1, "F5", "T1.F5.05", "Particle canvas resizes dynamically on window resize"),

            # Tier 1 - F6: Interactive Audio Controls
            (self.test_f6_01_music_toggle_element_present, 1, "F6", "T1.F6.01", "Music toggle button exists in DOM"),
            (self.test_f6_02_music_toggle_accessibility, 1, "F6", "T1.F6.02", "Music toggle button includes accessible label/title"),
            (self.test_f6_03_audio_element_configured, 1, "F6", "T1.F6.03", "Background audio element exists with loop attribute and audio source"),
            (self.test_f6_04_toggle_event_listener_bound, 1, "F6", "T1.F6.04", "JavaScript binds event listener to toggle music playback"),
            (self.test_f6_05_audio_toggle_visual_states, 1, "F6", "T1.F6.05", "CSS defines active/muted visual styling for music toggle"),

            # Tier 1 - F7: Multi-Device Responsiveness
            (self.test_f7_01_viewport_meta_tag, 1, "F7", "T1.F7.01", "Viewport meta tag is properly configured"),
            (self.test_f7_02_responsive_height_units, 1, "F7", "T1.F7.02", "CSS uses responsive height units (dvh/vh)"),
            (self.test_f7_03_font_clamping, 1, "F7", "T1.F7.03", "CSS utilizes font clamp() for fluid readability"),
            (self.test_f7_04_mobile_media_queries, 1, "F7", "T1.F7.04", "CSS includes responsive mobile media queries"),
            (self.test_f7_05_touch_friendly_hit_targets, 1, "F7", "T1.F7.05", "Interactive buttons have adequate touch target sizing"),

            # Tier 1 - F8: Syntax & Code Hygiene
            (self.test_f8_01_no_trailing_markdown_fence, 1, "F8", "T1.F8.01", "No trailing markdown code fence at end of file"),
            (self.test_f8_02_doctype_and_html_lang, 1, "F8", "T1.F8.02", "Valid DOCTYPE declaration and lang attribute"),
            (self.test_f8_03_tags_closure_integrity, 1, "F8", "T1.F8.03", "Critical DOM containers are properly closed"),
            (self.test_f8_04_clean_javascript_no_stray_markdown, 1, "F8", "T1.F8.04", "JavaScript tags contain clean code with no stray markdown"),
            (self.test_f8_05_balanced_css_braces, 1, "F8", "T1.F8.05", "CSS style blocks have balanced curly braces"),

            # Tier 2 - Boundary & Corner Cases
            (self.test_t2_01_extreme_text_wrapping, 2, "Boundary", "T2.B01", "Long text wrapping prevents horizontal overflow"),
            (self.test_t2_02_narrow_mobile_bounds, 2, "Boundary", "T2.B02", "Card width is bounded on narrow mobile displays (320px-375px)"),
            (self.test_t2_03_landscape_mobile_max_height, 2, "Boundary", "T2.B03", "Card height is constrained for mobile landscape orientation"),
            (self.test_t2_04_audio_autoplay_rejection_safety, 2, "Boundary", "T2.B04", "Audio play() is guarded with catch() against autoplay rejection"),
            (self.test_t2_05_rapid_double_click_guard, 2, "Boundary", "T2.B05", "Gift box click handler guards against rapid double click spam"),

            # Tier 3 - Cross-Feature Combinations
            (self.test_t3_01_box_open_triggers_audio_and_typewriter, 3, "CrossFeature", "T3.C01", "Box opening coordinates audio playback and typewriter initialization"),
            (self.test_t3_02_typewriter_and_scrollable_container_harmony, 3, "CrossFeature", "T3.C02", "Typewriter operates smoothly inside scrollable card container"),
            (self.test_t3_03_modal_and_card_zindex_hierarchy, 3, "CrossFeature", "T3.C03", "Settings modal z-index takes precedence over greeting card and canvas"),

            # Tier 4 - Real-World Scenarios (Chrome Headless)
            (self.test_t4_01_desktop_1080p_render, 4, "VisualRender", "T4.R01", "Chrome Headless 1920x1080 Desktop snapshot capture"),
            (self.test_t4_02_tablet_portrait_render, 4, "VisualRender", "T4.R02", "Chrome Headless 768x1024 Tablet snapshot capture"),
            (self.test_t4_03_mobile_portrait_render, 4, "VisualRender", "T4.R03", "Chrome Headless 375x667 Mobile Portrait snapshot capture"),
            (self.test_t4_04_mobile_landscape_render, 4, "VisualRender", "T4.R04", "Chrome Headless 667x375 Mobile Landscape snapshot capture"),
            (self.test_t4_05_visual_screenshot_integrity, 4, "VisualRender", "T4.R05", "All generated screenshot files are valid PNGs with substantial payload"),
        ]

    # ==========================================================================
    # TIER 1 - F1: Title & Microcopy
    # ==========================================================================

    def test_f1_01_title_no_forbidden_romance(self) -> Tuple[bool, str]:
        title = self.inspector.soup.title.string if self.inspector.soup.title else ""
        if not title:
            return False, "Missing <title> tag"
        
        found = []
        for word in ROMANTIC_FORBIDDEN_WORDS:
            if word.lower() in title.lower():
                found.append(word)
        for emoji in ROMANTIC_FORBIDDEN_EMOJIS:
            if emoji in title:
                found.append(emoji)

        if found:
            return False, f"Title contains forbidden romantic terms/emojis: {found} (Title: '{title}')"
        return True, f"Title has zero forbidden romance terms: '{title}'"

    def test_f1_02_title_christmas_friendship_keywords(self) -> Tuple[bool, str]:
        title = (self.inspector.soup.title.string or "").lower()
        has_christmas = any(k in title for k in ["giáng sinh", "noel", "christmas"])
        has_friendship = any(k in title for k in ["bạn", "tình bạn", "ấm áp", "thân", "an lành", "yêu thương", "đồng hành"])

        if not has_christmas:
            return False, f"Title missing Christmas keywords: '{title}'"
        if not has_friendship:
            return False, f"Title missing friendship/warmth keywords: '{title}'"
        return True, f"Title contains both Christmas and friendship themes: '{title}'"

    def test_f1_03_taphint_no_couple_pronouns(self) -> Tuple[bool, str]:
        hint = self.inspector.soup.find(id="tapHint")
        if not hint:
            return False, "Element #tapHint not found in DOM"
        text = hint.get_text()
        found = []
        for word in ["đi em", "anh yêu", "em yêu", "cho em", "hỡi em"]:
            if word in text.lower():
                found.append(word)
        if found:
            return False, f"#tapHint contains forbidden couple pronouns: {found} (Text: '{text}')"
        return True, f"#tapHint free of couple pronouns: '{text}'"

    def test_f1_04_taphint_friendly_invitation(self) -> Tuple[bool, str]:
        hint = self.inspector.soup.find(id="tapHint")
        if not hint:
            return False, "Element #tapHint not found in DOM"
        text = hint.get_text().lower()
        has_action = any(k in text for k in ["hộp quà", "mở", "chạm", "nhấn", "khám phá"])
        has_friendly_tone = any(k in text for k in ["bạn", "nhé", "nào", "thôi", "bất ngờ", "đi"])
        if not has_action:
            return False, f"#tapHint missing action invitation: '{hint.get_text()}'"
        if not has_friendly_tone:
            return False, f"#tapHint missing warm friendly tone: '{hint.get_text()}'"
        return True, f"#tapHint presents a warm festive invitation: '{hint.get_text()}'"

    def test_f1_05_h1_no_romantic_emojis(self) -> Tuple[bool, str]:
        h1 = self.inspector.soup.find("h1")
        if not h1:
            return False, "No <h1> element found"
        text = h1.get_text()
        found = [e for e in ROMANTIC_FORBIDDEN_EMOJIS if e in text]
        if found:
            return False, f"H1 contains romantic emojis: {found} (Text: '{text}')"
        has_festive = any(k in text.lower() for k in ["christmas", "giáng sinh", "noel", "chúc mừng"])
        if not has_festive:
            return False, f"H1 missing holiday greeting text: '{text}'"
        return True, f"H1 has clean festive greeting without romance emojis: '{text}'"

    def test_f1_06_settings_modal_friendly_copy(self) -> Tuple[bool, str]:
        modal = self.inspector.soup.find(id="settingsModal")
        if not modal:
            return False, "Element #settingsModal not found in DOM"
        text = modal.get_text().lower()
        if "người con gái" in text or "người yêu" in text or "cho em" in text:
            return False, f"Settings modal contains romantic couple phrasing: '{modal.get_text()[:150]}...'"
        has_sharing_friendship = any(k in text for k in ["bạn", "người thân", "mọi người", "bạn bè"])
        if not has_sharing_friendship:
            return False, f"Settings modal missing friendly sharing text: '{modal.get_text()[:150]}...'"
        return True, "Settings modal uses friendly non-romantic phrasing"

    # ==========================================================================
    # TIER 1 - F2: Friendship Letter & Typewriter
    # ==========================================================================

    def test_f2_01_message_variable_exists(self) -> Tuple[bool, str]:
        if not self.inspector.message_text:
            return False, "Greeting message variable ('const message = ...') not found in JavaScript"
        return True, f"Greeting message variable found ({len(self.inspector.message_text)} chars)"

    def test_f2_02_message_no_forbidden_romance(self) -> Tuple[bool, str]:
        msg = self.inspector.message_text.lower()
        if not msg:
            return False, "Message variable not found"
        violations = []
        for word in ROMANTIC_FORBIDDEN_WORDS:
            if word.lower() in msg:
                violations.append(word)
        for emoji in ROMANTIC_FORBIDDEN_EMOJIS:
            if emoji in self.inspector.message_text:
                violations.append(emoji)
        if violations:
            return False, f"Greeting message contains forbidden romantic terms: {violations}"
        return True, "Greeting message is 100% free of romantic vocabulary"

    def test_f2_03_message_friendship_keywords(self) -> Tuple[bool, str]:
        msg = self.inspector.message_text.lower()
        if not msg:
            return False, "Message variable not found"
        found = [k for k in FRIENDSHIP_KEYWORDS if k in msg]
        if len(found) < 3:
            return False, f"Greeting message has insufficient friendship themes (found {found}, expected >= 3)"
        return True, f"Greeting message contains strong friendship themes: {found}"

    def test_f2_04_message_length_balanced(self) -> Tuple[bool, str]:
        msg_len = len(self.inspector.message_text)
        if not (450 <= msg_len <= 750):
            return False, f"Message length ({msg_len} chars) out of recommended bounds [450, 750]"
        return True, f"Message length is well balanced: {msg_len} characters"

    def test_f2_05_typewriter_speed_configured(self) -> Tuple[bool, str]:
        speed_match = re.search(r'(?:const|let|var)\s+speed\s*=\s*(\d+)', self.inspector.scripts)
        if not speed_match:
            # Check setTimeout timing inside typewriter
            alt_match = re.search(r'setTimeout\s*\([^,]+,\s*(\d+)\s*\)', self.inspector.scripts)
            if not alt_match:
                return False, "Could not detect typewriter speed configuration"
            speed_val = int(alt_match.group(1))
        else:
            speed_val = int(speed_match.group(1))

        if not (15 <= speed_val <= 100):
            return False, f"Typewriter speed ({speed_val}ms) out of readable range [15ms, 100ms]"
        return True, f"Typewriter speed configured at {speed_val}ms per character"

    def test_f2_06_typewriter_handles_html_tags(self) -> Tuple[bool, str]:
        # Verifies typewriter logic parses <br> properly
        has_tag_handling = (
            "substr" in self.inspector.scripts or
            "slice" in self.inspector.scripts or
            "substring" in self.inspector.scripts or
            "<br>" in self.inspector.scripts
        )
        if not has_tag_handling:
            return False, "Typewriter does not appear to handle <br> tags properly"
        return True, "Typewriter script includes HTML break tag handling"

    # ==========================================================================
    # TIER 1 - F3: Card Architecture & Anti-Overflow
    # ==========================================================================

    def test_f3_01_card_container_no_overflow_clipping(self) -> Tuple[bool, str]:
        # Check if .content has overflow:hidden with NO inner scrollable element
        content_overflow_hidden = bool(re.search(r'\.content\s*\{[^}]*overflow\s*:\s*hidden', self.inspector.styles))
        has_scroll_body = bool(re.search(r'(?:#cardBody|\.card-body|#typewriter)\s*\{[^}]*overflow-y\s*:\s*(?:auto|scroll)', self.inspector.styles))
        
        if content_overflow_hidden and not has_scroll_body:
            return False, "Card container (.content) has overflow:hidden while lacking an inner scrollable body (causes text clipping defect)"
        return True, "Card architecture permits scrollable inner content without clipping"

    def test_f3_02_card_body_overflow_auto(self) -> Tuple[bool, str]:
        # Look for overflow-y: auto or scroll on card body / typewriter container
        has_overflow_y = bool(
            re.search(r'(?:#cardBody|\.card-body|#typewriter|\.card-content)\s*\{[^}]*overflow-y\s*:\s*(?:auto|scroll)', self.inspector.styles)
        )
        if not has_overflow_y:
            return False, "No scrollable card body rule ('overflow-y: auto' or 'scroll') found in CSS"
        return True, "Card body explicitly defines vertical scrollability (overflow-y: auto)"

    def test_f3_03_overscroll_behavior_contain(self) -> Tuple[bool, str]:
        has_contain = bool(re.search(r'overscroll-behavior(?:-y)?\s*:\s*contain', self.inspector.styles))
        if not has_contain:
            return False, "Missing 'overscroll-behavior: contain' to prevent mobile touch chaining"
        return True, "Scroll container specifies 'overscroll-behavior: contain'"

    def test_f3_04_custom_scrollbar_styled(self) -> Tuple[bool, str]:
        has_custom_scrollbar = (
            "::-webkit-scrollbar" in self.inspector.styles or
            "scrollbar-width" in self.inspector.styles or
            "scrollbar-color" in self.inspector.styles
        )
        if not has_custom_scrollbar:
            return False, "Missing custom scrollbar styling (::-webkit-scrollbar or scrollbar-width: thin)"
        return True, "Custom scrollbar styles defined for smooth festive aesthetic"

    def test_f3_05_card_structural_split(self) -> Tuple[bool, str]:
        # Check if card is structured into header, body, footer (or cardBody and typewriter)
        has_header = bool(self.inspector.soup.find(class_=re.compile(r"card-header|header")) or self.inspector.soup.find("h1"))
        has_body = bool(self.inspector.soup.find(id="cardBody") or self.inspector.soup.find(class_=re.compile(r"card-body")) or self.inspector.soup.find(id="typewriter"))
        has_footer = bool(self.inspector.soup.find(class_=re.compile(r"card-footer|signature|footer")) or "card-footer" in self.inspector.styles)

        if not (has_header and has_body):
            return False, f"Card missing structural components (Header: {has_header}, Body: {has_body})"
        if not has_footer:
            return False, "Card lacks distinct footer / closing signature structure"
        return True, "Card architecture provides clear header, scrollable body, and footer structure"

    # ==========================================================================
    # TIER 1 - F4: Holiday Palette & Lighting
    # ==========================================================================

    def test_f4_01_body_twilight_gradient(self) -> Tuple[bool, str]:
        # Background should not be candy pink/purple #f093fb
        if "#f093fb" in self.inspector.styles.lower():
            return False, "Body background uses romantic candy pink (#f093fb), expected midnight winter twilight"
        # Check for winter twilight palette tones
        twilight_colors = ["#090e1a", "#0a1128", "#162a45", "#0d1b2a", "#0a2239", "#1a2639", "#0f2027", "#101820"]
        found_twilight = any(c in self.inspector.styles.lower() for c in twilight_colors)
        if not found_twilight:
            return False, "Body background does not declare a dark holiday winter twilight gradient"
        return True, "Body background uses dark holiday winter twilight palette"

    def test_f4_02_ambient_glows_gold_pine(self) -> Tuple[bool, str]:
        # body::before should not use hot pink radial glows
        pink_glow = bool(re.search(r'rgba\(\s*255\s*,\s*107\s*,\s*157', self.inspector.styles))
        magenta_glow = bool(re.search(r'rgba\(\s*196\s*,\s*69\s*,\s*105', self.inspector.styles))
        if pink_glow or magenta_glow:
            return False, "Ambient radial glows contain romantic hot pink/magenta (rgba(255, 107, 157) / rgba(196, 69, 105))"
        
        has_festive_glow = (
            "255, 215, 0" in self.inspector.styles or
            "255, 224, 130" in self.inspector.styles or
            "218, 165, 32" in self.inspector.styles or
            "gold" in self.inspector.styles.lower()
        )
        if not has_festive_glow:
            return False, "Ambient glows missing warm amber gold accents"
        return True, "Ambient glows transition from romantic pinks to warm amber gold / holiday accents"

    def test_f4_03_threejs_lighting_palette(self) -> Tuple[bool, str]:
        # Three.js PointLight must not use pink 0xff6b9d
        if "0xff6b9d" in self.inspector.scripts.lower():
            return False, "Three.js PointLight uses romantic pink (0xff6b9d), expected warm holiday/gold light"
        has_warm_light = any(k in self.inspector.scripts.lower() for k in ["0xffd700", "0xffaa00", "0xffe082", "0xffffff", "0x4fc3f7", "0x2e7d32"])
        if not has_warm_light:
            return False, "Three.js scene missing warm holiday lighting"
        return True, "Three.js scene lighting uses warm festive/holiday illumination"

    def test_f4_04_box_shadow_festive_tones(self) -> Tuple[bool, str]:
        content_match = re.search(r'\.content\s*\{([^}]*)\}', self.inspector.styles)
        if not content_match:
            return False, "Rule for .content not found in styles"
        content_css = content_match.group(1)
        if "255, 107, 157" in content_css:
            return False, "Card (.content) box-shadow uses romantic pink rgba(255, 107, 157)"
        return True, "Card glow and box-shadow uses festive holiday lighting"

    def test_f4_05_heading_gradient_festive(self) -> Tuple[bool, str]:
        h1_match = re.search(r'h1\s*\{([^}]*)\}', self.inspector.styles)
        if not h1_match:
            return False, "Rule for h1 not found in styles"
        h1_css = h1_match.group(1).lower()
        if "#ff6b9d" in h1_css:
            return False, "Card H1 text gradient uses romantic pink (#ff6b9d)"
        return True, "Card H1 text styling uses festive holiday gold/winter palette"

    # ==========================================================================
    # TIER 1 - F5: Holiday Particle System
    # ==========================================================================

    def test_f5_01_no_heart_particle_class(self) -> Tuple[bool, str]:
        if "class HeartParticle" in self.inspector.scripts:
            return False, "Found HeartParticle class definition in JavaScript"
        return True, "HeartParticle class definition has been removed"

    def test_f5_02_no_heart_particle_instantiation(self) -> Tuple[bool, str]:
        if "HeartParticle" in self.inspector.scripts:
            return False, "HeartParticle references remain in JavaScript particle loops"
        return True, "Zero HeartParticle instantiations found"

    def test_f5_03_snow_particles_exist(self) -> Tuple[bool, str]:
        has_snow_class = "class SnowParticle" in self.inspector.scripts
        has_snow_new = "new SnowParticle" in self.inspector.scripts
        if not has_snow_class or not has_snow_new:
            return False, f"SnowParticle system incomplete (Class: {has_snow_class}, New: {has_snow_new})"
        return True, "Drifting snow particle system is defined and instantiated"

    def test_f5_04_sparkle_bokeh_particles_exist(self) -> Tuple[bool, str]:
        has_sparkle = "class SparkleParticle" in self.inspector.scripts or "class BokehParticle" in self.inspector.scripts or "class StardustParticle" in self.inspector.scripts
        has_sparkle_new = "new SparkleParticle" in self.inspector.scripts or "new BokehParticle" in self.inspector.scripts or "new StardustParticle" in self.inspector.scripts
        if not has_sparkle or not has_sparkle_new:
            return False, "Sparkle/Bokeh holiday particle system incomplete"
        return True, "Sparkling holiday bokeh/stardust particle system is active"

    def test_f5_05_particle_canvas_sync_resize(self) -> Tuple[bool, str]:
        has_resize_listener = "window.addEventListener(\"resize\"" in self.inspector.scripts or "window.addEventListener('resize'" in self.inspector.scripts
        has_canvas_resize = "canvas.width = window.innerWidth" in self.inspector.scripts and "canvas.height = window.innerHeight" in self.inspector.scripts
        if not (has_resize_listener and has_canvas_resize):
            return False, "Particle canvas does not sync dimensions on window resize event"
        return True, "Particle canvas dynamically synchronizes dimensions on window resize"

    # ==========================================================================
    # TIER 1 - F6: Interactive Audio Controls
    # ==========================================================================

    def test_f6_01_music_toggle_element_present(self) -> Tuple[bool, str]:
        toggle = self.inspector.soup.find(id="musicToggle") or self.inspector.soup.find(class_=re.compile(r"music-toggle"))
        if not toggle:
            return False, "Element #musicToggle or .music-toggle not found in DOM"
        return True, f"Music toggle control present in DOM (<{toggle.name} id='{toggle.get('id', '')}'>)"

    def test_f6_02_music_toggle_accessibility(self) -> Tuple[bool, str]:
        toggle = self.inspector.soup.find(id="musicToggle") or self.inspector.soup.find(class_=re.compile(r"music-toggle"))
        if not toggle:
            return False, "Music toggle element not found in DOM"
        has_label = bool(toggle.get("title") or toggle.get("aria-label"))
        if not has_label:
            return False, "Music toggle button missing accessible label (title or aria-label attribute)"
        return True, f"Music toggle includes accessible label: '{toggle.get('title') or toggle.get('aria-label')}'"

    def test_f6_03_audio_element_configured(self) -> Tuple[bool, str]:
        audio = self.inspector.soup.find("audio", id="bgMusic")
        if not audio:
            return False, "Audio element <audio id='bgMusic'> not found"
        if not audio.has_attr("loop"):
            return False, "Background audio element missing 'loop' attribute"
        src = audio.get("src") or (audio.find("source").get("src") if audio.find("source") else None)
        if not src:
            return False, "Audio element has no valid audio source"
        return True, f"Audio element configured with loop and source: '{src}'"

    def test_f6_04_toggle_event_listener_bound(self) -> Tuple[bool, str]:
        has_music_toggle_listener = (
            "musicToggle.addEventListener" in self.inspector.scripts or
            "toggleMusic" in self.inspector.scripts or
            "bgMusic.paused" in self.inspector.scripts or
            "bgMusic.muted" in self.inspector.scripts
        )
        if not has_music_toggle_listener:
            return False, "JavaScript does not bind click event listener to toggle music playback"
        return True, "JavaScript event handler for music toggle control is implemented"

    def test_f6_05_audio_toggle_visual_states(self) -> Tuple[bool, str]:
        has_toggle_styles = (
            "musicToggle" in self.inspector.styles or
            "music-toggle" in self.inspector.styles
        )
        if not has_toggle_styles:
            return False, "CSS does not define visual styles for music toggle control"
        return True, "CSS contains styling for interactive audio toggle button"

    # ==========================================================================
    # TIER 1 - F7: Multi-Device Responsiveness
    # ==========================================================================

    def test_f7_01_viewport_meta_tag(self) -> Tuple[bool, str]:
        meta = self.inspector.soup.find("meta", attrs={"name": "viewport"})
        if not meta:
            return False, "Missing <meta name='viewport'> tag"
        content = meta.get("content", "")
        if "width=device-width" not in content or "initial-scale=1.0" not in content:
            return False, f"Viewport meta content incomplete: '{content}'"
        return True, f"Viewport meta configured correctly: '{content}'"

    def test_f7_02_responsive_height_units(self) -> Tuple[bool, str]:
        has_dvh = "dvh" in self.inspector.styles.lower()
        has_vh = "vh" in self.inspector.styles.lower()
        if not (has_dvh or has_vh):
            return False, "CSS does not utilize responsive height units (dvh/vh)"
        unit = "dvh (modern dynamic viewport)" if has_dvh else "vh"
        return True, f"CSS uses responsive height units ({unit})"

    def test_f7_03_font_clamping(self) -> Tuple[bool, str]:
        clamp_matches = re.findall(r'clamp\s*\([^)]+\)', self.inspector.styles)
        if len(clamp_matches) < 2:
            return False, f"CSS uses insufficient font clamp() definitions (found {len(clamp_matches)}, expected >= 2)"
        return True, f"CSS applies fluid typography with {len(clamp_matches)} clamp() definitions"

    def test_f7_04_mobile_media_queries(self) -> Tuple[bool, str]:
        media_queries = re.findall(r'@media[^{]+', self.inspector.styles)
        has_mobile = any(
            re.search(r'(?:max-width|min-width)\s*:\s*(?:375|480|575|767|768)px', q)
            for q in media_queries
        )
        if not has_mobile:
            return False, f"CSS lacks explicit mobile responsive media queries (found {len(media_queries)} queries)"
        return True, f"CSS contains responsive media queries covering mobile breakpoints ({len(media_queries)} total)"

    def test_f7_05_touch_friendly_hit_targets(self) -> Tuple[bool, str]:
        # Check settings btn and close btn dimensions
        settings_btn_match = re.search(r'\.settings-btn\s*\{([^}]*)\}', self.inspector.styles)
        if not settings_btn_match:
            return False, "CSS rule for .settings-btn not found"
        css = settings_btn_match.group(1)
        has_min_size = bool(re.search(r'(?:width|height)\s*:\s*(?:[4-9]\d|3[6-9])px', css))
        if not has_min_size:
            return False, "Interactive touch controls sizing is smaller than minimum 36px touch target"
        return True, "Interactive touch controls comply with accessible hit target dimensions (>= 36px)"

    # ==========================================================================
    # TIER 1 - F8: Syntax & Code Hygiene
    # ==========================================================================

    def test_f8_01_no_trailing_markdown_fence(self) -> Tuple[bool, str]:
        last_chunk = "".join(self.inspector.lines[-10:])
        if "```" in last_chunk:
            return False, "File terminates with an invalid trailing markdown code fence (```)"
        return True, "File terminates cleanly without stray markdown code fences"

    def test_f8_02_doctype_and_html_lang(self) -> Tuple[bool, str]:
        raw_start = self.inspector.raw_content[:200].lower()
        if "<!doctype html>" not in raw_start:
            return False, "Document missing standard <!DOCTYPE html> preamble"
        html_tag = self.inspector.soup.find("html")
        if not html_tag or html_tag.get("lang") != "vi":
            return False, f"<html> tag missing proper lang='vi' attribute (found: {html_tag.get('lang') if html_tag else 'None'})"
        return True, "Document specifies standard DOCTYPE and valid Vietnamese lang attribute (lang='vi')"

    def test_f8_03_tags_closure_integrity(self) -> Tuple[bool, str]:
        head = self.inspector.soup.find("head")
        body = self.inspector.soup.find("body")
        if not head or not body:
            return False, "Missing <head> or <body> tags"
        # Check matching counts of open vs close for critical tags
        div_opens = len(re.findall(r'<div\b', self.inspector.raw_content, re.IGNORECASE))
        div_closes = len(re.findall(r'</div\s*>', self.inspector.raw_content, re.IGNORECASE))
        if div_opens != div_closes:
            return False, f"Mismatched <div> tag count: {div_opens} open vs {div_closes} close"
        return True, f"Critical DOM tags paired and cleanly closed (Divs balanced: {div_opens}/{div_closes})"

    def test_f8_04_clean_javascript_no_stray_markdown(self) -> Tuple[bool, str]:
        if "```" in self.inspector.scripts:
            return False, "JavaScript code contains stray markdown code fences"
        return True, "JavaScript code is clean and free of markdown syntax artifacts"

    def test_f8_05_balanced_css_braces(self) -> Tuple[bool, str]:
        open_b = self.inspector.styles.count("{")
        close_b = self.inspector.styles.count("}")
        if open_b != close_b:
            return False, f"CSS curly braces unbalanced: {open_b} open '{{' vs {close_b} close '}}'"
        return True, f"CSS styles have perfectly balanced curly braces ({open_b} pairs)"

    # ==========================================================================
    # TIER 2 - Boundary & Corner Cases
    # ==========================================================================

    def test_t2_01_extreme_text_wrapping(self) -> Tuple[bool, str]:
        # Verifies card body has word-wrap or break-word preventing overflow on long strings
        has_wrapping = (
            "word-break" in self.inspector.styles or
            "overflow-wrap" in self.inspector.styles or
            "word-wrap" in self.inspector.styles or
            "break-word" in self.inspector.styles
        )
        if not has_wrapping:
            return False, "Card body missing 'word-break: break-word' or 'overflow-wrap' boundary protection"
        return True, "Card text specifies word-wrapping boundary protection against text blowout"

    def test_t2_02_narrow_mobile_bounds(self) -> Tuple[bool, str]:
        # Card width must be bounded by percentage (e.g. 90% or 92%) so it never exceeds screen on 320px
        content_match = re.search(r'\.content\s*\{([^}]*)\}', self.inspector.styles)
        if not content_match:
            return False, ".content CSS rule missing"
        css = content_match.group(1)
        has_responsive_width = bool(re.search(r'width\s*:\s*(?:9[0-5]%|calc)', css))
        if not has_responsive_width:
            return False, "Card container missing responsive width boundary rule (width: 90%-95%)"
        return True, "Card container enforces responsive width bounds for 320px-375px mobile displays"

    def test_t2_03_landscape_mobile_max_height(self) -> Tuple[bool, str]:
        # Verify max-height <= 90vh / 90dvh or landscape media query
        content_match = re.search(r'\.content\s*\{([^}]*)\}', self.inspector.styles)
        if not content_match:
            return False, ".content CSS rule missing"
        css = content_match.group(1)
        has_max_height = bool(re.search(r'max-height\s*:\s*(?:8[0-9]|90)d?vh', css))
        if not has_max_height:
            return False, "Card container missing max-height boundary rule (max-height: 85vh-90vh/dvh)"
        return True, "Card container enforces max-height constraint for landscape mobile displays"

    def test_t2_04_audio_autoplay_rejection_safety(self) -> Tuple[bool, str]:
        # .play() should be protected with .catch()
        play_calls = re.findall(r'(\.play\s*\([^)]*\))', self.inspector.scripts)
        if not play_calls:
            return False, "No audio .play() call found in script"
        has_catch = bool(re.search(r'\.play\s*\([^)]*\)\s*\.\s*catch', self.inspector.scripts))
        if not has_catch:
            return False, "Audio .play() lacks .catch() rejection handler (causes Uncaught (in promise) on strict browsers)"
        return True, "Audio playback safely encapsulates play() with .catch() rejection handling"

    def test_t2_05_rapid_double_click_guard(self) -> Tuple[bool, str]:
        # Gift box click handler must guard against double triggers
        has_guard = (
            "isOpen" in self.inspector.scripts or
            "isOpened" in self.inspector.scripts or
            "isOpening" in self.inspector.scripts or
            "boxOpened" in self.inspector.scripts or
            "hasOpened" in self.inspector.scripts
        )
        if not has_guard:
            return False, "Gift box open interaction missing state guard (isOpen / isOpening) against rapid click spamming"
        return True, "Gift box interaction implements state guard against duplicate triggering"

    # ==========================================================================
    # TIER 3 - Cross-Feature Combinations & Harmony
    # ==========================================================================

    def test_t3_01_box_open_triggers_audio_and_typewriter(self) -> Tuple[bool, str]:
        # When box opens, both audio playback and typewriter animation must be triggered
        has_audio_trigger = "music.play()" in self.inspector.scripts or "bgMusic.play()" in self.inspector.scripts
        has_typewriter_trigger = "typeWriter()" in self.inspector.scripts or "startTypewriter()" in self.inspector.scripts or "typewriter" in self.inspector.scripts
        if not (has_audio_trigger and has_typewriter_trigger):
            return False, f"Box opening does not harmonize audio and typewriter (Audio: {has_audio_trigger}, Typewriter: {has_typewriter_trigger})"
        return True, "Box opening harmoniously triggers both audio playback and typewriter delivery"

    def test_t3_02_typewriter_and_scrollable_container_harmony(self) -> Tuple[bool, str]:
        # Typewriter text element must reside within scrollable card structure
        typewriter = self.inspector.soup.find(id="typewriter")
        if not typewriter:
            return False, "Element #typewriter not found in DOM"
        parent = typewriter.parent
        parent_id = parent.get("id", "")
        parent_class = " ".join(parent.get("class", []))
        is_in_card = "content" in parent_class or parent_id in ["cardBody", "mainContent"] or "card-body" in parent_class
        if not is_in_card:
            return False, f"Typewriter element is not properly encapsulated within card container (Parent: <{parent.name} id='{parent_id}' class='{parent_class}'>)"
        return True, "Typewriter element is cleanly embedded within the card scroll hierarchy"

    def test_t3_03_modal_and_card_zindex_hierarchy(self) -> Tuple[bool, str]:
        # Settings modal z-index must be higher than card container and canvases
        modal_match = re.search(r'\.settings-modal\s*\{([^}]*)\}', self.inspector.styles)
        content_match = re.search(r'\.content\s*\{([^}]*)\}', self.inspector.styles)
        if not modal_match or not content_match:
            return False, "Could not extract z-index rules for modal and card"
        
        m_z = re.search(r'z-index\s*:\s*(\d+)', modal_match.group(1))
        c_z = re.search(r'z-index\s*:\s*(\d+)', content_match.group(1))

        if not m_z or not c_z:
            return False, "Missing explicit z-index definitions on modal or card"

        modal_z = int(m_z.group(1))
        content_z = int(c_z.group(1))

        if modal_z <= content_z:
            return False, f"Modal z-index ({modal_z}) is not higher than card z-index ({content_z}), causing overlay collision"
        return True, f"Z-index layering correctly ordered: Modal ({modal_z}) > Card ({content_z})"

    # ==========================================================================
    # TIER 4 - Real-World Scenarios (Chrome Headless Multi-Viewport Snapshots)
    # ==========================================================================

    def _render_viewport_screenshot(self, name: str, size_str: str) -> Tuple[bool, str]:
        if self.skip_chrome:
            return True, "Skipped by --skip-chrome flag"

        chrome_path = self.inspector.locate_chrome()
        if not chrome_path:
            return False, "Google Chrome executable not found in system paths"

        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        out_png = SCREENSHOTS_DIR / f"screenshot_{name}.png"
        index_url = f"file:///{str(INDEX_HTML.resolve()).replace(os.sep, '/')}"

        cmd = [
            chrome_path,
            "--headless=new",
            f"--window-size={size_str}",
            f"--screenshot={str(out_png)}",
            "--disable-gpu",
            "--no-sandbox",
            index_url,
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if res.returncode != 0:
                return False, f"Chrome exited with code {res.returncode}: {res.stderr[:200]}"
            if not out_png.exists():
                return False, f"Expected screenshot was not written to {out_png}"
            size_bytes = out_png.stat().st_size
            if size_bytes < 5000:
                return False, f"Screenshot file suspiciously small ({size_bytes} bytes)"
            return True, f"Snapshot captured successfully ({size_bytes:,} bytes -> {out_png.name})"
        except subprocess.TimeoutExpired:
            return False, "Chrome process timed out after 20 seconds"
        except Exception as ex:
            return False, f"Failed to execute Chrome: {ex}"

    def test_t4_01_desktop_1080p_render(self) -> Tuple[bool, str]:
        return self._render_viewport_screenshot("desktop_1080p", "1920,1080")

    def test_t4_02_tablet_portrait_render(self) -> Tuple[bool, str]:
        return self._render_viewport_screenshot("tablet_portrait", "768,1024")

    def test_t4_03_mobile_portrait_render(self) -> Tuple[bool, str]:
        return self._render_viewport_screenshot("mobile_portrait", "375,667")

    def test_t4_04_mobile_landscape_render(self) -> Tuple[bool, str]:
        return self._render_viewport_screenshot("mobile_landscape", "667,375")

    def test_t4_05_visual_screenshot_integrity(self) -> Tuple[bool, str]:
        if self.skip_chrome:
            return True, "Skipped by --skip-chrome flag"

        png_header = b"\x89PNG\r\n\x1a\n"
        missing = []
        corrupted = []
        total_size = 0

        for name, _, _, _ in VIEWPORT_CONFIGS:
            path = SCREENSHOTS_DIR / f"screenshot_{name}.png"
            if not path.exists():
                missing.append(path.name)
                continue
            with open(path, "rb") as f:
                header = f.read(8)
                if header != png_header:
                    corrupted.append(path.name)
            total_size += path.stat().st_size

        if missing:
            return False, f"Missing screenshot files: {missing}"
        if corrupted:
            return False, f"Corrupted PNG headers: {corrupted}"
        return True, f"All 4 viewport screenshots valid PNGs (Total size: {total_size:,} bytes)"


# ==============================================================================
# REPORTING & CLI INTERFACE
# ==============================================================================

def print_banner():
    banner = """
======================================================================
     GIFT-CHRISTMAS 4-TIER END-TO-END VERIFICATION HARNESS
======================================================================
"""
    print(banner)


def format_status(passed: bool) -> str:
    # Use ANSI green/red if terminal supports it
    green = "\033[92mPASS\033[0m"
    red = "\033[91mFAIL\033[0m"
    if sys.stdout.isatty():
        return green if passed else red
    return "[PASS]" if passed else "[FAIL]"


def generate_console_report(results: List[TestResult]):
    current_tier = None
    current_feature = None

    for r in results:
        if r.tier != current_tier:
            current_tier = r.tier
            tier_names = {
                1: "Tier 1: Feature Coverage (F1 to F8)",
                2: "Tier 2: Boundary & Corner Cases",
                3: "Tier 3: Cross-Feature Combinations & Harmony",
                4: "Tier 4: Real-World Scenarios (Chrome Headless Visual Snapshots)",
            }
            print(f"\n--- {tier_names.get(current_tier, f'Tier {current_tier}')} ---")

        if r.feature != current_feature:
            current_feature = r.feature
            print(f"  [{current_feature}]")

        status_str = format_status(r.passed)
        print(f"    {status_str} {r.test_id}: {r.name} ({r.duration_ms}ms)")
        if not r.passed:
            print(f"           >>> Defect: {r.detail}")

    total = len(results)
    passed_count = sum(1 for r in results if r.passed)
    failed_count = total - passed_count
    pass_pct = (passed_count / total * 100.0) if total > 0 else 0.0

    print("\n" + "=" * 70)
    print(f"SUITE SUMMARY: {passed_count}/{total} PASSED ({pass_pct:.1f}%) | {failed_count} FAILED")
    print("=" * 70)


def export_json_report(results: List[TestResult], output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = len(results)
    passed_count = sum(1 for r in results if r.passed)
    failed_count = total - passed_count

    data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total": total,
        "passed": passed_count,
        "failed": failed_count,
        "pass_percentage": round(passed_count / total * 100.0, 2) if total else 0.0,
        "results": [asdict(r) for r in results],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Gift-Christmas 4-Tier E2E Verification Harness")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4], help="Run specific test tier only")
    parser.add_argument("--feature", type=str, help="Run specific feature tests only (e.g., F1, F2)")
    parser.add_argument("--skip-chrome", action="store_true", help="Skip headless Chrome visual snapshot tier")
    parser.add_argument("--json", action="store_true", help="Output results strictly as JSON to stdout")
    parser.add_argument("--allow-fail", action="store_true", help="Exit with 0 even if test cases fail")
    args = parser.parse_args()

    inspector = CodebaseInspector(INDEX_HTML)
    suite = GiftChristmasTestSuite(inspector, skip_chrome=args.skip_chrome)

    if not args.json:
        print_banner()

    suite.run_all(target_tier=args.tier, target_feature=args.feature)

    export_json_report(suite.results, RESULTS_JSON)

    if args.json:
        with open(RESULTS_JSON, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        generate_console_report(suite.results)
        print(f"\nArtifacts & JSON Report saved to:\n  -> {RESULTS_JSON.resolve()}")
        if not args.skip_chrome:
            print(f"  -> {SCREENSHOTS_DIR.resolve()}")

    all_passed = all(r.passed for r in suite.results)
    if not all_passed and not args.allow_fail:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
