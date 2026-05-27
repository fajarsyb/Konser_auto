import asyncio
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)

# Kata kunci yang umum dipakai untuk tombol/link beli tiket
BUY_KEYWORDS = [
    "beli", "buy", "pesan", "ticket", "tiket",
    "get ticket", "beli tiket", "order", "daftar",
    "register", "book now", "checkout"
]

# Domain platform tiket yang dikenal
TICKET_PLATFORMS = [
    "tiket.com", "loket.com", "eventbrite.com",
    "tokopedia.com", "blibli.com", "go-tix"
]


async def scan_page(url, timeout=15000):
    """
    Memindai halaman publik untuk menemukan:
    1. Link menuju platform tiket (tiket.com, loket.com, dll)
    2. Tombol dengan teks bermakna "beli"

    Mengembalikan dict hasil pemindaian.
    """
    results = {
        "source_url": url,
        "ticket_links": [],
        "buy_buttons": [],
        "status": "unknown"
    }

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            await page.wait_for_timeout(3000)

            # --- 1. Cari semua <a> yang mengarah ke platform tiket ---
            all_links = await page.eval_on_selector_all(
                "a[href]",
                """els => els.map(el => ({
                    href: el.href,
                    text: (el.innerText || '').trim().substring(0, 100)
                }))"""
            )

            for link in all_links:
                href = link.get("href", "").lower()
                for platform in TICKET_PLATFORMS:
                    if platform in href:
                        results["ticket_links"].append({
                            "url": link["href"],
                            "text": link["text"],
                            "platform": platform
                        })

            # --- 2. Cari tombol/link dengan teks bermakna "beli" ---
            clickables = await page.eval_on_selector_all(
                "button, a, [role='button'], input[type='submit']",
                """els => els.map(el => ({
                    tag: el.tagName.toLowerCase(),
                    text: (el.innerText || el.value || '').trim().substring(0, 100),
                    href: el.href || '',
                    visible: el.offsetParent !== null
                }))"""
            )

            for el in clickables:
                text_lower = el.get("text", "").lower()
                for keyword in BUY_KEYWORDS:
                    if keyword in text_lower and el.get("visible", False):
                        results["buy_buttons"].append({
                            "tag": el["tag"],
                            "text": el["text"],
                            "href": el.get("href", "")
                        })
                        break

            results["status"] = "scanned"
            logging.info(
                f"Scan selesai: {len(results['ticket_links'])} link tiket, "
                f"{len(results['buy_buttons'])} tombol beli ditemukan."
            )

        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            logging.error(f"Gagal scan {url}: {e}")

        finally:
            await browser.close()

    return results


async def monitor_event_page(url, on_found_callback=None, interval=5, max_checks=60):
    """
    Memantau halaman event secara berkala.
    Jika link tiket atau tombol beli ditemukan, panggil callback.
    """
    for i in range(max_checks):
        logging.info(f"[Monitor {i+1}/{max_checks}] Scanning {url}...")
        result = await scan_page(url)

        if result["ticket_links"] or result["buy_buttons"]:
            logging.info("Tiket/tombol beli terdeteksi!")
            if on_found_callback:
                on_found_callback(result)
            return result

        await asyncio.sleep(interval)

    logging.info("Monitoring selesai tanpa menemukan tiket.")
    return None
