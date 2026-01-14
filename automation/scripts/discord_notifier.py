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
    post_content: Optional[str] = None,
) -> bool:
    """포스트 생성 성공 알림"""
    # 파일명에서 날짜와 제목 추출
    from pathlib import Path
    post_file = Path(post_path)
    post_filename = post_file.name
    
    # 파일명 형식: YYYY-MM-DD-title.md
    # 블로그 URL 생성: https://rldhkstopic.github.io/blog/YYYY/MM/DD/title/
    if post_filename.startswith("20") and len(post_filename) >= 10:
        date_part = post_filename[:10]  # YYYY-MM-DD
        title_part = post_filename[11:-3]  # title (확장자 제외)
        year, month, day = date_part.split("-")
        blog_url = f"https://rldhkstopic.github.io/blog/{year}/{month}/{day}/{title_part}/"
    else:
        blog_url = "https://rldhkstopic.github.io/blog/"
    
    # 포스트 내용 읽기 (없으면 파일에서 읽기)
    if post_content is None:
        try:
            post_content = post_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"[WARN] 포스트 내용 읽기 실패: {e}")
            post_content = ""
    
    # Front Matter 제거 (---로 시작하는 부분)
    if post_content.startswith("---"):
        parts = post_content.split("---", 2)
        if len(parts) >= 3:
            post_content = parts[2].strip()
    
    # 마크다운 코드 블록과 이미지 제거 (간단한 정리)
    import re
    post_content = re.sub(r"```[\s\S]*?```", "[코드 블록]", post_content)
    post_content = re.sub(r"!\[.*?\]\(.*?\)", "[이미지]", post_content)
    
    # 글 내용 요약 (최대 1500자, Discord Embed description 제한 고려)
    content_preview = post_content[:1500] if len(post_content) > 1500 else post_content
    if len(post_content) > 1500:
        content_preview += "\n\n... (전체 내용은 블로그에서 확인하세요)"
    
    fields = [
        {"name": "카테고리", "value": category, "inline": True},
        {"name": "파일명", "value": f"`{post_filename}`", "inline": False},
        {"name": "블로그 링크", "value": f"[글 보기]({blog_url})", "inline": False},
        {"name": "글 내용", "value": content_preview, "inline": False},
    ]
    
    if request_source:
        fields.insert(0, {"name": "요청 출처", "value": request_source, "inline": True})
    
    return send_discord_notification(
        webhook_url=webhook_url,
        title="✅ 포스트 생성 완료",
        description=f"**{topic}**\n\n블로그 포스트가 성공적으로 생성되었습니다.\n\n[블로그에서 확인하기]({blog_url})",
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

