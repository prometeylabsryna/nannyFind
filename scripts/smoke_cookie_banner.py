#!/usr/bin/env python3
"""Smoke: cookie-банер видимий у вьюпорті на кількох висотах екрана.

Потрібно: pip3 install playwright && python3 -m playwright install chromium
Запуск: python3 scripts/smoke_cookie_banner.py [--base http://localhost:8082]
"""

from __future__ import annotations

import argparse
import sys
import time

VIEWPORTS = [
    ("iPhone 15 Pro", 393, 852),
    ("iPhone SE", 375, 667),
    ("Pixel 7", 412, 915),
    ("iPad Mini", 768, 1024),
    ("short mobile", 390, 640),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:8082")
    parser.add_argument("--path", default="/")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("FAIL: встановіть Playwright: pip3 install playwright && python3 -m playwright install chromium")
        return 2

    url = args.base.rstrip("/") + args.path
    failures: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, w, h in VIEWPORTS:
            context = browser.new_context(
                viewport={"width": w, "height": h},
                device_scale_factor=2,
                is_mobile=w < 768,
                has_touch=w < 1024,
                locale="uk-UA",
            )
            page = context.new_page()
            page.add_init_script(
                """() => {
                  try { localStorage.removeItem('pp-cookie-consent'); } catch (e) {}
                  document.cookie = 'pp-cookie-consent=; Path=/; Max-Age=0';
                }"""
            )
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            banner = page.wait_for_selector("#cookie-banner.visible", state="visible", timeout=8000)
            if not banner:
                failures.append(f"{name} ({w}x{h}): банер не з'явився")
                context.close()
                continue

            # Дочекатися кінця transition opacity
            page.wait_for_timeout(450)

            metrics = page.evaluate(
                """() => {
                  const el = document.getElementById('cookie-banner');
                  if (!el) return null;
                  const cs = getComputedStyle(el);
                  const r = el.getBoundingClientRect();
                  const sticky = document.querySelector('.sticky-cta');
                  const stickyCs = sticky ? getComputedStyle(sticky) : null;
                  return {
                    position: cs.position,
                    top: cs.top,
                    bottom: cs.bottom,
                    opacity: cs.opacity,
                    visibility: cs.visibility,
                    rect: { top: r.top, bottom: r.bottom, height: r.height, width: r.width },
                    vh: window.innerHeight,
                    bodyOpen: document.body.classList.contains('cookie-consent-open'),
                    stickyDisplay: stickyCs ? stickyCs.display : null,
                    settingsBtn: !!document.getElementById('cookie-settings-btn'),
                  };
                }"""
            )

            if not metrics:
                failures.append(f"{name} ({w}x{h}): немає #cookie-banner")
                context.close()
                continue

            top = float(metrics["rect"]["top"])
            bottom = float(metrics["rect"]["bottom"])
            height = float(metrics["rect"]["height"])
            vh = float(metrics["vh"])
            computed_top = metrics["top"]

            ok = True
            reasons: list[str] = []

            if metrics["position"] != "fixed":
                ok = False
                reasons.append(f"position={metrics['position']}")
            if metrics["bottom"] not in ("0px", "0"):
                # bottom used value may be "0px"
                if not str(metrics["bottom"]).startswith("0"):
                    ok = False
                    reasons.append(f"bottom={metrics['bottom']}")
            if height < 40:
                ok = False
                reasons.append(f"height={height}")
            if top >= vh - 1:
                ok = False
                reasons.append(f"rect.top={top} >= vh={vh} (поза вьюпортом)")
            if bottom <= 0:
                ok = False
                reasons.append(f"rect.bottom={bottom}")
            if float(metrics["opacity"]) < 0.95:
                ok = False
                reasons.append(f"opacity={metrics['opacity']}")
            if not metrics["bodyOpen"]:
                ok = False
                reasons.append("немає body.cookie-consent-open")
            if w < 768 and metrics["stickyDisplay"] not in (None, "none"):
                ok = False
                reasons.append(f"sticky-cta display={metrics['stickyDisplay']}")

            # Клік «Налаштування» має бути досяжним без scrollIntoView fail
            try:
                btn = page.locator("#cookie-settings-btn")
                btn.click(timeout=3000)
                page.wait_for_selector("#cookie-settings:not(.hidden)", timeout=2000)
            except Exception as exc:  # noqa: BLE001
                ok = False
                reasons.append(f"клік Налаштування: {exc}")

            if ok:
                print(f"OK  {name} ({w}x{h}): top={top:.1f} bottom={bottom:.1f} computedTop={computed_top}")
            else:
                msg = f"FAIL {name} ({w}x{h}): " + "; ".join(reasons)
                print(msg)
                failures.append(msg)

            context.close()

        browser.close()

    if failures:
        print(f"\n{len(failures)}/{len(VIEWPORTS)} viewport(s) failed")
        return 1
    print(f"\nAll {len(VIEWPORTS)} viewports passed")
    return 0


if __name__ == "__main__":
    # невелика пауза якщо сервер щойно стартував
    time.sleep(0)
    sys.exit(main())
