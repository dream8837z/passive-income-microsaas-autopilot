#!/usr/bin/env python3
"""Autonomous Self-Diagnostic, Self-Healing, Gmail OAuth2 Check & KakaoTalk 18:00 KST Reporter."""
from __future__ import annotations

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

KST = timezone(timedelta(hours=9))
ROOT_DIR = Path(__file__).resolve().parent
TOKEN_FILE = ROOT_DIR / ".kakao_tokens.json"
GOOGLE_FILE = ROOT_DIR / ".google_oauth.json"
LOG_FILE = ROOT_DIR / "kakao_daily.log"

REPOS = [
    "dream8837z/pseo-revenue-autopilot",
    "dream8837z/passive-income-microsaas-autopilot",
    "dream8837z/devtool-ai-utility-autopilot",
]


def rotate_log_if_needed() -> None:
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > 2_000_000:
        lines = LOG_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()[-600:]
        LOG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_or_refresh_tokens() -> dict[str, Any]:
    """Load Kakao tokens from env vars or local .kakao_tokens.json and auto-refresh."""
    env_key = os.environ.get("KAKAO_REST_API_KEY", "").strip()
    env_sec = os.environ.get("KAKAO_CLIENT_SECRET", "").strip()
    env_ref = os.environ.get("KAKAO_REFRESH_TOKEN", "").strip()
    if env_key and env_ref:
        tokens: dict[str, Any] = {
            "rest_api_key": env_key,
            "client_secret": env_sec,
            "refresh_token": env_ref,
        }
    else:
        tokens = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))

    data = urllib.parse.urlencode(
        {
            "grant_type": "refresh_token",
            "client_id": tokens["rest_api_key"],
            "client_secret": tokens["client_secret"],
            "refresh_token": tokens["refresh_token"],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://kauth.kakao.com/oauth/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode("utf-8"))

    tokens["access_token"] = res["access_token"]
    if res.get("refresh_token"):
        tokens["refresh_token"] = res["refresh_token"]
    if TOKEN_FILE.exists() or not env_key:
        TOKEN_FILE.write_text(json.dumps(tokens, indent=2, ensure_ascii=False), encoding="utf-8")
        os.chmod(TOKEN_FILE, 0o600)
    return tokens


def check_google_oauth_health() -> dict[str, Any]:
    """Verify headless Gmail/Google OAuth2 auto-login token refresh."""
    cid = os.environ.get("GOOGLE_CLIENT_ID") or os.environ.get("YOUTUBE_CLIENT_ID") or ""
    csec = os.environ.get("GOOGLE_CLIENT_SECRET") or os.environ.get("YOUTUBE_CLIENT_SECRET") or ""
    rtok = os.environ.get("GOOGLE_REFRESH_TOKEN") or os.environ.get("YOUTUBE_REFRESH_TOKEN") or ""
    if not (cid and csec and rtok) and GOOGLE_FILE.exists():
        g = json.loads(GOOGLE_FILE.read_text(encoding="utf-8"))
        cid = g.get("client_id", "")
        csec = g.get("client_secret", "")
        rtok = g.get("refresh_token", "")
    if not (cid and csec and rtok):
        return {"ok": False, "status": "unconfigured"}

    data = urllib.parse.urlencode(
        {"client_id": cid, "client_secret": csec, "refresh_token": rtok, "grant_type": "refresh_token"}
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return {"ok": bool(payload.get("access_token")), "status": "OK", "scope": payload.get("scope", "")}
    except Exception as e:
        return {"ok": False, "status": f"ERR({e.__class__.__name__})"}


def check_and_heal_github_run(repo: str, gh_token: str = "") -> dict[str, str]:
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=1"
    headers = {"User-Agent": "WealthStackSelfHealer/2.0"}
    if gh_token:
        headers["Authorization"] = f"Bearer {gh_token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            runs = json.loads(resp.read().decode("utf-8")).get("workflow_runs", [])
        if not runs:
            return {"status": "none", "run": "-", "time": "-", "healed": "no"}
        r = runs[0]
        dt = datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")).astimezone(KST)
        st = str(r.get("conclusion") or r.get("status"))
        healed = "no"
        if st in ("failure", "cancelled", "timed_out") and gh_token:
            wf_id = r.get("workflow_id")
            dreq = urllib.request.Request(
                f"https://api.github.com/repos/{repo}/actions/workflows/{wf_id}/dispatches",
                data=json.dumps({"ref": "main"}).encode("utf-8"),
                method="POST",
                headers={
                    "Authorization": f"Bearer {gh_token}",
                    "Accept": "application/vnd.github+json",
                    "Content-Type": "application/json",
                    "User-Agent": "WealthStackSelfHealer/2.0",
                },
            )
            try:
                urllib.request.urlopen(dreq, timeout=10)
                healed = "retriggered"
                st = "healed"
            except Exception:
                pass
        return {"status": st, "run": f"#{r.get('run_number')}", "time": dt.strftime("%m/%d %H:%M"), "healed": healed}
    except Exception as e:
        return {"status": f"err({e.__class__.__name__})", "run": "-", "time": "-", "healed": "no"}


def count_sitemap_urls(url: str) -> tuple[int, int]:
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "WealthStackSelfHealer/2.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                code = resp.status
                root = ET.fromstring(resp.read())
            return code, len(list(root))
        except Exception:
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    return 0, 0


def check_http_ok(url: str) -> int:
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "WealthStackSelfHealer/2.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status
        except Exception:
            if attempt < 2:
                time.sleep(1.0)
    return 0


def build_report_text() -> tuple[str, dict[str, Any]]:
    now_kst = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    gh_token = os.environ.get("GH_PAT", "").strip()
    if not gh_token and (Path.home() / ".git-credentials").exists():
        raw_cred = (Path.home() / ".git-credentials").read_text(errors="ignore")
        if "dream8837z:" in raw_cred:
            gh_token = raw_cred.split("dream8837z:")[1].split("@github.com")[0].strip()

    pseo_run = check_and_heal_github_run("dream8837z/pseo-revenue-autopilot", gh_token)
    ms_run = check_and_heal_github_run("dream8837z/passive-income-microsaas-autopilot", gh_token)
    tf_run = check_and_heal_github_run("dream8837z/devtool-ai-utility-autopilot", gh_token)
    g_auth = check_google_oauth_health()

    pseo_code, pseo_cnt = count_sitemap_urls("https://dream8837z.github.io/pseo-revenue-autopilot/sitemap.xml")
    ms_code, ms_cnt = count_sitemap_urls("https://dream8837z.github.io/passive-income-microsaas-autopilot/sitemap.xml")
    tf_code, tf_cnt = count_sitemap_urls("https://dream8837z.github.io/devtool-ai-utility-autopilot/sitemap.xml")
    root_code = check_http_ok("https://dream8837z.github.io/")
    ads_code = check_http_ok("https://dream8837z.github.io/ads.txt")

    total_pages = pseo_cnt + ms_cnt + tf_cnt
    all_ok = (
        pseo_run["status"] in ("success", "healed")
        and ms_run["status"] in ("success", "healed")
        and tf_run["status"] in ("success", "healed")
        and pseo_code == 200
        and ms_code == 200
        and tf_code == 200
        and root_code == 200
        and ads_code == 200
    )
    badge = "✅ 자가진단 정상" if all_ok else "🔧 자동복구 가동"
    g_badge = "OK" if g_auth["ok"] else g_auth["status"]

    text = (
        f"[자가진단·진화 리포트] {badge}\n"
        f"• {now_kst} | 총 {total_pages}p\n"
        f"• 머니핀랩:{pseo_run['status']}({pseo_cnt}p)\n"
        f"• Wealth:{ms_run['status']}({ms_cnt}p) Tool:{tf_run['status']}({tf_cnt}p)\n"
        f"• Gmail인증:{g_badge} / ads:{ads_code}"
    )
    summary = {
        "checked_at": now_kst,
        "all_ok": all_ok,
        "google_oauth": g_auth,
        "pseo": {"run": pseo_run, "http": pseo_code, "pages": pseo_cnt},
        "wealthstack": {"run": ms_run, "http": ms_code, "pages": ms_cnt},
        "toolforge": {"run": tf_run, "http": tf_code, "pages": tf_cnt},
        "root_http": root_code,
        "ads_txt_http": ads_code,
        "total_pages": total_pages,
    }
    return text, summary


def send_kakao_memo(access_token: str, text: str) -> dict[str, Any]:
    template = {
        "object_type": "text",
        "text": text[:200],
        "link": {
            "web_url": "https://dream8837z.github.io/",
            "mobile_web_url": "https://dream8837z.github.io/",
        },
        "button_title": "통합 수익 포털 열기",
    }
    data = urllib.parse.urlencode(
        {"template_object": json.dumps(template, ensure_ascii=False)}
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        data=data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    import sys
    silent_if_ok = "--silent-if-ok" in sys.argv
    rotate_log_if_needed()
    tokens = load_or_refresh_tokens()
    text, summary = build_report_text()
    any_healed = any(
        summary[k]["run"].get("healed") == "retriggered"
        for k in ("pseo", "wealthstack", "toolforge")
    )
    if silent_if_ok and summary["all_ok"] and not any_healed:
        print(json.dumps({"kakao_result": "skipped_silent_ok", "summary": summary}, indent=2, ensure_ascii=False))
        return
    res = send_kakao_memo(tokens["access_token"], text)
    print(json.dumps({"kakao_result": res, "message": text, "summary": summary}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
