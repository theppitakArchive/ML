import uiautomator2 as u2
import subprocess
import time
import random

d = u2.connect()

DESCRIPTION = "#สินค้าดี #โปรโมชั่น ราคาพิเศษ สั่งได้เลยค่ะ"
PRODUCT_LINKS = "https://s.shopee.co.th/6fefvtvzUA\nhttps://s.shopee.co.th/9pbhhkgeWr"
VIDEO_DIR_LOCAL  = r"C:\platform-tools\videos"
VIDEO_DIR_REMOTE = "/sdcard/DCIM/Camera"
TOTAL_VIDEOS = 90

SONGS = [
    "Wira Dance", "Happy", "Sparky Parker", "Down To Business",
    "You Cool!", "Tiny Toy Inventions", "Young Love", "Moon Carrot Rust", "Summer Love",
    "Nature's Way", "Tropical Chill House", "Get To Work",
    "Cello Shots", "Mustache Love", "Cool Whip", "Slowly Turning",
    "Cool Kids", "We Can Only Move So Fast", "Chitown Chill",
    "Feeling Nostalgic (Prelude In A Major - Chopin)",
]

def adb(cmd):
    subprocess.run(cmd, shell=True)

def push_video(n):
    local  = f"{VIDEO_DIR_LOCAL}\\{n}.mp4"
    remote = f"{VIDEO_DIR_REMOTE}/{n}.mp4"
    print(f"[push] {n}.mp4 ...")
    adb(f'adb push "{local}" "{remote}"')
    adb(f'adb shell touch "{remote}"')
    adb(f'adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{remote}')
    time.sleep(4)

for n in range(1, TOTAL_VIDEOS + 1):
    print(f"\n{'='*40}")
    print(f"รอบที่ {n} / {TOTAL_VIDEOS}")
    print(f"{'='*40}")

    # Step 1 — push วิดีโอ N เข้ามือถือ
    push_video(n)

    # Step 2 — กดปุ่ม + เพิ่มวิดีโอ
    d(description="click top right create icon").click()
    print("[2] กดปุ่มเพิ่มวิดีโอแล้ว")
    time.sleep(3)

    # Step 3 — เปิดคลังภาพ
    d(resourceId="com.shopee.th:id/ll_gallery_entrance").click()
    print("[3] เปิดคลังภาพแล้ว")
    time.sleep(4)

    # Step 4 — กด tab วิดีโอ แล้วเลือกวิดีโอตัวแรก (ล่าสุด = ที่เพิ่ง push)
    d(description="วิดีโอ").click()
    time.sleep(2)
    d(resourceId="com.shopee.th:id/ll_check").click()
    print("[4] เลือกวิดีโอแล้ว")
    time.sleep(2)

    # Step 5 — กดถัดไป
    d(resourceId="com.shopee.th:id/tv_pick_top_next").click()
    print("[5] กดถัดไปแล้ว")
    time.sleep(5)

    # Step 6 — กดเพิ่มเพลง
    d(resourceId="com.shopee.th:id/ll_music").click()
    print("[6] กดเพิ่มเพลงแล้ว")
    time.sleep(4)

    # Step 7 — กดแท็บ 'ล่าสุด'
    d(description="ล่าสุด").click()
    print("[7] กดล่าสุดแล้ว")
    time.sleep(3)

    # Step 8 — สุ่มเพลง + scroll หา + กด
    picked = random.choice(SONGS)
    print(f"[8] สุ่มได้: {picked}")
    d(scrollable=True).scroll.to(text=picked)
    time.sleep(1)
    d(text=picked).click()
    print(f"[8] กดเพลง '{picked}' แล้ว")
    time.sleep(3)

    # Step 9 — แตะพื้นที่ว่างเพื่อปิดหน้าเลือกเพลง
    d.click(360, 400)
    print("[9] ปิดหน้าเลือกเพลงแล้ว")
    time.sleep(2)

    # Step 10 — กดถัดไป (compress)
    d(resourceId="com.shopee.th:id/tv_compress").click()
    print("[10] กดถัดไปแล้ว")
    time.sleep(5)

    # Step 11 — ใส่ caption
    d(resourceId="com.shopee.th.dfpluginshopee16:id/et_caption").click()
    time.sleep(1)
    d(focused=True).set_text(DESCRIPTION)
    print("[11] ใส่ caption แล้ว")
    time.sleep(1)

    # Step 12 — แตะนอกช่องพิมพ์ก่อน แล้วกด toggle ไม่ใช้ซ้ำ
    d.click(100, 600)
    time.sleep(1)
    d.click(650, 636)
    print("[12] toggle ไม่อนุญาตใช้ซ้ำแล้ว")
    time.sleep(2)

    # Step 13 — กดเพิ่มสินค้า
    d(resourceId="com.shopee.th.dfpluginshopee16:id/ll_add_product_symbol").click()
    print("[13] กดเพิ่มสินค้าแล้ว")
    time.sleep(3)

    # Step 14 — เปิดหน้ากรอกลิงก์ (tap icon ขวาบน)
    d.click(665, 112)
    print("[14] เปิดหน้ากรอกลิงก์แล้ว")
    time.sleep(2)

    # Step 15 — ใส่ลิงก์สินค้า 2 ลิงก์ (คั่นด้วย newline)
    d(className="android.widget.EditText").click()
    time.sleep(1)
    d(focused=True).set_text(PRODUCT_LINKS)
    print("[15] ใส่ลิงก์สินค้าแล้ว")
    time.sleep(1)

    # Step 16 — ปิด keyboard แล้วกดนำเข้า
    d.press("back")
    time.sleep(1)
    d(text="นำเข้า").click()
    print("[16] กดนำเข้าแล้ว")
    time.sleep(3)

    # Step 17 — เลือกทั้งหมด
    d(text="เลือกทั้งหมด").click()
    print("[17] เลือกทั้งหมดแล้ว")
    time.sleep(1)

    # Step 18 — กดเพิ่ม (ใช้พิกัดเพราะ text="เพิ่ม(2)" ไม่ตรง)
    d.click(469, 1423)
    print("[18] กดเพิ่มแล้ว")
    time.sleep(3)

    # Step 19 — กดโพสต์
    d(resourceId="com.shopee.th.dfpluginshopee16:id/btn_post").click()
    print(f"[19] กดโพสต์แล้ว — รอบที่ {n}/{TOTAL_VIDEOS} เสร็จ!")
    time.sleep(10)

print("\n" + "="*40)
print(f"เสร็จครบ {TOTAL_VIDEOS} วิดีโอแล้ว!")
print("="*40)
