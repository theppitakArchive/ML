"""
dump_ui.py — ดึงรายการ element ทั้งหมดในหน้าจอตอนนี้
ใช้สำรวจว่ามีปุ่ม/ข้อความอะไรบ้าง เพื่อหาวิธีกด

วิธีใช้:
  1. เปิดมือถือไปหน้าที่ต้องการสำรวจ
  2. รัน: python dump_ui.py
  3. ดูรายการที่ออกมา → เลือกว่าจะใช้ text อะไรกดปุ่ม
"""

import uiautomator2 as u2

d = u2.connect()

print("=" * 70)
print("รายการ element ในหน้าจอตอนนี้")
print("=" * 70)

# วน element ทั้งหมดที่คลิกได้หรือมีข้อความ
xml = d.dump_hierarchy()

# ใช้ xml parser หา element ที่น่าสนใจ
import xml.etree.ElementTree as ET

root = ET.fromstring(xml)

found = []
for node in root.iter("node"):
    text       = node.get("text", "")
    desc       = node.get("content-desc", "")
    rid        = node.get("resource-id", "")
    clickable  = node.get("clickable", "false")
    cls        = node.get("class", "")
    bounds     = node.get("bounds", "")

    # เลือกเฉพาะที่กดได้หรือมีข้อความ
    if clickable == "true" or text or desc:
        found.append({
            "text":      text,
            "desc":      desc,
            "id":        rid.split("/")[-1] if rid else "",
            "class":     cls.split(".")[-1],
            "clickable": clickable,
            "bounds":    bounds,
        })

# แสดงผล
for i, f in enumerate(found):
    flags = []
    if f["text"]:
        flags.append(f'text="{f["text"]}"')
    if f["desc"]:
        flags.append(f'desc="{f["desc"]}"')
    if f["id"]:
        flags.append(f'id="{f["id"]}"')
    if f["clickable"] == "true":
        flags.append("[CLICKABLE]")

    if flags:
        print(f"{i+1:3d}. {f['class']:20s} " + "  ".join(flags))

print("\n" + "=" * 70)
print(f"เจอ {len(found)} element")
print("=" * 70)

# save เป็นไฟล์ด้วย
with open("ui_dump.txt", "w", encoding="utf-8") as f:
    for item in found:
        f.write(str(item) + "\n")
print("\n  บันทึกรายละเอียดเต็มไว้ที่ ui_dump.txt")
