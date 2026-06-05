import uiautomator2 as u2
import time
import random

d = u2.connect()

DESCRIPTION = "#สินค้าดี #โปรโมชั่น ราคาพิเศษ สั่งได้เลยค่ะ"
PRODUCT_LINKS = "https://s.shopee.co.th/6fefvtvzUA\nhttps://s.shopee.co.th/9pbhhkgeWr"

SONGS = [
    "Wira Dance", "Happy", "Sparky Parker", "Down To Business",
    "You Cool!", "Tiny Toy Inventions", "Young Love", "Moon Carrot Rust", "Summer Love",
    "Nature's Way", "Tropical Chill House", "Get To Work",
    "Cello Shots", "Mustache Love", "Cool Whip", "Slowly Turning",
    "Cool Kids", "We Can Only Move So Fast", "Chitown Chill",
    "Feeling Nostalgic (Prelude In A Major - Chopin)",
]

# Step 2 — กดปุ่ม + เพิ่มวิดีโอ
d(description="click top right create icon").click()
time.sleep(3)

# Step 3 — เปิดคลังภาพ
d(resourceId="com.shopee.th:id/ll_gallery_entrance").click()
time.sleep(4)

# Step 4 — กด tab วิดีโอ แล้วเลือกวิดีโอตัวแรก
d(description="วิดีโอ").click()
time.sleep(2)
d(resourceId="com.shopee.th:id/ll_check").click()
time.sleep(2)

# Step 5 — กดถัดไป
d(resourceId="com.shopee.th:id/tv_pick_top_next").click()
time.sleep(5)

# Step 6 — กดเพิ่มเพลง
d(resourceId="com.shopee.th:id/ll_music").click()
time.sleep(4)

# Step 7 — กดแท็บ 'ล่าสุด'
d(description="ล่าสุด").click()
time.sleep(3)

# Step 8 — สุ่มเพลง + scroll หา + กด
picked = random.choice(SONGS)
d(scrollable=True).scroll.to(text=picked)
time.sleep(1)
d(text=picked).click()
time.sleep(3)

# Step 9 — แตะพื้นที่ว่างเพื่อปิดหน้าเลือกเพลง
d.click(360, 400)
time.sleep(2)

# Step 10 — กดถัดไป (compress)
d(resourceId="com.shopee.th:id/tv_compress").click()
time.sleep(5)

# Step 11 — ใส่ caption
d(resourceId="com.shopee.th.dfpluginshopee16:id/et_caption").click()
time.sleep(1)
d(focused=True).set_text(DESCRIPTION)
time.sleep(1)

# Step 12 — แตะนอกช่องพิมพ์ก่อน แล้วกด toggle ไม่ใช้ซ้ำ
d.click(100, 600)
time.sleep(1)
d.click(650, 636)
time.sleep(2)

# Step 13 — กดเพิ่มสินค้า
d(resourceId="com.shopee.th.dfpluginshopee16:id/ll_add_product_symbol").click()
time.sleep(3)

# Step 14 — เปิดหน้ากรอกลิงก์ (tap icon ขวาบน)
d.click(665, 112)
time.sleep(2)

# Step 15 — ใส่ลิงก์สินค้า 2 ลิงก์ (คั่นด้วย newline)
d(className="android.widget.EditText").click()
time.sleep(1)
d(focused=True).set_text(PRODUCT_LINKS)
time.sleep(1)

# Step 16 — ปิด keyboard แล้วกดเพิ่ม
d.press("back")
time.sleep(1)
d(text="เพิ่ม").click()
print("[16] กดเพิ่มแล้ว")
time.sleep(3)

print("หยุดที่ step 16 — dump หน้าจอแล้วแจ้งไปต่อ")

# Step 17 — กดโพสต์ (ยังไม่รัน — รอยืนยัน)
# d(resourceId="com.shopee.th.dfpluginshopee16:id/btn_post").click()
# time.sleep(5)
