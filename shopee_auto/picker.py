"""
picker.py — ใช้คลิกบนหน้าจอมือถือเพื่อหาพิกัดปุ่ม
วิธีใช้:
  1. เปิดมือถือไปหน้าที่ต้องการหาพิกัด
  2. รัน: python picker.py
  3. คลิกบนปุ่มที่ต้องการ → พิกัดจะแสดงใน terminal
  4. กด 's' เพื่อ save พิกัดทั้งหมดลง coords.py
  5. กด 'q' หรือ ESC เพื่อออก
"""

import subprocess
import cv2
import numpy as np
import json
import os

COORDS_FILE = "coords.json"
clicks = {}  # {"ชื่อปุ่ม": (x, y)}
current_name = ""


def screenshot():
    result = subprocess.run(
        "adb exec-out screencap -p",
        shell=True, capture_output=True
    )
    if not result.stdout:
        print("ERROR: ไม่พบอุปกรณ์ รัน 'adb devices' เพื่อตรวจสอบ")
        exit(1)
    return cv2.imdecode(np.frombuffer(result.stdout, np.uint8), cv2.IMREAD_COLOR)


def redraw(img, clicks):
    display = img.copy()
    for name, (x, y) in clicks.items():
        cv2.circle(display, (x, y), 8, (0, 0, 255), -1)
        cv2.putText(display, name, (x + 10, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return display


def on_click(event, x, y, flags, param):
    global current_name
    if event == cv2.EVENT_LBUTTONDOWN:
        if not current_name:
            print("  กรุณาพิมพ์ชื่อปุ่มใน terminal ก่อนคลิก")
            return

        clicks[current_name] = (x, y)
        print(f"  บันทึก '{current_name}': x={x}, y={y}")
        current_name = ""

        # วาดจุดใหม่
        display = redraw(param["img"], clicks)
        cv2.imshow("Picker — กด S=save, R=refresh, Q=quit", display)


def save_coords():
    # บันทึก JSON
    with open(COORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(clicks, f, indent=2, ensure_ascii=False)

    # สร้าง coords.py พร้อมใช้งาน
    lines = ["COORDS = {\n"]
    for name, (x, y) in clicks.items():
        lines.append(f'    "{name}": ({x}, {y}),\n')
    lines.append("}\n")

    with open("coords.py", "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"\n  บันทึกแล้ว → {COORDS_FILE} และ coords.py")
    print(f"  มีทั้งหมด {len(clicks)} จุด\n")


def load_existing():
    if os.path.exists(COORDS_FILE):
        with open(COORDS_FILE) as f:
            data = json.load(f)
        for k, v in data.items():
            clicks[k] = tuple(v)
        print(f"โหลดพิกัดเดิม {len(clicks)} จุด จาก {COORDS_FILE}\n")


def print_help():
    print("=" * 45)
    print("  PICKER — วิธีใช้")
    print("=" * 45)
    print("  1. พิมพ์ชื่อปุ่ม แล้วกด Enter")
    print("  2. คลิกบนหน้าจอมือถือ")
    print("  กด S  → save พิกัดทั้งหมด")
    print("  กด R  → refresh ภาพหน้าจอใหม่")
    print("  กด D  → ลบจุดสุดท้าย")
    print("  กด Q / ESC → ออก")
    print("=" * 45)
    print("\nชื่อปุ่มแนะนำ:")
    suggested = [
        "upload_button", "select_music", "no_music",
        "next_button", "description_field",
        "product_link_button", "no_duet_toggle",
        "confirm_upload", "latest_file"
    ]
    for s in suggested:
        status = "✓" if s in clicks else " "
        print(f"  [{status}] {s}")
    print()


def main():
    global current_name

    print_help()
    load_existing()

    img = screenshot()
    param = {"img": img}

    win = "Picker — กด S=save, R=refresh, Q=quit"
    cv2.imshow(win, redraw(img, clicks))
    cv2.setMouseCallback(win, on_click, param)

    while True:
        # รับชื่อปุ่มจาก terminal
        name = input("พิมพ์ชื่อปุ่มที่ต้องการมาร์ก (หรือ s=save, r=refresh, d=ลบ, q=ออก): ").strip()

        if name.lower() == "q":
            break
        elif name.lower() == "s":
            save_coords()
            print_help()
        elif name.lower() == "r":
            img = screenshot()
            param["img"] = img
            cv2.imshow(win, redraw(img, clicks))
            print("  refresh แล้ว\n")
        elif name.lower() == "d":
            if clicks:
                removed = list(clicks.keys())[-1]
                del clicks[removed]
                print(f"  ลบ '{removed}' แล้ว\n")
                cv2.imshow(win, redraw(param["img"], clicks))
            else:
                print("  ไม่มีจุดให้ลบ\n")
        elif name:
            current_name = name
            print(f"  ตอนนี้: คลิกบนหน้าจอเพื่อมาร์กปุ่ม '{name}'")

        key = cv2.waitKey(100) & 0xFF
        if key in (ord('q'), 27):
            break

    cv2.destroyAllWindows()
    print("\nปิด picker แล้ว")
    if clicks:
        print(f"พิกัดที่บันทึกไว้ ({len(clicks)} จุด):")
        for name, (x, y) in clicks.items():
            print(f"  {name}: ({x}, {y})")


if __name__ == "__main__":
    main()
