import math

def compute_positions(w, h, count=12):
    is_landscape = w > h and h <= 560
    is_mobile = w < 768 and not is_landscape

    # Music & settings boxes
    music_box = {'left': 14, 'top': 14, 'right': 60, 'bottom': 60, 'width': 46, 'height': 46}
    settings_box = {'left': w - 60, 'top': 14, 'right': w - 14, 'bottom': 60, 'width': 46, 'height': 46}

    if is_landscape:
        card_w = min(w * 0.62, 390)
        card_h = min(h * 0.60, 220)
    elif is_mobile:
        card_w = min(w * 0.92, 340) if w <= 375 else min(w * 0.90, 390)
        card_h = min(h * 0.50, 300) if w <= 375 else min(h * 0.52, 320)
    else:
        card_w = min(w * 0.85, 650)
        card_h = min(h * 0.70, 400)

    card_left = (w - card_w) / 2
    card_top = (h - card_h) / 2
    card_box = {
        'left': card_left,
        'top': card_top,
        'right': card_left + card_w,
        'bottom': card_top + card_h,
        'width': card_w,
        'height': card_h
    }

    positions = []
    if is_landscape:
        s = min(42, max(36, int(h * 0.11)))
        # Left wing
        positions.append({'x': 14, 'y': max(music_box['bottom'] + 10, 68), 'size': s, 'rot': -5})
        positions.append({'x': min(card_box['left'] - s - 12, 54), 'y': int(h * 0.50 - s / 2), 'size': s, 'rot': 6})
        positions.append({'x': 14, 'y': min(h - s - 12, int(h * 0.78)), 'size': s, 'rot': -4})
        # Right wing
        positions.append({'x': w - s - 14, 'y': max(settings_box['bottom'] + 10, 68), 'size': s, 'rot': 5})
        positions.append({'x': max(card_box['right'] + 12, w - s - 54), 'y': int(h * 0.50 - s / 2), 'size': s, 'rot': -6})
        positions.append({'x': w - s - 14, 'y': min(h - s - 12, int(h * 0.78)), 'size': s, 'rot': 4})
        # Top shelf
        positions.append({'x': int(w * 0.35 - s / 2), 'y': max(10, int(card_box['top'] - s - 10)), 'size': s, 'rot': 3})
        positions.append({'x': int(w * 0.50 - s / 2), 'y': max(8, int(card_box['top'] - s - 12)), 'size': s, 'rot': -2})
        positions.append({'x': int(w * 0.65 - s / 2), 'y': max(10, int(card_box['top'] - s - 10)), 'size': s, 'rot': -3})
        # Bottom shelf
        positions.append({'x': int(w * 0.35 - s / 2), 'y': min(h - s - 10, int(card_box['bottom'] + 10)), 'size': s, 'rot': -4})
        positions.append({'x': int(w * 0.50 - s / 2), 'y': min(h - s - 8, int(card_box['bottom'] + 12)), 'size': s, 'rot': 3})
        positions.append({'x': int(w * 0.65 - s / 2), 'y': min(h - s - 10, int(card_box['bottom'] + 10)), 'size': s, 'rot': 4})
    elif is_mobile:
        s = 42 if w <= 375 else 46
        top_row_y = max(music_box['bottom'] + 12, 68)
        top_center_y = max(12, int(music_box['top'] + 2))
        mid_upper_y = max(top_row_y + s + 6, min(int(card_box['top'] - s - 10), top_row_y + s + 12))
        # Top Zone (5 slots)
        positions.append({'x': 14, 'y': top_row_y, 'size': s, 'rot': -6})
        positions.append({'x': w - s - 14, 'y': top_row_y, 'size': s, 'rot': 6})
        positions.append({'x': int(w / 2 - s / 2), 'y': top_center_y, 'size': s, 'rot': 2})
        positions.append({'x': int(w * 0.28 - s / 2), 'y': mid_upper_y, 'size': s - 2, 'rot': -3})
        positions.append({'x': int(w * 0.72 - s / 2), 'y': mid_upper_y, 'size': s - 2, 'rot': 3})

        # Bottom Zone (7 slots)
        bot_y1 = int(card_box['bottom'] + 12)
        bot_y2 = min(h - s - 12, bot_y1 + s + 14)
        positions.append({'x': 16, 'y': bot_y1, 'size': s, 'rot': 5})
        positions.append({'x': int(w * 0.38 - s / 2), 'y': bot_y1 + 6, 'size': s, 'rot': -4})
        positions.append({'x': int(w * 0.62 - s / 2), 'y': bot_y1 + 6, 'size': s, 'rot': 4})
        positions.append({'x': w - s - 16, 'y': bot_y1, 'size': s, 'rot': -5})
        positions.append({'x': int(w * 0.20 - s / 2), 'y': bot_y2, 'size': s - 2, 'rot': 3})
        positions.append({'x': int(w * 0.50 - s / 2), 'y': bot_y2 - 2, 'size': s - 2, 'rot': -3})
        positions.append({'x': int(w * 0.80 - s / 2), 'y': bot_y2, 'size': s - 2, 'rot': 4})
    
    return positions, card_box, music_box, settings_box

viewports = [
    (360, 640),
    (375, 667),
    (390, 844),
    (412, 915),
    (430, 932),
    (667, 375),
    (844, 390)
]

for w, h in viewports:
    positions, card_box, music_box, settings_box = compute_positions(w, h, 12)
    print(f"\n=== Viewport {w}x{h} ===")
    print(f"CardBox: [{card_box['left']:.1f}, {card_box['top']:.1f}, {card_box['right']:.1f}, {card_box['bottom']:.1f}]")
    card_overlaps = 0
    music_overlaps = 0
    settings_overlaps = 0
    pairwise_overlaps = 0
    out_of_bounds = 0
    
    for i, p1 in enumerate(positions):
        s1 = p1['size']
        b1 = {'left': p1['x'], 'top': p1['y'], 'right': p1['x'] + s1, 'bottom': p1['y'] + s1}
        # Check out of bounds
        if b1['left'] < 0 or b1['top'] < 0 or b1['right'] > w or b1['bottom'] > h:
            print(f"  [OOB] Pos {i}: {b1}")
            out_of_bounds += 1
        # Check card overlap
        if not (b1['right'] <= card_box['left'] or b1['left'] >= card_box['right'] or
                b1['bottom'] <= card_box['top'] or b1['top'] >= card_box['bottom']):
            print(f"  [CARD OVERLAP] Pos {i}: {b1} vs Card {card_box}")
            card_overlaps += 1
        # Check music overlap
        if not (b1['right'] <= music_box['left'] or b1['left'] >= music_box['right'] or
                b1['bottom'] <= music_box['top'] or b1['top'] >= music_box['bottom']):
            print(f"  [MUSIC OVERLAP] Pos {i}: {b1}")
            music_overlaps += 1
        # Check settings overlap
        if not (b1['right'] <= settings_box['left'] or b1['left'] >= settings_box['right'] or
                b1['bottom'] <= settings_box['top'] or b1['top'] >= settings_box['bottom']):
            print(f"  [SETTINGS OVERLAP] Pos {i}: {b1}")
            settings_overlaps += 1
        # Check pairwise
        for j in range(i + 1, len(positions)):
            p2 = positions[j]
            s2 = p2['size']
            b2 = {'left': p2['x'], 'top': p2['y'], 'right': p2['x'] + s2, 'bottom': p2['y'] + s2}
            if not (b1['right'] <= b2['left'] or b1['left'] >= b2['right'] or
                    b1['bottom'] <= b2['top'] or b1['top'] >= b2['bottom']):
                print(f"  [PAIRWISE OVERLAP] Pos {i} and Pos {j}: {b1} vs {b2}")
                pairwise_overlaps += 1
                
    print(f"Results: Card={card_overlaps}, Music={music_overlaps}, Settings={settings_overlaps}, Pairwise={pairwise_overlaps}, OOB={out_of_bounds}")
    assert card_overlaps == 0
    assert music_overlaps == 0
    assert settings_overlaps == 0
    assert pairwise_overlaps == 0
    assert out_of_bounds == 0
print("\n>>> ALL VIEWPORT GEOMETRIES ARE 100% COLLISION FREE! <<<")
