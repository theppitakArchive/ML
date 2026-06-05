import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import time
import random
import os
import glob

try:
    import uiautomator2 as u2
except ImportError:
    u2 = None

# ============================================================
# CONFIG
# ============================================================
DESCRIPTION = "#สินค้าดี #โปรโมชั่น ราคาพิเศษ สั่งได้เลยค่ะ"
PRODUCT_LINKS = "https://s.shopee.co.th/6fefvtvzUA\nhttps://s.shopee.co.th/9pbhhkgeWr"
VIDEO_DIR_LOCAL  = r"C:\platform-tools\videos"
VIDEO_DIR_REMOTE = "/sdcard/DCIM/Camera"

SONGS = [
    "Wira Dance", "Happy", "Sparky Parker", "Down To Business",
    "You Cool!", "Tiny Toy Inventions", "Young Love", "Moon Carrot Rust", "Summer Love",
    "Nature's Way", "Tropical Chill House", "Get To Work",
    "Cello Shots", "Mustache Love", "Cool Whip", "Slowly Turning",
    "Cool Kids", "We Can Only Move So Fast", "Chitown Chill",
    "Feeling Nostalgic (Prelude In A Major - Chopin)",
]

# ============================================================
# AUTOMATION
# ============================================================
def adb(cmd):
    subprocess.run(cmd, shell=True)

def push_video(filename):
    local  = os.path.join(VIDEO_DIR_LOCAL, filename)
    remote = f"{VIDEO_DIR_REMOTE}/{filename}"
    adb(f'adb push "{local}" "{remote}"')
    adb(f'adb shell touch "{remote}"')
    adb(f'adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{remote}')
    time.sleep(4)

def interruptible_sleep(seconds, pause_event, cancel_event, interval=0.5):
    """Sleep ที่ตรวจ pause/cancel ทุก interval วินาที"""
    elapsed = 0
    while elapsed < seconds:
        if cancel_event.is_set():
            return False
        while pause_event.is_set():
            if cancel_event.is_set():
                return False
            time.sleep(0.2)
        time.sleep(interval)
        elapsed += interval
    return True

def run_upload(queue, status_cb, done_cb, pause_event, cancel_event):
    d = u2.connect()
    total = len(queue)

    for i, filename in enumerate(queue, 1):
        if cancel_event.is_set():
            status_cb(f"ยกเลิกแล้ว — หยุดที่ {i-1}/{total}")
            done_cb(i - 1, cancelled=True)
            return

        # รอถ้า pause
        while pause_event.is_set():
            if cancel_event.is_set():
                status_cb("ยกเลิกแล้ว")
                done_cb(i - 1, cancelled=True)
                return
            time.sleep(0.2)

        status_cb(f"กำลังลง {i}/{total} — {filename}")

        push_video(filename)
        if cancel_event.is_set(): done_cb(i-1, cancelled=True); return

        d(description="click top right create icon").click()
        if not interruptible_sleep(3, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d(resourceId="com.shopee.th:id/ll_gallery_entrance").click()
        if not interruptible_sleep(4, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d(description="วิดีโอ").click()
        if not interruptible_sleep(2, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d(resourceId="com.shopee.th:id/ll_check").click()
        if not interruptible_sleep(2, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d(resourceId="com.shopee.th:id/tv_pick_top_next").click()
        if not interruptible_sleep(5, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d(resourceId="com.shopee.th:id/ll_music").click()
        if not interruptible_sleep(4, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d(description="ล่าสุด").click()
        if not interruptible_sleep(3, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        picked = random.choice(SONGS)
        d(scrollable=True).scroll.to(text=picked)
        if not interruptible_sleep(1, pause_event, cancel_event): done_cb(i-1, cancelled=True); return
        d(text=picked).click()
        if not interruptible_sleep(3, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d.click(360, 400)
        if not interruptible_sleep(2, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d(resourceId="com.shopee.th:id/tv_compress").click()
        if not interruptible_sleep(5, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d(resourceId="com.shopee.th.dfpluginshopee16:id/et_caption").click()
        if not interruptible_sleep(1, pause_event, cancel_event): done_cb(i-1, cancelled=True); return
        d(focused=True).set_text(DESCRIPTION)
        if not interruptible_sleep(1, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d.click(100, 600)
        if not interruptible_sleep(1, pause_event, cancel_event): done_cb(i-1, cancelled=True); return
        d.click(650, 636)
        if not interruptible_sleep(2, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d(resourceId="com.shopee.th.dfpluginshopee16:id/ll_add_product_symbol").click()
        if not interruptible_sleep(3, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d.click(665, 112)
        if not interruptible_sleep(2, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d(className="android.widget.EditText").click()
        if not interruptible_sleep(1, pause_event, cancel_event): done_cb(i-1, cancelled=True); return
        d(focused=True).set_text(PRODUCT_LINKS)
        if not interruptible_sleep(1, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d.press("back")
        if not interruptible_sleep(1, pause_event, cancel_event): done_cb(i-1, cancelled=True); return
        d(text="นำเข้า").click()
        if not interruptible_sleep(3, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d(text="เลือกทั้งหมด").click()
        if not interruptible_sleep(1, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d.click(469, 1423)
        if not interruptible_sleep(3, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        d(resourceId="com.shopee.th.dfpluginshopee16:id/btn_post").click()
        if not interruptible_sleep(10, pause_event, cancel_event): done_cb(i-1, cancelled=True); return

        status_cb(f"เสร็จแล้ว {i}/{total} — {filename} ✓")

    done_cb(total, cancelled=False)

# ============================================================
# UI
# ============================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shopee Video Uploader")
        self.geometry("700x580")
        self.resizable(False, False)
        self.configure(bg="#f5f5f5")

        self._drag_start = None
        self._pause_event = threading.Event()   # set = paused
        self._cancel_event = threading.Event()  # set = cancel

        self._build_ui()
        self._load_videos()

    def _build_ui(self):
        # ---- top frame ----
        top = tk.Frame(self, bg="#f5f5f5")
        top.pack(fill="both", expand=True, padx=12, pady=10)

        # left panel
        lf = tk.LabelFrame(top, text="วิดีโอทั้งหมด", bg="#f5f5f5")
        lf.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.lb_all = tk.Listbox(lf, selectmode="extended", width=24, activestyle="none")
        self.lb_all.pack(side="left", fill="both", expand=True)
        sb_all = ttk.Scrollbar(lf, orient="vertical", command=self.lb_all.yview)
        sb_all.pack(side="right", fill="y")
        self.lb_all.config(yscrollcommand=sb_all.set)
        self.lb_all.bind("<Double-Button-1>", self._add_to_queue)

        # middle buttons
        mid = tk.Frame(top, bg="#f5f5f5")
        mid.pack(side="left", padx=4)
        tk.Button(mid, text="เพิ่ม →", width=8, command=self._add_to_queue).pack(pady=4)
        tk.Button(mid, text="← ลบ",   width=8, command=self._remove_from_queue).pack(pady=4)
        tk.Button(mid, text="ขึ้น ↑",  width=8, command=self._move_up).pack(pady=4)
        tk.Button(mid, text="ลง ↓",   width=8, command=self._move_down).pack(pady=4)
        tk.Button(mid, text="ล้างคิว", width=8, command=self._clear_queue).pack(pady=16)

        # right panel
        rf = tk.LabelFrame(top, text="คิวที่จะลง", bg="#f5f5f5")
        rf.pack(side="left", fill="both", expand=True, padx=(6, 0))

        self.lb_queue = tk.Listbox(rf, selectmode="single", width=24, activestyle="none")
        self.lb_queue.pack(side="left", fill="both", expand=True)
        sb_q = ttk.Scrollbar(rf, orient="vertical", command=self.lb_queue.yview)
        sb_q.pack(side="right", fill="y")
        self.lb_queue.config(yscrollcommand=sb_q.set)
        self.lb_queue.bind("<ButtonPress-1>", self._drag_start_cb)
        self.lb_queue.bind("<B1-Motion>", self._drag_motion_cb)

        # ---- control buttons ----
        ctrl = tk.Frame(self, bg="#f5f5f5")
        ctrl.pack(fill="x", padx=12, pady=(0, 4))

        self.lbl_count = tk.Label(ctrl, text="คิว: 0 วิดีโอ", bg="#f5f5f5", font=("Arial", 10))
        self.lbl_count.pack(side="left", pady=6)

        self.btn_cancel = tk.Button(
            ctrl, text="✕  ยกเลิก", font=("Arial", 10, "bold"),
            bg="#999", fg="white", relief="flat", padx=12, pady=5,
            state="disabled", command=self._cancel
        )
        self.btn_cancel.pack(side="right", padx=(6, 0))

        self.btn_pause = tk.Button(
            ctrl, text="⏸  หยุดชั่วคราว", font=("Arial", 10, "bold"),
            bg="#f0a500", fg="white", relief="flat", padx=12, pady=5,
            state="disabled", command=self._toggle_pause
        )
        self.btn_pause.pack(side="right", padx=(6, 0))

        self.btn_start = tk.Button(
            ctrl, text="▶  Start", font=("Arial", 11, "bold"),
            bg="#ee4d2d", fg="white", relief="flat", padx=16, pady=5,
            command=self._start
        )
        self.btn_start.pack(side="right")

        # ---- progress bar ----
        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x", side="bottom", padx=0)

        # ---- status bar ----
        self.status_var = tk.StringVar(value="พร้อมใช้งาน")
        status_bar = tk.Label(
            self, textvariable=self.status_var,
            bg="#ee4d2d", fg="white", anchor="w",
            font=("Arial", 10), padx=10, pady=5
        )
        status_bar.pack(fill="x", side="bottom")

    def _load_videos(self):
        self.lb_all.delete(0, "end")
        files = sorted(glob.glob(os.path.join(VIDEO_DIR_LOCAL, "*.mp4")))
        for f in files:
            self.lb_all.insert("end", os.path.basename(f))
        if not files:
            self.lb_all.insert("end", "(ไม่พบไฟล์ .mp4)")

    def _add_to_queue(self, event=None):
        for i in self.lb_all.curselection():
            self.lb_queue.insert("end", self.lb_all.get(i))
        self._update_count()

    def _remove_from_queue(self):
        for i in reversed(self.lb_queue.curselection()):
            self.lb_queue.delete(i)
        self._update_count()

    def _move_up(self):
        sel = self.lb_queue.curselection()
        if not sel or sel[0] == 0:
            return
        i = sel[0]; val = self.lb_queue.get(i)
        self.lb_queue.delete(i); self.lb_queue.insert(i - 1, val)
        self.lb_queue.selection_set(i - 1)

    def _move_down(self):
        sel = self.lb_queue.curselection()
        if not sel or sel[0] == self.lb_queue.size() - 1:
            return
        i = sel[0]; val = self.lb_queue.get(i)
        self.lb_queue.delete(i); self.lb_queue.insert(i + 1, val)
        self.lb_queue.selection_set(i + 1)

    def _clear_queue(self):
        self.lb_queue.delete(0, "end")
        self._update_count()

    def _drag_start_cb(self, event):
        self._drag_start = self.lb_queue.nearest(event.y)

    def _drag_motion_cb(self, event):
        if self._drag_start is None:
            return
        i = self.lb_queue.nearest(event.y)
        if i != self._drag_start:
            val = self.lb_queue.get(self._drag_start)
            self.lb_queue.delete(self._drag_start)
            self.lb_queue.insert(i, val)
            self.lb_queue.selection_set(i)
            self._drag_start = i

    def _update_count(self):
        n = self.lb_queue.size()
        self.lbl_count.config(text=f"คิว: {n} วิดีโอ")
        self.progress["maximum"] = n if n else 1
        self.progress["value"] = 0

    def _toggle_pause(self):
        if self._pause_event.is_set():
            self._pause_event.clear()
            self.btn_pause.config(text="⏸  หยุดชั่วคราว", bg="#f0a500")
            self.status_var.set(self.status_var.get().replace(" (หยุดชั่วคราว)", "") + " (ต่อแล้ว)")
        else:
            self._pause_event.set()
            self.btn_pause.config(text="▶  ต่อ", bg="#2ecc71")
            self.status_var.set(self.status_var.get() + " (หยุดชั่วคราว)")

    def _cancel(self):
        if messagebox.askyesno("ยืนยัน", "ยกเลิกการลงวิดีโอใช่ไหม?"):
            self._cancel_event.set()
            self._pause_event.clear()  # unblock thread ถ้ากำลัง pause อยู่
            self.btn_cancel.config(state="disabled")
            self.btn_pause.config(state="disabled")

    def _start(self):
        if u2 is None:
            messagebox.showerror("Error", "ไม่พบ uiautomator2\nรัน: pip install uiautomator2")
            return
        queue = list(self.lb_queue.get(0, "end"))
        if not queue:
            messagebox.showwarning("คิวว่าง", "กรุณาเพิ่มวิดีโอเข้าคิวก่อน")
            return

        self._pause_event.clear()
        self._cancel_event.clear()

        self.btn_start.config(state="disabled")
        self.btn_pause.config(state="normal")
        self.btn_cancel.config(state="normal")
        self.progress["maximum"] = len(queue)
        self.progress["value"] = 0

        def status_cb(msg):
            self.status_var.set(msg)
            try:
                n = int(msg.split()[1].split("/")[0])
                self.progress["value"] = n - 1
            except Exception:
                pass
            self.update_idletasks()

        def done_cb(done, cancelled=False):
            self.progress["value"] = done
            if cancelled:
                self.status_var.set(f"ยกเลิกแล้ว — ลงไปแล้ว {done} วิดีโอ")
            else:
                self.status_var.set(f"เสร็จครบ {done} วิดีโอแล้ว! 🎉")
                messagebox.showinfo("เสร็จแล้ว", f"ลงวิดีโอครบ {done} คลิปแล้ว!")
            self.btn_start.config(state="normal")
            self.btn_pause.config(state="disabled", text="⏸  หยุดชั่วคราว", bg="#f0a500")
            self.btn_cancel.config(state="disabled")

        t = threading.Thread(
            target=run_upload,
            args=(queue, status_cb, done_cb, self._pause_event, self._cancel_event),
            daemon=True
        )
        t.start()


if __name__ == "__main__":
    app = App()
    app.mainloop()
