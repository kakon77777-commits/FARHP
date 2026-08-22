import os
import threading
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format, *_args):
        pass


@contextmanager
def local_site():
    handler = partial(QuietHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def browser_executable():
    candidates = [
        os.environ.get("EMPSL_CHROMIUM_EXECUTABLE"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "/usr/bin/chromium",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


with local_site() as base_url, sync_playwright() as playwright:
    launch_options = {
        "headless": True,
        "args": ["--no-sandbox", "--disable-dev-shm-usage"],
    }
    executable = browser_executable()
    if executable:
        launch_options["executable_path"] = executable

    browser = playwright.chromium.launch(**launch_options)
    page = browser.new_page(
        viewport={"width": 1440, "height": 1050},
        device_scale_factor=1,
        accept_downloads=True,
    )
    errors = []
    page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
    page.on("pageerror", lambda error: errors.append(str(error)))

    page.goto(base_url, wait_until="load", timeout=30_000)
    page.wait_for_function("window.EMPSL_V04_READY===true")

    assert page.title().startswith("Axioglyph｜理符")
    assert page.locator("#status").inner_text().startswith("PASS")
    assert page.locator("#ruleGrid .rule").count() == 30
    assert page.locator("#variantGallery .atom-card").count() == 8
    assert page.locator("#activityStatus").get_attribute("aria-live") == "polite"
    assert page.locator("#soundStatus").inner_text().startswith("可以播放")
    assert page.locator("#soundPhase").inner_text().startswith("PH16-")

    page.click('[data-voice="male"]')
    assert page.locator('[data-voice="male"]').get_attribute("aria-pressed") == "true"
    assert "男聲" in page.locator("#soundVoice").inner_text()

    page.click("#playSound")
    page.wait_for_timeout(120)
    assert "播放" in page.locator("#soundStatus").inner_text()
    page.click("#stopSound")
    assert "停止" in page.locator("#soundStatus").inner_text()

    page.click("#autoSoundDemo")
    page.wait_for_function(
        "document.querySelector('#soundStatus').textContent.includes('自動示範完成')",
        timeout=10_000,
    )

    page.click("#randomSoundDemo")
    page.wait_for_function(
        "document.querySelector('#soundSeed').textContent !== '—'",
        timeout=5_000,
    )
    random_seed = page.locator("#soundSeed").inner_text()
    assert page.locator("#replayRandomSound").is_enabled()
    page.click("#replayRandomSound")
    assert page.locator("#soundSeed").inner_text() == random_seed
    page.click("#stopSound")

    with page.expect_download() as wav_download:
        page.click("#exportSoundWav")
    assert wav_download.value.suggested_filename.startswith("axioglyph_")
    assert wav_download.value.suggested_filename.endswith(".wav")
    assert "WAV" in page.locator("#soundStatus").inner_text()

    page.click("#invalidExample")
    page.wait_for_timeout(200)
    assert page.locator("#status").inner_text().startswith("FAIL")
    assert page.locator("#issues .issue").count() > 0
    assert "已載入錯誤案例" in page.locator("#activityStatus").inner_text()

    page.click("#repair")
    page.wait_for_timeout(200)
    assert page.locator("#status").inner_text().startswith("PASS")
    assert "自動修正完成" in page.locator("#activityStatus").inner_text()

    page.select_option("#onset", "ONSET-G")
    page.select_option("#hu", "HU-CUOKOU")
    page.select_option("#rime", "RIME-AI")
    page.wait_for_timeout(200)
    issue_text = page.locator("#issues").inner_text()
    assert "P-002" in issue_text and "P-003" in issue_text

    page.click("#repair")
    page.wait_for_timeout(200)
    assert page.locator("#status").inner_text().startswith("PASS")

    r90 = page.locator('#variantGallery .atom-card[data-id$="@R90"]')
    r90.click()
    page.wait_for_timeout(200)
    assert page.locator("#seedTransform").input_value() == "R90"
    assert r90.get_attribute("aria-pressed") == "true"
    assert "R90" in page.locator("#activityStatus").inner_text()

    with page.expect_download() as svg_download:
        page.click("#exportSvg")
    assert svg_download.value.suggested_filename == "EMPSL_glyph_v0.4.svg"
    assert "SVG" in page.locator("#activityStatus").inner_text()

    with page.expect_download() as json_download:
        page.click("#exportJson")
    assert json_download.value.suggested_filename == "EMPSL_recipe_v0.4.json"
    assert "JSON" in page.locator("#activityStatus").inner_text()

    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert not errors, errors
    browser.close()

print("PASS browser v0.4 · HTTP · rules=30 · variants=8 · audio demos · downloads=3 · console_errors=0")
