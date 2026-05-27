import queue
import tkinter as tk
from tkinter import messagebox, scrolledtext

from engine import TicketAssistantEngine
from notifier import send_telegram_alert


class TicketAssistantGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Ticket Assistant (Operator Mode)")
        self.root.geometry("860x620")

        self.engine = TicketAssistantEngine()
        self.ui_queue = queue.Queue()

        self._build_ui()
        self._poll_ui_queue()

    def _build_ui(self):
        top = tk.Frame(self.root)
        top.pack(fill=tk.X, padx=12, pady=8)

        tk.Label(top, text="Daftar URL (1 baris = 1 URL):").pack(anchor="w")
        self.urls_text = scrolledtext.ScrolledText(top, height=7)
        self.urls_text.pack(fill=tk.X)
        self.urls_text.insert(
            tk.END,
            "https://fforeverindonesia.com/\nhttps://www.loket.com/event/fforever30may\n",
        )

        cfg = tk.Frame(self.root)
        cfg.pack(fill=tk.X, padx=12, pady=6)

        tk.Label(cfg, text="Interval (detik):").grid(row=0, column=0, sticky="w")
        self.interval_var = tk.StringVar(value="5")
        tk.Entry(cfg, textvariable=self.interval_var, width=8).grid(
            row=0, column=1, padx=6, sticky="w"
        )

        tk.Label(cfg, text="Maks cek:").grid(row=0, column=2, sticky="w")
        self.max_checks_var = tk.StringVar(value="60")
        tk.Entry(cfg, textvariable=self.max_checks_var, width=8).grid(
            row=0, column=3, padx=6, sticky="w"
        )

        self.auto_open_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            cfg,
            text="Auto-open link tiket saat terdeteksi",
            variable=self.auto_open_var,
        ).grid(row=0, column=4, padx=12, sticky="w")

        actions = tk.Frame(self.root)
        actions.pack(fill=tk.X, padx=12, pady=8)

        self.start_btn = tk.Button(actions, text="Start Monitoring", command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=4)

        self.stop_btn = tk.Button(
            actions, text="Stop", command=self.stop, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=4)

        tk.Button(actions, text="Test Telegram", command=self.test_telegram).pack(
            side=tk.LEFT, padx=4
        )

        self.status_var = tk.StringVar(value="Status: idle")
        tk.Label(self.root, textvariable=self.status_var, anchor="w").pack(
            fill=tk.X, padx=12
        )

        tk.Label(self.root, text="Log:").pack(anchor="w", padx=12)
        self.log_text = scrolledtext.ScrolledText(self.root, height=18, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

    def _append_log(self, text: str):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _poll_ui_queue(self):
        while not self.ui_queue.empty():
            action, payload = self.ui_queue.get()
            if action == "log":
                self._append_log(payload)
            elif action == "finish":
                self.status_var.set(f"Status: {payload}")
                self.start_btn.configure(state=tk.NORMAL)
                self.stop_btn.configure(state=tk.DISABLED)
                self._append_log(payload)
            elif action == "detect":
                self._handle_detect(payload)
        self.root.after(150, self._poll_ui_queue)

    def _handle_detect(self, result: dict):
        url = result.get("source_url", "-")
        links = result.get("ticket_links", [])
        buttons = result.get("buy_buttons", [])

        self._append_log(f"[DETECT] Sumber: {url}")
        for idx, link in enumerate(links, start=1):
            self._append_log(f"  link[{idx}] {link.get('platform')}: {link.get('url')}")
        for idx, button in enumerate(buttons, start=1):
            self._append_log(f"  tombol[{idx}] {button.get('text')} ({button.get('tag')})")

        self.status_var.set("Status: temuan terdeteksi")

    def start(self):
        raw_urls = self.urls_text.get("1.0", tk.END).strip().splitlines()
        urls = [u.strip() for u in raw_urls if u.strip()]

        if not urls:
            messagebox.showwarning("Input kurang", "Masukkan minimal 1 URL.")
            return

        try:
            interval = int(self.interval_var.get())
            max_checks = int(self.max_checks_var.get())
            if interval < 1 or max_checks < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Input tidak valid", "Interval dan maks cek harus angka >= 1."
            )
            return

        started = self.engine.start(
            urls=urls,
            interval=interval,
            max_checks=max_checks,
            auto_open=self.auto_open_var.get(),
            on_log=lambda msg: self.ui_queue.put(("log", msg)),
            on_detect=lambda result: self.ui_queue.put(("detect", result)),
            on_finish=lambda summary: self.ui_queue.put(("finish", summary)),
        )

        if not started:
            messagebox.showinfo("Sedang berjalan", "Monitoring masih berjalan.")
            return

        self.status_var.set("Status: monitoring berjalan")
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self._append_log(f"Start monitoring {len(urls)} URL.")

    def stop(self):
        self.engine.stop()
        self.status_var.set("Status: menghentikan...")
        self._append_log("Menghentikan monitoring atas permintaan operator...")

    def test_telegram(self):
        send_telegram_alert("Test notifikasi dari Ticket Assistant berhasil.")
        self._append_log("Mengirim test notifikasi Telegram.")


def run_app():
    root = tk.Tk()
    app = TicketAssistantGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
