#!/usr/bin/env python3
"""
Discord 웹훅으로 처리 결과를 전송하는 유틸리티
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional
import requests


def send_discord_notification(
    webhook_url: str,
    title: str,
    description: str,
    color: int = 0x5865F2,  # Discord 블루
    fields: Optional[list] = None,
    footer: Optional[str] = None,
) -> bool:
    """
    Discord 웹훅으로 Embed 메시지 전송
    
    Args:
        webhook_url: Discord 웹훅 URL
        title: Embed 제목
        description: Embed 설명
        color: Embed 색상 (16진수)
        fields: 추가 필드 리스트 [{"name": "...", "value": "...", "inline": bool}]
        footer: Footer 텍스트
    
    Returns:
        bool: 전송 성공 여부
    """
    if not webhook_url:
        return False
    
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if fields:
        embed["fields"] = fields
    
    if footer:
        embed["footer"] = {"text": footer}
    
    payload = {"embeds": [embed]}
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[WARN] Discord 웹훅 전송 실패: {e}")
        return False


def notify_post_success(
    webhook_url: str,
    topic: str,
    category: str,
    post_path: str,
    request_source: Optional[str] = None,
) -> bool:
    """포스트 생성 성공 알림"""
    fields = [
        {"name": "카테고리", "value": category, "inline": True},
        {"name": "파일 경로", "value": f"`{post_path}`", "inline": False},
    ]
    
    if request_source:
        fields.insert(0, {"name": "요청 출처", "value": request_source, "inline": True})
    
    return send_discord_notification(
        webhook_url=webhook_url,
        title="✅ 포스트 생성 완료",
        description=f"**{topic}**\n\n블로그 포스트가 성공적으로 생성되었습니다.",
        color=0x00FF00,  # Green
        fields=fields,
        footer="GitHub Actions",
    )


def notify_post_failure(
    webhook_url: str,
    topic: Optional[str],
    error_message: str,
    request_source: Optional[str] = None,
) -> bool:
    """포스트 생성 실패 알림"""
    fields = [
        {"name": "오류 메시지", "value": f"```{error_message[:1000]}```", "inline": False},
    ]
    
    if request_source:
        fields.insert(0, {"name": "요청 출처", "value": request_source, "inline": True})
    
    return send_discord_notification(
        webhook_url=webhook_url,
        title="❌ 포스트 생성 실패",
        description=f"**{topic or '알 수 없음'}**\n\n포스트 생성 중 오류가 발생했습니다.",
        color=0xFF0000,  # Red
        fields=fields,
        footer="GitHub Actions",
    )


def save_processing_result(
    result_dir: str,
    request_id: str,
    status: str,
    topic: str,
    post_path: Optional[str] = None,
    error: Optional[str] = None,
) -> str:
    """
    처리 결과를 JSON 파일로 저장
    
    Returns:
        str: 저장된 파일 경로
    """
    from pathlib import Path
    
    result_path = Path(result_dir)
    result_path.mkdir(parents=True, exist_ok=True)
    
    result_file = result_path / f"result_{request_id}.json"
    
    data = {
        "request_id": request_id,
        "status": status,  # "success" or "failure"
        "topic": topic,
        "post_path": post_path,
        "error": error,
        "processed_at": datetime.utcnow().isoformat() + "Z",
    }
    
    result_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(result_file)

