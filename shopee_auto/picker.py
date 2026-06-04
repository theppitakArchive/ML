"""
picker.py — คลิกบนหน้าจอมือถือเพื่อหาพิกัดปุ่ม (LIVE MODE)

วิธีใช้:
  1. เปิดมือถือไปหน้าที่ต้องการ
  2. รัน: python picker.py
  3. หน้าจอมือถืออัพเดทเอง
  4. กดเลข 1-9 เลือกปุ่ม -> คลิกบนภาพ
  5. กด S = save, Q = ออก (หรือปิดหน้าต่างได้เลย)
"""

import subprocess
import cv2
import numpy as np
import json
import os
import threading
import time

COORDS_FILE  = "coords.json"
BUTTON_NAMES = [
    "add_video",          # 1 กดเพิ่มวิดีโอ
    "open_gallery",       # 2 เปิดคลังวิดีโอ
    "select_video",       # 3 กดเลือกวิดีโอ
    "confirm_select",     # 4 กดเลือก
    "latest_video",       # 5 เลือกวิดีโอล่าสุด
    "select_music",       # 6 เลือกเพลง
    "tap_exit_music",     # 7 เคาะจอเพื่อออก
    "next_button",        # 8 ถัดไป
    "no_reuse_toggle",    # 9 ไม่อนุญาตใช้ซ้ำ
    "description_field",  # 10 วาง#+รายละเอียด (พิมพ์)
    "select_product",     # 11 แตะเลือกสินค้า
    "paste_link_mode",    # 12 เลือกวางแบบลิงก์
    "link_field",         # 13 วางลิงก์ (พิมพ์)
    "add_product",        # 14 กดเพิ่ม
    "post_button",        # 15 กดโพส
]

clicks       = {}
selected_idx = [0]
latest_frame = [None]
scale_ref    = [1.0]
running      = [True]
frame_lock   = threading.Lock()


def screenshot():
    try:
        result = subprocess.run(
            "adb exec-out screencap -p",
            shell=True, capture_output=True, timeout=10
        )
        if not result.stdout:
            return None
        return cv2.imdecode(np.frombuffer(result.stdout, np.uint8), cv2.IMREAD_COLOR)
    except Exception:
        return None


def capture_loop():
    """thread: ดึงภาพหน้าจอมือถือต่อเนื่อง (ไม่ถี่เกินไป)"""
    while running[0]:
        frame = screenshot()
        if frame is not None:
            with frame_lock:
                latest_frame[0] = frame
        # หน่วงพอให้ Windows ไม่ค้างจากการเปิด process ถี่เกิน
        time.sleep(0.3)


def make_display(img):
    h, w  = img.shape[:2]
    scale = min(700 / h, 400 / w)
    small = cv2.resize(img, (int(w * scale), int(h * scale)))

    # วาดเฉพาะจุดที่อยู่ใน BUTTON_NAMES (กรองชื่อเก่าที่ไม่ใช่)
    for name, (rx, ry) in clicks.items():
        if name not in BUTTON_NAMES:
            continue
        sx, sy = int(rx * scale), int(ry * scale)
        cv2.circle(small, (sx, sy), 8, (0, 0, 255), -1)
        cv2.putText(small, name, (sx + 6, sy - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

    panel_w = 300
    panel   = np.zeros((small.shape[0], panel_w, 3), dtype=np.uint8)
    cv2.putText(panel, "N=next B=back  click=mark", (8, 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    cv2.putText(panel, "D=del current  X=clear all", (8, 36),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
    cv2.putText(panel, "S=save  Q=quit", (8, 54),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
    cv2.line(panel, (0, 61), (panel_w, 61), (80, 80, 80), 1)

    for i, name in enumerate(BUTTON_NAMES):
        y       = 76 + i * 25
        is_sel  = (i == selected_idx[0])
        is_done = name in clicks
        color   = (0, 255, 255) if is_sel else ((0, 255, 0) if is_done else (180, 180, 180))
        prefix  = f"{i+1:2d}" + (" >" if is_sel else "  ") + ("* " if is_done else "  ")
        cv2.putText(panel, prefix + name, (8, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    cv2.putText(panel, f"saved: {len(clicks)}/{len(BUTTON_NAMES)}",
                (8, panel.shape[0] - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 200, 255), 1)

    return np.hstack([panel, small]), scale


def on_click(event, x, y, flags, _):
    panel_w = 300
    if event == cv2.EVENT_LBUTTONDOWN and x > panel_w:
        real_x = int((x - panel_w) / scale_ref[0])
        real_y = int(y / scale_ref[0])
        name   = BUTTON_NAMES[selected_idx[0]]
        clicks[name] = (real_x, real_y)
        print(f"  บันทึก '{name}': x={real_x}, y={real_y}")
        if selected_idx[0] < len(BUTTON_NAMES) - 1:
            selected_idx[0] += 1


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

    t = threading.Thread(target=capture_loop, daemon=True)
    t.start()

    print("กำลังเชื่อมต่อมือถือ...")
    for _ in range(100):
        with frame_lock:
            if latest_frame[0] is not None:
                break
        time.sleep(0.1)
    else:
        print("ERROR: ไม่พบมือถือ รัน 'adb devices' เพื่อตรวจสอบ")
        running[0] = False
        return

    win = "Picker"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_click)

    print("\n=== PICKER (LIVE) ===")
    print("N = ปุ่มถัดไป | B = ย้อนกลับ -> คลิกบนภาพ")
    print("(คลิกแล้วเลื่อนไปปุ่มถัดไปเอง)")
    print("S = save | Q = ออก\n")

    while running[0]:
        with frame_lock:
            frame = None if latest_frame[0] is None else latest_frame[0].copy()

        if frame is not None:
            display, scale_ref[0] = make_display(frame)
            cv2.imshow(win, display)

        key = cv2.waitKey(50) & 0xFF

        # ตรวจว่าผู้ใช้กดปุ่มปิดหน้าต่าง (X) หรือยัง
        try:
            if cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:
                break
        except cv2.error:
            break

        if key in (ord('q'), ord('Q'), 27):
            break
        elif key in (ord('s'), ord('S')):
            save_coords()
        elif key in (ord('n'), ord('N')):
            selected_idx[0] = (selected_idx[0] + 1) % len(BUTTON_NAMES)
            print(f"  เลือก: {BUTTON_NAMES[selected_idx[0]]}")
        elif key in (ord('b'), ord('B')):
            selected_idx[0] = (selected_idx[0] - 1) % len(BUTTON_NAMES)
            print(f"  เลือก: {BUTTON_NAMES[selected_idx[0]]}")
        elif key in (ord('d'), ord('D')):
            # ลบจุดของปุ่มที่เลือกอยู่
            name = BUTTON_NAMES[selected_idx[0]]
            if name in clicks:
                del clicks[name]
                print(f"  ลบ '{name}' แล้ว")
            else:
                print(f"  '{name}' ยังไม่มีจุดให้ลบ")
        elif key in (ord('x'), ord('X')):
            # ล้างทุกจุด รวมถึงชื่อเก่าที่ไม่อยู่ใน BUTTON_NAMES
            clicks.clear()
            print("  ล้างทุกจุดแล้ว")

    # ปิดให้สะอาด แล้วบังคับจบ process กันค้าง
    running[0] = False
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    if clicks:
        save_coords()
    print("ปิด picker แล้ว")
    os._exit(0)   # บังคับจบ กัน thread/subprocess ค้าง


if __name__ == "__main__":
    main()
