"""
picker.py — คลิกบนหน้าจอมือถือเพื่อหาพิกัดปุ่ม

วิธีใช้:
  1. เปิดมือถือไปหน้าที่ต้องการ
  2. รัน: python picker.py
  3. กดตัวเลข 1-9 เพื่อเลือกปุ่มที่จะมาร์ก
  4. คลิกบนหน้าจอ
  5. กด S เพื่อ save, R เพื่อ refresh, Q เพื่อออก
"""

import subprocess
import cv2
import numpy as np
import json
import os

COORDS_FILE    = "coords.json"
BUTTON_NAMES   = [
    "upload_button",
    "latest_file",
    "select_music",
    "no_music",
    "next_button",
    "description_field",
    "product_link_button",
    "no_duet_toggle",
    "confirm_upload",
]

clicks       = {}   # {"ชื่อ": (x, y)}
selected_idx = [0]  # ปุ่มที่เลือกอยู่ตอนนี้
img_ref      = [None]
scale_ref    = [1.0]


def screenshot():
    result = subprocess.run("adb exec-out screencap -p",
                            shell=True, capture_output=True)
    if not result.stdout:
        print("ERROR: ไม่พบมือถือ รัน 'adb devices' เพื่อตรวจสอบ")
        exit(1)
    return cv2.imdecode(np.frombuffer(result.stdout, np.uint8), cv2.IMREAD_COLOR)


def make_display(img):
    h, w   = img.shape[:2]
    scale  = min(700 / h, 400 / w)
    small  = cv2.resize(img, (int(w * scale), int(h * scale)))

    # วาดจุดที่มาร์กแล้ว
    for name, (rx, ry) in clicks.items():
        sx, sy = int(rx * scale), int(ry * scale)
        cv2.circle(small, (sx, sy), 8, (0, 0, 255), -1)
        cv2.putText(small, name, (sx + 6, sy - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

    # แถบรายการปุ่มทางซ้าย
    panel_w = 260
    panel   = np.zeros((small.shape[0], panel_w, 3), dtype=np.uint8)
    cv2.putText(panel, "กดเลข -> คลิกบนภาพ", (8, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
    cv2.putText(panel, "S=save  R=refresh  Q=quit", (8, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
    cv2.line(panel, (0, 45), (panel_w, 45), (80, 80, 80), 1)

    for i, name in enumerate(BUTTON_NAMES):
        y       = 65 + i * 28
        is_sel  = (i == selected_idx[0])
        is_done = name in clicks
        color   = (0, 255, 255) if is_sel else ((0, 255, 0) if is_done else (180, 180, 180))
        prefix  = f"[{i+1}]" + (" >" if is_sel else "  ") + (" * " if is_done else "   ")
        cv2.putText(panel, prefix + name, (8, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1)

    done_count = len(clicks)
    cv2.putText(panel, f"บันทึกแล้ว: {done_count}/{len(BUTTON_NAMES)}",
                (8, panel.shape[0] - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 200, 255), 1)

    return np.hstack([panel, small]), scale


def on_click(event, x, y, flags, _):
    panel_w   = 260
    if event == cv2.EVENT_LBUTTONDOWN and x > panel_w:
        real_x = int((x - panel_w) / scale_ref[0])
        real_y = int(y / scale_ref[0])
        name   = BUTTON_NAMES[selected_idx[0]]
        clicks[name] = (real_x, real_y)
        print(f"  บันทึก '{name}': x={real_x}, y={real_y}")

        # เลื่อนไปปุ่มถัดไปอัตโนมัติ
        if selected_idx[0] < len(BUTTON_NAMES) - 1:
            selected_idx[0] += 1

        display, scale_ref[0] = make_display(img_ref[0])
        cv2.imshow("Picker", display)


def save_coords():
    with open(COORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(clicks, f, indent=2, ensure_ascii=False)
    with open("coords.py", "w", encoding="utf-8") as f:
        f.write("COORDS = {\n")
        for name, (x, y) in clicks.items():
            f.write(f'    "{name}": ({x}, {y}),\n')
        f.write("}\n")
    print(f"\n  บันทึกแล้ว {len(clicks)} จุด -> coords.py และ {COORDS_FILE}\n")


def load_existing():
    if os.path.exists(COORDS_FILE):
        with open(COORDS_FILE) as f:
            for k, v in json.load(f).items():
                clicks[k] = tuple(v)
        print(f"โหลดพิกัดเดิม {len(clicks)} จุด")


def main():
    load_existing()

    img_ref[0]    = screenshot()
    display, s    = make_display(img_ref[0])
    scale_ref[0]  = s

    cv2.imshow("Picker", display)
    cv2.setMouseCallback("Picker", on_click)

    print("\n=== PICKER ===")
    print("กดเลข 1-9 เพื่อเลือกปุ่มที่จะมาร์ก")
    print("คลิกบนหน้าจอมือถือเพื่อบันทึกพิกัด")
    print("S = save | R = refresh | Q = ออก\n")

    while True:
        key = cv2.waitKey(30) & 0xFF

        if key in (ord('q'), ord('Q'), 27):
            break
        elif key in (ord('s'), ord('S')):
            save_coords()
        elif key in (ord('r'), ord('R')):
            print("  กำลัง refresh...")
            img_ref[0] = screenshot()
            display, scale_ref[0] = make_display(img_ref[0])
            cv2.imshow("Picker", display)
            print("  refresh แล้ว")
        elif ord('1') <= key <= ord('9'):
            idx = key - ord('1')
            if idx < len(BUTTON_NAMES):
                selected_idx[0] = idx
                print(f"  เลือก: {BUTTON_NAMES[idx]}")
                display, scale_ref[0] = make_display(img_ref[0])
                cv2.imshow("Picker", display)

    cv2.destroyAllWindows()
    if clicks:
        save_coords()
    print("ปิด picker แล้ว")


if __name__ == "__main__":
    main()
