"""Main pipeline orchestrator: fetch -> build -> sitemap/ads.txt -> audit."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

from .apps_builder import build_all_micro_apps
from .config import SiteConfig, load_config
from .data_fetcher import fetch_live_market_data
from .pseo_pages import (
    build_core_pages,
    build_dividend_pages,
    build_hysa_pages,
    build_pod_pages,
    build_property_pages,
    build_saas_pages,
)
from .seo_auditor import audit_dist


def _write_file(base: Path, rel: str, content: str) -> None:
    target = base / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def run_pipeline(cfg: SiteConfig | None = None) -> dict[str, Any]:
    cfg = cfg or load_config()
    market = fetch_live_market_data(cfg.data_dir, dry_run=cfg.dry_run)

    if cfg.dist_dir.exists():
        shutil.rmtree(cfg.dist_dir)
    cfg.dist_dir.mkdir(parents=True, exist_ok=True)

    all_urls: list[str] = []

    # 1. Build 4 interactive Vibe-Coded Micro-SaaS apps
    for rel, html_doc in build_all_micro_apps(cfg, market):
        _write_file(cfg.dist_dir, rel, html_doc)
        all_urls.append(rel)

    # 2. Build 104 pSEO long-tail pages
    hysa_pages = build_hysa_pages(cfg, market)
    div_pages = build_dividend_pages(cfg, market)
    prop_pages = build_property_pages(cfg, market)
    pod_pages = build_pod_pages(cfg, market)
    saas_pages = build_saas_pages(cfg, market)

    for group in (hysa_pages, div_pages, prop_pages, pod_pages, saas_pages):
        for rel, _, html_doc in group:
            _write_file(cfg.dist_dir, rel, html_doc)
            all_urls.append(rel)

    # 3. Build core & legal pages
    for rel, html_doc in build_core_pages(
        cfg, market, hysa_pages, div_pages, prop_pages, pod_pages, saas_pages
    ):
        _write_file(cfg.dist_dir, rel, html_doc)
        all_urls.append(rel)

    # 4. Write sitemap.xml, robots.txt, ads.txt, manifest.json, .nojekyll
    updated = market["updated_date"]
    url_entries = []
    for rel in sorted(all_urls):
        loc = f"{cfg.site_url}/" if rel == "index.html" else f"{cfg.site_url}/{rel}"
        prio = "1.0" if rel == "index.html" else ("0.9" if rel.startswith("apps/") else "0.75")
        url_entries.append(
            f"  <url><loc>{loc}</loc><lastmod>{updated}</lastmod><priority>{prio}</priority></url>"
        )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(url_entries)
        + "\n</urlset>\n"
    )
    _write_file(cfg.dist_dir, "sitemap.xml", sitemap)
    _write_file(
        cfg.dist_dir,
        "robots.txt",
        f"User-agent: *\nAllow: /\n\nUser-agent: OAI-SearchBot\nAllow: /\n\nUser-agent: PerplexityBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n\nUser-agent: Google-Extended\nAllow: /\n\nSitemap: {cfg.site_url}/sitemap.xml\n",
    )
    _write_file(
        cfg.dist_dir,
        "llms.txt",
        (
            "# WealthStack Studio — Official AI & LLM Discovery Index (llms.txt)\n\n"
            f"> Last Updated: {updated} | Cost: $0 (100% Free Interactive B2B Micro-SaaS & USD Passive Income Suite)\n\n"
            "## Primary Interactive Web Applications\n"
            f"- **Clutch — Driving Instructor & Learner B2B Manager**: {cfg.site_url}/apps/clutch-driving-instructor.html\n"
            f"- **PropYield Pro — Commercial NNN vs Residential Rental Analyzer**: {cfg.site_url}/apps/commercial-nnn-analyzer.html\n"
            f"- **DiviFlow — $100/Week HYSA & Dividend ETF DRIP Planner**: {cfg.site_url}/apps/passive-income-planner.html\n"
            f"- **PD-POD Studio — Copyright-Safe Public Domain POD Margin Engine**: {cfg.site_url}/apps/public-domain-pod-studio.html\n"
        ),
    )
    _write_file(
        cfg.dist_dir,
        "ads.txt",
        f"google.com, {cfg.adsense_pub_id}, DIRECT, f08c47fec0942fa0\n",
    )
    _write_file(
        cfg.dist_dir,
        "manifest.json",
        json.dumps(
            {
                "name": "WealthStack Studio",
                "short_name": "WealthStack",
                "start_url": "./index.html",
                "display": "standalone",
                "background_color": "#0b1120",
                "theme_color": "#0b1120",
            },
            indent=2,
        ),
    )
    _write_file(cfg.dist_dir, ".nojekyll", "")

    # 5. Run automated SEO & integrity audit
    audit = audit_dist(cfg)
    summary = {
        "updated_date": updated,
        "fx_source": market["fx_source"],
        "fx_date": market["fx_date"],
        "audit": audit,
    }
    if audit["status"] != "PASS":
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        sys.exit(1)
    return summary
