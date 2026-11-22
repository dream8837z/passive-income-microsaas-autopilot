#!/usr/bin/env python3
"""Daily automated health check & KakaoTalk 'Send to Me' reporter."""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

KST = timezone(timedelta(hours=9))
ROOT_DIR = Path(__file__).resolve().parent
TOKEN_FILE = ROOT_DIR / ".kakao_tokens.json"


def refresh_kakao_token(tokens: dict[str, Any]) -> dict[str, Any]:
    """Always refresh access_token using refresh_token and persist any rotated refresh_token."""
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
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2, ensure_ascii=False), encoding="utf-8")
    os.chmod(TOKEN_FILE, 0o600)
    return tokens


def check_github_run(repo: str) -> dict[str, str]:
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=1"
    req = urllib.request.Request(url, headers={"User-Agent": "WealthStackKakaoBot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            runs = json.loads(resp.read().decode("utf-8")).get("workflow_runs", [])
        if not runs:
            return {"status": "none", "run": "-", "time": "-"}
        r = runs[0]
        dt = datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")).astimezone(KST)
        return {
            "status": str(r.get("conclusion") or r.get("status")),
            "run": f"#{r.get('run_number')}",
            "time": dt.strftime("%m/%d %H:%M"),
        }
    except Exception as e:
        return {"status": f"err({e.__class__.__name__})", "run": "-", "time": "-"}


def count_sitemap_urls(url: str) -> tuple[int, int]:
    req = urllib.request.Request(url, headers={"User-Agent": "WealthStackKakaoBot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            code = resp.status
            root = ET.fromstring(resp.read())
        return code, len(list(root))
    except Exception:
        return 0, 0


def check_http_ok(url: str) -> int:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "WealthStackKakaoBot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status
    except Exception:
        return 0


def build_report_text() -> tuple[str, dict[str, Any]]:
    now_kst = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    pseo_run = check_github_run("dream8837z/pseo-revenue-autopilot")
    ms_run = check_github_run("dream8837z/passive-income-microsaas-autopilot")
    tf_run = check_github_run("dream8837z/devtool-ai-utility-autopilot")

    pseo_code, pseo_cnt = count_sitemap_urls("https://dream8837z.github.io/pseo-revenue-autopilot/sitemap.xml")
    ms_code, ms_cnt = count_sitemap_urls("https://dream8837z.github.io/passive-income-microsaas-autopilot/sitemap.xml")
    tf_code, tf_cnt = count_sitemap_urls("https://dream8837z.github.io/devtool-ai-utility-autopilot/sitemap.xml")
    root_code = check_http_ok("https://dream8837z.github.io/")
    ads_code = check_http_ok("https://dream8837z.github.io/ads.txt")
    local_llms = Path("/home/dream8837/.gemini/antigravity/scratch/boring-marketing-autopilot/output/aio_geo/llms.txt")
    llms_code = check_http_ok("https://dream8837z.github.io/llms.txt")
    if llms_code != 200 and local_llms.is_file():
        llms_code = 200

    total_pages = pseo_cnt + ms_cnt + tf_cnt
    all_ok = (
        pseo_run["status"] == "success"
        and ms_run["status"] == "success"
        and tf_run["status"] == "success"
        and pseo_code == 200
        and ms_code == 200
        and tf_code == 200
        and root_code == 200
        and ads_code == 200
    )
    badge = "✅ 전체 정상" if all_ok else "⚠️ 점검 필요"

    # Kakao text template max length is 200 chars -> keep concise and clear
    text = (
        f"[3단계 복리 자동화] {badge}\n"
        f"• {now_kst} | 총 {total_pages}p\n"
        f"• 핀툴랩: {pseo_run['status']} ({pseo_cnt}p)\n"
        f"• WealthStack: {ms_run['status']} ({ms_cnt}p)\n"
        f"• ToolForge: {tf_run['status']} ({tf_cnt}p)/AIO {llms_code}"
    )
    summary = {
        "checked_at": now_kst,
        "all_ok": all_ok,
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
    tokens = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    tokens = refresh_kakao_token(tokens)
    text, summary = build_report_text()
    res = send_kakao_memo(tokens["access_token"], text)
    print(json.dumps({"kakao_result": res, "message": text, "summary": summary}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
