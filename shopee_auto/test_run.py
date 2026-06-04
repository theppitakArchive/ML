"""
test_run.py — ทดสอบ flow 17 ขั้น (ไม่กด post_button)
วางไฟล์ที่ C:\platform-tools\
รัน: python test_run.py
"""

import subprocess
import uiautomator2 as u2
import time

# ============================================================
# CONFIG
# ============================================================
VIDEO_LOCAL  = r"C:\platform-tools\videos\1.mp4"
VIDEO_REMOTE = "/sdcard/DCIM/Camera/1.mp4"
DESCRIPTION  = "#สินค้าดี #โปรโมชั่น ราคาพิเศษ สั่งได้เลยค่ะ"
PRODUCT_LINK = "https://shopee.co.th/product/test"

COORDS = {
    "add_video":          (667, 124),
    "open_gallery":       (576, 1248),
    "select_video":       (363, 224),
    "confirm_select":     (91, 363),
    "next_button_1":      (590, 1328),
    "select_music":       (353, 126),
    "music_tab":          (229, 899),
    "latest_music":       (196, 1019),
    "confirm_music":      (234, 592),
    "tap_exit_music":     (393, 597),
    "next_button_2":      (604, 1450),
    "no_reuse_toggle":    (646, 651),
    "description_field":  (283, 213),
    "select_product":     (613, 536),
    "paste_link_mode":    (672, 98),
    "link_field":         (70, 297),
    "add_product":        (454, 855),
    "post_button":        (402, 1485),
}

# ============================================================
# HELPERS
# ============================================================
def adb(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def tap(name):
    x, y = COORDS[name]
    print(f"  tap {name} ({x}, {y})")
    adb(f"adb shell input tap {x} {y}")
    time.sleep(1.0)

def wait(s, reason=""):
    if reason:
        print(f"  รอ {s}s — {reason}")
    time.sleep(s)

def push_video():
    print("\n[1] Push วิดีโอเข้ามือถือ")
    adb(f'adb push "{VIDEO_LOCAL}" {VIDEO_REMOTE}')
    adb(f"adb shell touch {VIDEO_REMOTE}")
    adb(f"adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{VIDEO_REMOTE}")
    wait(2, "รอ gallery scan")

def fill_text(name, text):
    x, y = COORDS[name]
    d.click(x, y)
    time.sleep(0.5)
    d(focused=True).set_text(text)
    time.sleep(0.5)

# ============================================================
# MAIN FLOW
# ============================================================
def main():
    global d
    print("เชื่อมต่อมือถือ...")
    d = u2.connect()
    print("เชื่อมต่อแล้ว\n")

    # Step 1 — push วิดีโอ
    push_video()

    # Step 2 — กดเพิ่มวิดีโอ
    print("\n[2] กดเพิ่มวิดีโอ")
    tap("add_video")
    wait(1)

    # Step 3 — เปิดคลังวิดีโอ
    print("\n[3] เปิดคลังวิดีโอ")
    tap("open_gallery")
    wait(1.5)

    # Step 4 — เลือกวิดีโอ (บนซ้าย)
    print("\n[4] เลือกวิดีโอ")
    tap("select_video")
    wait(1)

    # Step 5 — กดเลือก
    print("\n[5] กดเลือก")
    tap("confirm_select")
    wait(2)

    # Step 6 — กดถัดไป (ครั้งแรก)
    print("\n[6] กดถัดไป (ครั้งแรก)")
    tap("next_button_1")
    wait(2)

    # Step 7 — กดเลือกเพลง
    print("\n[7] กดเลือกเพลง")
    tap("select_music")
    wait(1.5)

    # Step 8 — กดแท็บเพลง
    print("\n[8] กดแท็บเพลง")
    tap("music_tab")
    wait(1)

    # Step 9 — เลือกเพลงล่าสุด
    print("\n[9] เลือกเพลงล่าสุด")
    tap("latest_music")
    wait(1)

    # Step 10 — confirm เพลง
    print("\n[10] confirm เพลง")
    tap("confirm_music")
    wait(1)

    # Step 11 — เคาะหน้าจอออก
    print("\n[11] เคาะหน้าจอออก")
    tap("tap_exit_music")
    wait(1)

    # Step 12 — กดถัดไป (ครั้งสอง)
    print("\n[12] กดถัดไป (ครั้งสอง)")
    tap("next_button_2")
    wait(2)

    # Step 13 — ปุ่มไม่อนุญาตใช้ซ้ำ
    print("\n[13] ปุ่มไม่อนุญาตใช้ซ้ำ")
    tap("no_reuse_toggle")
    wait(1)

    # Step 14 — ใส่ description
    print("\n[14] ใส่ description")
    fill_text("description_field", DESCRIPTION)

    # Step 15 — แตะเลือกสินค้า
    print("\n[15] แตะเลือกสินค้า")
    tap("select_product")
    wait(1.5)

    # Step 16 — เลือกวางแบบลิงก์
    print("\n[16] เลือกวางแบบลิงก์")
    tap("paste_link_mode")
    wait(1)

    # Step 17 — วางลิงก์สินค้า
    print("\n[17] วางลิงก์สินค้า")
    fill_text("link_field", PRODUCT_LINK)

    # Step 18 — กดเพิ่ม
    print("\n[18] กดเพิ่ม")
    tap("add_product")
    wait(1)

    print("\n" + "="*40)
    print("✓ ครบ 17 ขั้น — หยุดก่อน ไม่กด post")
    print("ตรวจดูหน้าจอมือถือว่าถูกต้องไหม")
    print("="*40)


if __name__ == "__main__":
    main()
