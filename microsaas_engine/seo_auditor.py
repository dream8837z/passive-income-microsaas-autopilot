"""Automated SEO, AdSense, link integrity, and content quality auditor."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .config import SiteConfig


def audit_dist(cfg: SiteConfig) -> dict[str, Any]:
    dist = cfg.dist_dir
    html_files = sorted(dist.rglob("*.html"))
    errors: list[str] = []
    warnings: list[str] = []

    if len(html_files) < 100:
        errors.append(f"Expected >= 100 HTML pages, found {len(html_files)}")

    for required in ("sitemap.xml", "robots.txt", "ads.txt", "manifest.json"):
        if not (dist / required).exists():
            errors.append(f"Missing required root file: {required}")

    seen_titles: set[str] = set()
    for f in html_files:
        content = f.read_text(encoding="utf-8")
        rel = f.relative_to(dist).as_posix()

        m_title = re.search(r"<title>(.*?)</title>", content, re.S)
        if not m_title or len(m_title.group(1).strip()) < 10:
            errors.append(f"{rel}: missing or too short <title>")
        else:
            t = m_title.group(1).strip()
            if t in seen_titles:
                errors.append(f"{rel}: duplicate <title>: {t}")
            seen_titles.add(t)

        if 'name="description"' not in content:
            errors.append(f"{rel}: missing meta description")
        if 'rel="canonical"' not in content:
            errors.append(f"{rel}: missing canonical link")
        if cfg.adsense_client_id and cfg.adsense_client_id not in content:
            errors.append(f"{rel}: missing AdSense client id")

        # Check relative internal hrefs resolve inside dist
        for href in re.findall(r'href="([^"]+)"', content):
            if href.startswith(("http://", "https://", "#", "mailto:", "javascript:")):
                continue
            target = (f.parent / href.split("#")[0].split("?")[0]).resolve()
            if not target.exists():
                errors.append(f"{rel}: broken internal link -> {href}")

    status = "PASS" if not errors else "FAIL"
    return {
        "status": status,
        "page_count": len(html_files),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors[:25],
        "warnings": warnings[:25],
    }
