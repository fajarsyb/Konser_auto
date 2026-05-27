import asyncio
import threading
import time
import webbrowser
from typing import Callable, List, Optional

from dotenv import load_dotenv

from detector import scan_page
from notifier import send_telegram_alert


class TicketAssistantEngine:
    def __init__(self):
        load_dotenv()
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def start(
        self,
        urls: List[str],
        interval: int,
        max_checks: int,
        auto_open: bool,
        on_log: Optional[Callable[[str], None]] = None,
        on_detect: Optional[Callable[[dict], None]] = None,
        on_finish: Optional[Callable[[str], None]] = None,
    ) -> bool:
        if self._running:
            return False

        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            args=(urls, interval, max_checks, auto_open, on_log, on_detect, on_finish),
            daemon=True,
        )
        self._thread.start()
        return True

    def stop(self):
        self._stop_event.set()

    def _run(
        self,
        urls: List[str],
        interval: int,
        max_checks: int,
        auto_open: bool,
        on_log: Optional[Callable[[str], None]],
        on_detect: Optional[Callable[[dict], None]],
        on_finish: Optional[Callable[[str], None]],
    ):
        try:
            asyncio.run(
                self._run_async(
                    urls, interval, max_checks, auto_open, on_log, on_detect
                )
            )
            if on_finish:
                on_finish("Monitoring selesai.")
        except Exception as exc:
            if on_finish:
                on_finish(f"Monitoring berhenti karena error: {exc}")
        finally:
            self._running = False

    async def _run_async(
        self,
        urls: List[str],
        interval: int,
        max_checks: int,
        auto_open: bool,
        on_log: Optional[Callable[[str], None]],
        on_detect: Optional[Callable[[dict], None]],
    ):
        if on_log:
            on_log(f"Mulai monitor {len(urls)} halaman.")

        tasks = [
            asyncio.create_task(
                self._monitor_single_url(
                    url=url,
                    interval=interval,
                    max_checks=max_checks,
                    auto_open=auto_open,
                    on_log=on_log,
                    on_detect=on_detect,
                )
            )
            for url in urls
        ]

        await asyncio.gather(*tasks)

    async def _monitor_single_url(
        self,
        url: str,
        interval: int,
        max_checks: int,
        auto_open: bool,
        on_log: Optional[Callable[[str], None]],
        on_detect: Optional[Callable[[dict], None]],
    ):
        for attempt in range(1, max_checks + 1):
            if self._stop_event.is_set():
                if on_log:
                    on_log(f"[{url}] Dihentikan operator.")
                return

            if on_log:
                on_log(f"[{url}] Scan {attempt}/{max_checks}...")

            result = await scan_page(url)
            if result.get("status") == "error":
                if on_log:
                    on_log(f"[{url}] Error scan: {result.get('error', 'unknown')}")
            else:
                links = result.get("ticket_links", [])
                buttons = result.get("buy_buttons", [])

                if links or buttons:
                    if on_log:
                        on_log(
                            f"[{url}] Terdeteksi {len(links)} link tiket, {len(buttons)} tombol beli."
                        )

                    if on_detect:
                        on_detect(result)

                    message = (
                        f"[Ticket Assistant]\n"
                        f"Sumber: {url}\n"
                        f"Link tiket: {len(links)}\n"
                        f"Tombol beli: {len(buttons)}\n"
                        f"Waktu: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    send_telegram_alert(message)

                    if auto_open and links:
                        first_link = links[0].get("url")
                        if first_link:
                            webbrowser.open(first_link)
                            if on_log:
                                on_log(f"[{url}] Membuka link: {first_link}")

                    return

            await asyncio.sleep(interval)

        if on_log:
            on_log(f"[{url}] Selesai tanpa temuan hingga batas cek.")
