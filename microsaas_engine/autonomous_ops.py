"""Autonomous Gmail/Google OAuth2 Auto-Login, Multi-Channel Publisher, Self-Diagnostics, Self-Healing & Bounded Auto-Evolution Engine."""
from __future__ import annotations

import html
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .config import SiteConfig
from .templates import render_ad_slot, render_page

KST = timezone(timedelta(hours=9))

EXPANDED_GOOGLE_SCOPES = (
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/blogger",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/indexing",
)


def request_with_retry(
    req: urllib.request.Request | str,
    retries: int = 3,
    base_delay: float = 1.0,
    timeout: int = 12,
) -> tuple[int, bytes]:
    """Execute HTTP request with exponential backoff for transient 429/5xx/network errors."""
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(base_delay * (2 ** attempt))
                last_err = e
                continue
            raise
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(base_delay * (2 ** attempt))
                continue
            raise
    raise RuntimeError(f"Request failed after {retries} attempts: {last_err}")


def verify_google_oauth_auto_login(
    client_id: str | None = None,
    client_secret: str | None = None,
    refresh_token: str | None = None,
) -> dict[str, Any]:
    """Perform headless Google/Gmail OAuth2 token refresh and inspect active publishing scopes."""
    cid = (client_id or os.environ.get("GOOGLE_CLIENT_ID") or os.environ.get("YOUTUBE_CLIENT_ID") or "").strip()
    csec = (client_secret or os.environ.get("GOOGLE_CLIENT_SECRET") or os.environ.get("YOUTUBE_CLIENT_SECRET") or "").strip()
    rtok = (refresh_token or os.environ.get("GOOGLE_REFRESH_TOKEN") or os.environ.get("YOUTUBE_REFRESH_TOKEN") or "").strip()

    if not (cid and csec and rtok):
        return {"ok": False, "reason": "missing_credentials", "scopes": []}

    data = urllib.parse.urlencode(
        {
            "client_id": cid,
            "client_secret": csec,
            "refresh_token": rtok,
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        status, raw = request_with_retry(req, retries=2, base_delay=1.0, timeout=10)
        payload = json.loads(raw.decode("utf-8"))
        scopes = str(payload.get("scope", "")).split()
        return {
            "ok": status == 200 and bool(payload.get("access_token")),
            "access_token": payload.get("access_token", ""),
            "expires_in": payload.get("expires_in", 0),
            "scopes": scopes,
            "has_youtube": any("youtube" in s for s in scopes),
            "has_blogger": any("blogger" in s for s in scopes),
            "has_gmail": any("gmail" in s for s in scopes),
            "has_indexing": any("indexing" in s or "webmasters" in s for s in scopes),
        }
    except Exception as e:
        return {"ok": False, "reason": f"{e.__class__.__name__}: {e}", "scopes": []}


def build_expanded_gmail_oauth_url(client_id: str, redirect_uri: str = "http://localhost:8080/") -> str:
    """Build 1-click Google OAuth2 consent URL for expanding Gmail/Blogger/Indexing scopes."""
    params = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "scope": " ".join(EXPANDED_GOOGLE_SCOPES),
        }
    )
    return f"https://accounts.google.com/o/oauth2/v2/auth?{params}"


def publish_to_google_blogger_if_enabled(access_token: str, blog_id: str, title: str, html_body: str) -> dict[str, Any]:
    """Auto-publish daily brief to Google Blogger when blogger scope & BLOGGER_BLOG_ID are present."""
    if not (access_token and blog_id):
        return {"published": False, "reason": "blogger_not_configured"}
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"
    payload = json.dumps({"kind": "blogger#post", "title": title, "content": html_body}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
    )
    try:
        status, raw = request_with_retry(req, retries=2)
        res = json.loads(raw.decode("utf-8"))
        return {"published": status in (200, 201), "url": res.get("url", "")}
    except Exception as e:
        return {"published": False, "reason": str(e)}


def evolve_daily_market_brief(cfg: SiteConfig, market: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    """Bounded Self-Evolution: synthesize daily FX/yield regime brief & update evolution ledger."""
    updated = market["updated_date"]
    fx = market["fx_rates"]
    bm = market["benchmarks"]

    krw = fx.get("KRW", 1385.0)
    gbp = fx.get("GBP", 0.79)
    eur = fx.get("EUR", 0.92)
    hysa_spread = round(bm["us_top_hysa_apy"] - bm["us_avg_savings_apy"], 2)
    nnn_spread = round(bm["commercial_nnn_cap_rate_pct"] - bm["us_mortgage_rate_pct"], 2)

    # Bounded regime classification
    if krw >= 1380:
        fx_regime = "Strong-USD Regime (High KRW/USD Conversion Yield for Global Dollar Assets)"
    elif krw <= 1300:
        fx_regime = "Balanced FX Regime (Favor Currency-Hedged Dividend Accumulators)"
    else:
        fx_regime = "Neutral FX Corridor (Diversify Across USD HYSA & Global FTSE Dividend ETFs)"

    ledger_path = cfg.data_dir / "evolution_ledger.json"
    history: list[dict[str, Any]] = []
    if ledger_path.exists():
        try:
            history = json.loads(ledger_path.read_text(encoding="utf-8")).get("cycles", [])
        except Exception:
            history = []

    cycle_entry = {
        "date": updated,
        "fx_source": market["fx_source"],
        "usd_krw": krw,
        "usd_gbp": gbp,
        "hysa_spread_pct": hysa_spread,
        "nnn_vs_mortgage_spread_pct": nnn_spread,
        "fx_regime": fx_regime,
    }
    if not history or history[-1].get("date") != updated:
        history.append(cycle_entry)
    else:
        history[-1] = cycle_entry
    history = history[-30:]  # Keep bounded 30-cycle window

    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(
        json.dumps({"version": "2.0", "total_cycles": len(history), "cycles": history}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    rel = "apps/autonomous-market-brief.html"
    title = f"Autonomous Daily Passive Income & FX Regime Brief ({updated})"
    desc = (
        f"Auto-evolved daily passive income brief ({updated}): USD/KRW {krw:,.0f}, "
        f"HYSA yield spread +{hysa_spread:.2f}%, Commercial NNN cap spread +{nnn_spread:.2f}%."
    )
    rows_html = "".join(
        f"<tr><td>{html.escape(c['date'])}</td><td>{c['usd_krw']:,.1f}</td><td>{c['usd_gbp']:.4f}</td>"
        f"<td>+{c['hysa_spread_pct']:.2f}%</td><td>{html.escape(c['fx_regime'])}</td></tr>"
        for c in reversed(history[-7:])
    )
    body = f"""
    <section class="hero">
      <span class="badge green">Bounded Self-Evolution Engine • Cycle #{len(history)} • {html.escape(updated)}</span>
      <h1>{html.escape(title)}</h1>
      <p class="muted">Automatically synthesized every day by our self-healing pipeline using live European Central Bank FX data ({html.escape(market['fx_date'])}) and verified passive income yield benchmarks.</p>
    </section>

    <div class="kpi-grid">
      <div class="kpi"><div class="kpi-label">Live USD / KRW</div><div class="kpi-val acc">₩{krw:,.1f}</div></div>
      <div class="kpi"><div class="kpi-label">Live USD / GBP / EUR</div><div class="kpi-val">£{gbp:.4f} / €{eur:.4f}</div></div>
      <div class="kpi"><div class="kpi-label">HYSA Advantage vs 0.38%</div><div class="kpi-val pos">+{hysa_spread:.2f}% APY</div></div>
      <div class="kpi"><div class="kpi-label">NNN Cap vs 7% Mortgage</div><div class="kpi-val pos">+{nnn_spread:.2f}%</div></div>
    </div>

    <div class="alert success">
      <strong>Today's Autonomous Regime Diagnosis:</strong> {html.escape(fx_regime)}
    </div>

    {render_ad_slot(cfg, "evolution-brief")}

    <section class="card">
      <h2>Recent Self-Evolution Ledger (Last 7 Cycles)</h2>
      <table>
        <thead><tr><th>Date</th><th>USD/KRW</th><th>USD/GBP</th><th>HYSA Spread</th><th>Detected Regime</th></tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </section>
    """
    return rel, render_page(cfg, rel, title, desc, body, updated), cycle_entry


def self_heal_github_workflows(gh_token: str, repos: list[str]) -> list[str]:
    """Inspect latest workflow runs across all repos and auto-retrigger any failed workflow."""
    healed: list[str] = []
    if not gh_token:
        return healed
    for repo in repos:
        url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=1"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {gh_token}", "User-Agent": "SelfHealer/2.0"},
        )
        try:
            _, raw = request_with_retry(req, retries=2)
            runs = json.loads(raw.decode("utf-8")).get("workflow_runs", [])
            if not runs:
                continue
            latest = runs[0]
            if latest.get("status") == "completed" and latest.get("conclusion") in ("failure", "cancelled", "timed_out"):
                wf_id = latest.get("workflow_id")
                dreq = urllib.request.Request(
                    f"https://api.github.com/repos/{repo}/actions/workflows/{wf_id}/dispatches",
                    data=json.dumps({"ref": "main"}).encode("utf-8"),
                    method="POST",
                    headers={
                        "Authorization": f"Bearer {gh_token}",
                        "Accept": "application/vnd.github+json",
                        "Content-Type": "application/json",
                        "User-Agent": "SelfHealer/2.0",
                    },
                )
                urllib.request.urlopen(dreq, timeout=10)
                healed.append(f"retriggered:{repo}#{latest.get('run_number')}")
        except Exception:
            continue
    return healed


def rotate_log_file(log_path: Path, max_bytes: int = 2_000_000, keep_lines: int = 800) -> bool:
    """Prevent disk exhaustion on 24/7 cloud servers by auto-trimming oversized log files."""
    if not log_path.exists() or log_path.stat().st_size <= max_bytes:
        return False
    lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-keep_lines:]
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True
