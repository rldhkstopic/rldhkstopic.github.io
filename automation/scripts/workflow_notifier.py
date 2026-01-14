#!/usr/bin/env python3
"""
GitHub Actions 워크플로우 상태를 Discord로 알리는 스크립트
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Optional

def send_workflow_notification(
    webhook_url: str,
    workflow_name: str,
    status: str,  # "started", "success", "failure", "cancelled"
    run_url: Optional[str] = None,
    commit_message: Optional[str] = None,
    actor: Optional[str] = None,
    branch: Optional[str] = None,
    duration: Optional[str] = None,
    error_message: Optional[str] = None,
) -> bool:
    """
    워크플로우 상태를 Discord로 전송
    
    Args:
        webhook_url: Discord 웹훅 URL
        workflow_name: 워크플로우 이름
        status: 상태 (started, success, failure, cancelled)
        run_url: 워크플로우 실행 URL
        commit_message: 커밋 메시지
        actor: 실행한 사용자
        branch: 브랜치
        duration: 실행 시간
        error_message: 오류 메시지 (실패 시)
    
    Returns:
        bool: 전송 성공 여부
    """
    if not webhook_url:
        print("[WARN] DISCORD_WEBHOOK_URL이 설정되지 않았습니다.")
        return False
    # Normalize common copy/paste issues (leading/trailing spaces/newlines/quotes)
    webhook_url = webhook_url.strip().strip('"').strip("'").strip()
    # Common misconfiguration: user pastes a numeric ID instead of a webhook URL
    if webhook_url.strip().isdigit():
        print(
            "[WARN] DISCORD_WEBHOOK_URL 형식이 잘못되었습니다. "
            "Discord Webhook URL 전체(https://discord.com/api/webhooks/<id>/<token>)를 설정해야 합니다."
        )
        return False
    # Accept official domains and variants (discordapp.com legacy, ptb/canary)
    if "/api/webhooks/" not in webhook_url:
        print(
            "[WARN] DISCORD_WEBHOOK_URL 형식이 예상과 다릅니다. "
            "Discord Webhook URL 전체를 설정했는지 확인하십시오."
        )
        return False
    
    # 상태에 따른 색상 및 이모지 설정
    status_config = {
        "started": {
            "emoji": "🔄",
            "color": 0x5865F2,  # Discord Blue
            "title": "워크플로우 시작",
        },
        "success": {
            "emoji": "✅",
            "color": 0x00FF00,  # Green
            "title": "워크플로우 성공",
        },
        "failure": {
            "emoji": "❌",
            "color": 0xFF0000,  # Red
            "title": "워크플로우 실패",
        },
        "cancelled": {
            "emoji": "🚫",
            "color": 0x808080,  # Gray
            "title": "워크플로우 취소",
        },
    }
    
    config = status_config.get(status, status_config["started"])
    
    # Embed 생성
    embed = {
        "title": f"{config['emoji']} {config['title']}: {workflow_name}",
        "color": config["color"],
        "timestamp": datetime.utcnow().isoformat(),
        "fields": [],
    }
    
    # 필드 추가
    if actor:
        embed["fields"].append({
            "name": "실행자",
            "value": actor,
            "inline": True,
        })
    
    if branch:
        embed["fields"].append({
            "name": "브랜치",
            "value": branch,
            "inline": True,
        })
    
    if duration:
        embed["fields"].append({
            "name": "실행 시간",
            "value": duration,
            "inline": True,
        })
    
    if commit_message:
        # 커밋 메시지가 너무 길면 자르기
        commit_preview = commit_message[:200] + "..." if len(commit_message) > 200 else commit_message
        embed["fields"].append({
            "name": "커밋 메시지",
            "value": f"```{commit_preview}```",
            "inline": False,
        })
    
    if error_message and status == "failure":
        error_preview = error_message[:1000] + "..." if len(error_message) > 1000 else error_message
        embed["fields"].append({
            "name": "오류 메시지",
            "value": f"```{error_preview}```",
            "inline": False,
        })
    
    if run_url:
        embed["description"] = f"[워크플로우 로그 보기]({run_url})"
    
    embed["footer"] = {"text": "GitHub Actions"}
    
    payload = {"embeds": [embed]}
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"[INFO] Discord 알림 전송 성공: {workflow_name} - {status}")
        return True
    except Exception as e:
        print(f"[WARN] Discord 웹훅 전송 실패: {e}")
        return False


def main():
    """메인 함수"""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    workflow_name = os.getenv("GITHUB_WORKFLOW", "Unknown Workflow")
    status = sys.argv[1] if len(sys.argv) > 1 else "started"
    
    # GitHub Actions 환경 변수에서 정보 가져오기
    run_url = os.getenv("GITHUB_SERVER_URL") and os.getenv("GITHUB_REPOSITORY") and os.getenv("GITHUB_RUN_ID")
    if run_url:
        run_url = f"{os.getenv('GITHUB_SERVER_URL')}/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}"
    
    actor = os.getenv("GITHUB_ACTOR")
    branch = os.getenv("GITHUB_REF_NAME")
    
    # 커밋 메시지 가져오기 (환경 변수 또는 파일에서)
    commit_message = os.getenv("GITHUB_COMMIT_MESSAGE")
    if not commit_message:
        # 최근 커밋 메시지 가져오기 시도
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=%B"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                commit_message = result.stdout.strip()
        except Exception:
            pass
    
    # 실행 시간 계산 (환경 변수에서)
    duration = os.getenv("WORKFLOW_DURATION")
    
    # 오류 메시지 (실패 시)
    error_message = None
    if status == "failure":
        # 마지막 로그 파일에서 오류 추출 시도
        log_file = os.getenv("GITHUB_STEP_SUMMARY")
        if log_file and os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 오류 패턴 찾기
                    if "Error:" in content or "error:" in content:
                        error_message = content[-500:]  # 마지막 500자
            except Exception:
                pass
    
    send_workflow_notification(
        webhook_url=webhook_url,
        workflow_name=workflow_name,
        status=status,
        run_url=run_url,
        commit_message=commit_message,
        actor=actor,
        branch=branch,
        duration=duration,
        error_message=error_message,
    )


if __name__ == "__main__":
    main()

