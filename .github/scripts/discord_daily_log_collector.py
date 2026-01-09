#!/usr/bin/env python3
"""
Discord Daily Log Collector

목적:
- 지정한 날짜(KST 기준)의 Discord 채널 메시지를 수집해
  `_daily_logs/YYYY-MM-DD/{message_id}.json` 파일로 저장한다.

필수 환경 변수:
- DISCORD_BOT_TOKEN   : Discord Bot Token
- DISCORD_CHANNEL_ID  : 수집 대상 채널 ID

선택 환경 변수:
- DAILY_LOGS_DIR      : 저장 루트 디렉토리 (기본: "_daily_logs")
- DISCORD_API_BASE    : Discord API 베이스 URL (기본: "https://discord.com/api/v10")

사용:
  python .github/scripts/discord_daily_log_collector.py              # 기본: (KST 기준) 어제
  python .github/scripts/discord_daily_log_collector.py 2026-01-03   # 날짜 지정
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests


def _kst_tz() -> timezone:
    return timezone(timedelta(hours=9))


def _parse_target_date(argv: List[str]) -> str:
    """
    args가 없으면 "KST 기준 어제"를 기본값으로 사용한다.
    """
    if len(argv) > 1:
        return argv[1].strip()

    now_kst = datetime.now(timezone.utc).astimezone(_kst_tz())
    return (now_kst.date() - timedelta(days=1)).strftime("%Y-%m-%d")


def _date_range_kst(target_date: str) -> Tuple[datetime, datetime]:
    tz = _kst_tz()
    start = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=tz)
    end = start + timedelta(days=1)
    return start, end


def _discord_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bot {token}",
        "User-Agent": "rldhkstopic-daily-log-collector/1.0",
    }


def _sleep_on_rate_limit(resp: requests.Response) -> None:
    if resp.status_code != 429:
        return
    try:
        data = resp.json()
        retry_after = float(data.get("retry_after", 1.0))
    except Exception:
        retry_after = 1.0
    time.sleep(max(0.5, retry_after))


def fetch_channel_messages(
    api_base: str,
    token: str,
    channel_id: str,
    *,
    before: Optional[str] = None,
    limit: int = 100,
    timeout_s: int = 20,
) -> List[Dict[str, Any]]:
    url = f"{api_base}/channels/{channel_id}/messages"
    params: Dict[str, Any] = {"limit": min(max(limit, 1), 100)}
    if before:
        params["before"] = before

    resp = requests.get(url, headers=_discord_headers(token), params=params, timeout=timeout_s)
    if resp.status_code == 429:
        _sleep_on_rate_limit(resp)
        resp = requests.get(url, headers=_discord_headers(token), params=params, timeout=timeout_s)

    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list):
        return []
    return data


def _author_string(author: Dict[str, Any]) -> str:
    username = author.get("username") or ""
    # Discord는 신규 계정에서 discriminator가 "0" 또는 누락일 수 있다.
    discriminator = author.get("discriminator")
    if discriminator and discriminator != "0":
        return f"{username}#{discriminator}"
    global_name = author.get("global_name")
    if global_name:
        return f"{global_name} ({username})"
    return username


def _message_to_log(msg: Dict[str, Any], *, channel_id: str) -> Dict[str, Any]:
    ts_utc = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
    ts_kst = ts_utc.astimezone(_kst_tz())

    log: Dict[str, Any] = {
        "id": str(msg.get("id", "")),
        "content": msg.get("content", ""),
        "timestamp": ts_kst.isoformat(),
        "mood": None,
        "tags": [],
        "location": None,
        "author": _author_string(msg.get("author") or {}),
        "message_id": str(msg.get("id", "")),
        "channel_id": str(channel_id),
    }

    attachments = msg.get("attachments") or []
    if isinstance(attachments, list) and attachments:
        urls = []
        for att in attachments:
            url = (att or {}).get("url")
            if url:
                urls.append(url)
        if urls:
            log["attachments"] = urls

    return log


def save_logs(target_date: str, logs: List[Dict[str, Any]], logs_root: str) -> Tuple[int, int]:
    base_dir = Path(logs_root) / target_date
    base_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0

    for log in logs:
        msg_id = (log.get("message_id") or log.get("id") or "").strip()
        if not msg_id:
            skipped += 1
            continue

        path = base_dir / f"{msg_id}.json"
        if path.exists():
            skipped += 1
            continue

        path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
        written += 1

    return written, skipped


def main() -> int:
    token = os.getenv("DISCORD_BOT_TOKEN", "").strip()
    channel_id = os.getenv("DISCORD_CHANNEL_ID", "").strip()
    logs_root = os.getenv("DAILY_LOGS_DIR", "_daily_logs").strip() or "_daily_logs"
    api_base = os.getenv("DISCORD_API_BASE", "https://discord.com/api/v10").strip() or "https://discord.com/api/v10"

    if not token:
        print("[ERROR] DISCORD_BOT_TOKEN is not set")
        return 2
    if not channel_id:
        print("[ERROR] DISCORD_CHANNEL_ID is not set")
        return 2

    target_date = _parse_target_date(sys.argv)
    start_kst, end_kst = _date_range_kst(target_date)
    print(f"[INFO] Target date (KST): {target_date}  range={start_kst.isoformat()}..{end_kst.isoformat()}")

    # Discord API는 최신 메시지부터 반환한다.
    before: Optional[str] = None
    collected: List[Dict[str, Any]] = []
    pages = 0
    stop = False

    while not stop:
        pages += 1
        msgs = fetch_channel_messages(api_base, token, channel_id, before=before, limit=100)
        if not msgs:
            break

        before = str(msgs[-1].get("id")) if msgs[-1].get("id") else before

        for msg in msgs:
            # 시스템 메시지/봇 메시지/빈 메시지 등은 일단 건너뜀(첨부만 있는 경우는 포함)
            author = msg.get("author") or {}
            if author.get("bot") is True:
                continue

            ts_utc = datetime.fromisoformat(str(msg.get("timestamp", "")).replace("Z", "+00:00"))
            ts_kst = ts_utc.astimezone(_kst_tz())

            # 범위 밖 필터
            if ts_kst >= end_kst:
                continue
            if ts_kst < start_kst:
                stop = True
                break

            content = msg.get("content") or ""
            attachments = msg.get("attachments") or []
            if not content and not attachments:
                continue

            collected.append(_message_to_log(msg, channel_id=channel_id))

        # 너무 빠르게 긁지 않도록 완화
        time.sleep(0.2)

        # 아주 큰 채널이면 무한루프 방지
        if pages > 200:
            print("[WARN] Too many pages; stopping to avoid runaway collection.")
            break

    # 시간순(오래된 → 최신)으로 저장되게 정렬
    collected.sort(key=lambda x: x.get("timestamp", ""))

    written, skipped = save_logs(target_date, collected, logs_root)
    print(f"[OK] Collected={len(collected)}  written={written}  skipped(existing/invalid)={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

