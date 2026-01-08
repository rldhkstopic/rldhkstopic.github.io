#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Slash Command → GitHub 요청 커밋 파이프라인

환경 변수:
- DISCORD_BOT_TOKEN : Discord Bot Token
- DISCORD_GUILD_ID  : (선택) 슬래시 명령 등록할 길드 ID (숫자)
- GITHUB_TOKEN      : GitHub Personal Access Token (repo 권한)
- GITHUB_REPO       : 대상 리포지토리 "owner/repo"
- REQUEST_DIR       : 요청 파일 경로 (기본: "_auto_post_requests")
- DAILY_LOG_CHANNEL : 일기 로그 수집 채널 이름 (기본: "일기-로그")
- DAILY_LOGS_DIR    : 일기 로그 저장 디렉토리 (기본: "_daily_logs")

기능:
1. `/write` 명령어: 블로그 글 요청 등록
2. 메시지 수집: `#일기-로그` 채널의 메시지를 자동으로 수집하여 GitHub에 저장
"""

import json
import os
import asyncio
from datetime import datetime, timezone, timedelta

import discord
from discord import app_commands
from github import Github
from github import Auth

# .env 파일 지원 (python-dotenv 설치 필요)
try:
    from dotenv import load_dotenv
    load_dotenv()  # local_bot/.env 파일 자동 로드
except ImportError:
    pass  # python-dotenv가 없어도 환경 변수로 동작

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "rldhkstopic/rldhkstopic.github.io")
REQUEST_DIR = os.getenv("REQUEST_DIR", "_auto_post_requests")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "_auto_post_requests_processed")
RESULTS_DIR = os.getenv("RESULTS_DIR", "_auto_post_results")
DAILY_LOG_CHANNEL = os.getenv("DAILY_LOG_CHANNEL", "일기-로그")  # Discord 채널 이름
DAILY_LOGS_DIR = os.getenv("DAILY_LOGS_DIR", "_daily_logs")

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN이 설정되지 않았습니다.")
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN이 설정되지 않았습니다.")


def commit_daily_log_to_github(message_data: dict) -> bool:
    """
    일기 로그를 GitHub에 커밋한다.
    
    Args:
        message_data: 메시지 데이터 딕셔너리
        
    Returns:
        bool: 커밋 성공 여부
    """
    try:
        auth = Auth.Token(GITHUB_TOKEN)
        gh = Github(auth=auth)
        repo = gh.get_repo(GITHUB_REPO)
        
        # 날짜 추출 (KST 기준)
        timestamp_str = message_data.get('timestamp', '')
        try:
            # zoneinfo 사용 (Python 3.9+)
            from zoneinfo import ZoneInfo
            kst = ZoneInfo("Asia/Seoul")
            if 'Z' in timestamp_str:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(timestamp_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dt_kst = dt.astimezone(kst)
        except ImportError:
            # Python 3.8 이하: pytz 사용 또는 UTC+9 직접 계산
            try:
                import pytz
                kst = pytz.timezone('Asia/Seoul')
                if 'Z' in timestamp_str:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                dt_kst = dt.astimezone(kst)
            except ImportError:
                # pytz도 없으면 UTC+9 직접 계산
                if 'Z' in timestamp_str:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                # UTC+9 = 9시간 추가
                dt_kst = dt.replace(tzinfo=None) + timedelta(hours=9)
        
        date_str = dt_kst.strftime('%Y-%m-%d')
        log_id = message_data.get('id', str(int(dt.timestamp() * 1000)))
        filename = f"{log_id}.json"
        path = f"{DAILY_LOGS_DIR}/{date_str}/{filename}"
        
        # JSON 변환
        content = json.dumps(message_data, ensure_ascii=False, indent=2)
        message = f"[DAILY LOG] {date_str} - {message_data.get('content', '')[:50]}"
        
        try:
            # 파일 생성 (GitHub API는 경로에 디렉토리가 포함되어 있으면 자동으로 생성)
            repo.create_file(path, message, content)
            return True
        except Exception as e:
            # 파일이 이미 존재하면 업데이트하지 않고 무시
            error_str = str(e).lower()
            if "already exists" in error_str or "422" in error_str or "sha" in error_str:
                print(f"[INFO] 로그 파일이 이미 존재합니다: {path}")
                return True
            raise
    except Exception as e:
        print(f"[ERROR] 일기 로그 커밋 실패: {e}")
        return False


def commit_request_to_github(payload: dict) -> tuple[str, str]:
    """요청 JSON을 GitHub에 커밋하고 워크플로우를 트리거"""
    # Deprecation 경고 수정: Auth.Token 사용
    auth = Auth.Token(GITHUB_TOKEN)
    gh = Github(auth=auth)
    repo = gh.get_repo(GITHUB_REPO)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"request_{ts}.json"
    path = f"{REQUEST_DIR}/{filename}"

    content = json.dumps(payload, ensure_ascii=False, indent=2)
    message = f"[REQUEST] {payload.get('Topic','Untitled')}"

    # 요청 파일 커밋
    repo.create_file(path, message, content)
    
    # 워크플로우 트리거 파일 업데이트 (GitHub Actions가 감지하도록)
    trigger_path = ".github/force-auto-post-run"
    trigger_content = f"Request triggered at {datetime.now(timezone.utc).isoformat()}\nRequest: {filename}"
    
    try:
        # 기존 파일이 있으면 업데이트, 없으면 생성
        try:
            existing_file = repo.get_contents(trigger_path)
            repo.update_file(
                trigger_path,
                f"[REQUEST] Trigger workflow for {payload.get('Topic','Untitled')}",
                trigger_content,
                existing_file.sha
            )
        except Exception:
            # 파일이 없으면 생성
            repo.create_file(trigger_path, f"[REQUEST] Trigger workflow for {payload.get('Topic','Untitled')}", trigger_content)
    except Exception as e:
        print(f"[WARN] 워크플로우 트리거 파일 업데이트 실패 (요청 파일은 커밋됨): {e}")
    
    return path, filename


async def monitor_workflow_status(
    interaction: discord.Interaction,
    request_filename: str,
    max_wait_time: int = 600,  # 최대 10분 대기
    check_interval: int = 10,  # 10초마다 체크
):
    """워크플로우 실행 상태를 모니터링하고 Discord에 업데이트"""
    auth = Auth.Token(GITHUB_TOKEN)
    gh = Github(auth=auth)
    repo = gh.get_repo(GITHUB_REPO)
    
    workflow_name = "Auto Post Daily"
    start_time = datetime.now(timezone.utc)
    last_status = None
    run_id = None
    
    # 초기 메시지 전송
    status_embed = discord.Embed(
        title="⏳ 워크플로우 실행 대기 중",
        description=f"요청: `{request_filename}`\n워크플로우를 찾는 중...",
        color=0xFFA500,  # Orange
    )
    status_embed.set_footer(text="상태를 확인하는 중...")
    status_message = await interaction.followup.send(embed=status_embed, wait=True)
    
    try:
        # 워크플로우 실행 찾기 (최근 실행 중에서)
        elapsed = 0
        while elapsed < max_wait_time:
            try:
                # 워크플로우 파일 찾기
                workflows = repo.get_workflows()
                target_workflow = None
                for workflow in workflows:
                    if "auto-post" in workflow.name.lower() or "auto post" in workflow.name.lower():
                        target_workflow = workflow
                        break
                
                if not target_workflow:
                    # 워크플로우를 찾지 못했으면 계속 대기
                    await asyncio.sleep(check_interval)
                    elapsed += check_interval
                    continue
                
                # 최근 워크플로우 실행 목록 가져오기
                runs = target_workflow.get_runs()
                
                # 가장 최근 실행 찾기
                for run in list(runs)[:5]:  # 최근 5개만 확인
                    # 우리가 트리거한 실행인지 확인 (최근 2분 이내)
                    created_at = run.created_at
                    if created_at and (datetime.now(timezone.utc) - created_at.replace(tzinfo=timezone.utc)).total_seconds() < 120:
                        # 워크플로우 이름 확인
                        if workflow_name.lower() in run.name.lower() or "auto-post" in run.name.lower():
                            run_id = run.id
                            current_status = run.status
                            conclusion = run.conclusion
                            
                            # 상태가 변경되었을 때만 업데이트
                            if current_status != last_status or conclusion:
                                last_status = current_status
                                
                                # 상태에 따른 색상 및 이모지
                                if conclusion == "success":
                                    color = 0x00FF00  # Green
                                    emoji = "✅"
                                    status_text = "완료"
                                elif conclusion == "failure":
                                    color = 0xFF0000  # Red
                                    emoji = "❌"
                                    status_text = "실패"
                                elif conclusion == "cancelled":
                                    color = 0x808080  # Gray
                                    emoji = "🚫"
                                    status_text = "취소됨"
                                elif current_status == "in_progress" or current_status == "queued":
                                    color = 0xFFA500  # Orange
                                    emoji = "⏳"
                                    status_text = "실행 중"
                                else:
                                    color = 0x5865F2  # Discord Blue
                                    emoji = "🔄"
                                    status_text = current_status
                                
                                # Embed 업데이트
                                updated_embed = discord.Embed(
                                    title=f"{emoji} 워크플로우 상태: {status_text}",
                                    description=f"요청: `{request_filename}`\n실행 ID: `{run_id}`",
                                    color=color,
                                )
                                
                                if conclusion:
                                    updated_embed.add_field(
                                        name="결과",
                                        value=f"**{conclusion.upper()}**",
                                        inline=True,
                                    )
                                    updated_embed.add_field(
                                        name="실행 시간",
                                        value=f"{(datetime.now(timezone.utc) - start_time).total_seconds():.0f}초",
                                        inline=True,
                                    )
                                    
                                    # 성공 시 포스트 링크 추가
                                    if conclusion == "success":
                                        updated_embed.add_field(
                                            name="📝 생성된 포스트",
                                            value=f"[GitHub에서 확인](https://github.com/{GITHUB_REPO}/tree/main/_posts)",
                                            inline=False,
                                        )
                                    
                                    updated_embed.set_footer(text="처리 완료")
                                    await status_message.edit(embed=updated_embed)
                                    return  # 완료되면 종료
                                else:
                                    updated_embed.add_field(
                                        name="상태",
                                        value=current_status,
                                        inline=True,
                                    )
                                    updated_embed.add_field(
                                        name="경과 시간",
                                        value=f"{(datetime.now(timezone.utc) - start_time).total_seconds():.0f}초",
                                        inline=True,
                                    )
                                    updated_embed.set_footer(text="다음 확인까지 대기 중...")
                                    await status_message.edit(embed=updated_embed)
                                
                                break
                
                # 실행을 찾지 못했으면 계속 대기
                if not run_id:
                    await asyncio.sleep(check_interval)
                    elapsed += check_interval
                    continue
                
                # 실행이 완료되었는지 확인
                if conclusion:
                    break
                
                # 다음 체크까지 대기
                await asyncio.sleep(check_interval)
                elapsed += check_interval
                
            except Exception as e:
                print(f"[WARN] 워크플로우 상태 확인 중 오류: {e}")
                await asyncio.sleep(check_interval)
                elapsed += check_interval
        
        # 타임아웃 처리
        if elapsed >= max_wait_time:
            timeout_embed = discord.Embed(
                title="⏰ 타임아웃",
                description=f"요청: `{request_filename}`\n워크플로우 상태 확인 시간이 초과되었습니다.",
                color=0xFFA500,
            )
            timeout_embed.add_field(
                name="수동 확인",
                value=f"[GitHub Actions에서 직접 확인](https://github.com/{GITHUB_REPO}/actions)",
                inline=False,
            )
            await status_message.edit(embed=timeout_embed)
    
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ 오류 발생",
            description=f"워크플로우 상태 모니터링 중 오류가 발생했습니다:\n```{str(e)}```",
            color=0xFF0000,
        )
        await status_message.edit(embed=error_embed)


def create_help_embed() -> discord.Embed:
    """도움말 Embed 생성"""
    embed = discord.Embed(
        title="📚 블로그 포스팅 봇 사용 가이드",
        description="이 봇을 사용하여 블로그 글 요청을 등록할 수 있습니다.",
        color=0x5865F2,  # Discord 블루
    )

    embed.add_field(
        name="📝 `/write` - 새 글 요청",
        value=(
            "블로그 포스트 작성을 요청합니다.\n\n"
            "**사용 방법:**\n"
            "1. `/write` 명령어 입력\n"
            "2. 카테고리 선택 (dev, study, daily, essay)\n"
            "3. 모달 창에서 다음 정보 입력:\n"
            "   • **Topic**: 글 제목/주제 (필수)\n"
            "   • **Situation**: 상황/문제 설명\n"
            "   • **Action**: 해결 방법/시도한 내용\n"
            "   • **Memo**: 기타 메모나 참고 링크\n"
            "4. 제출하면 GitHub에 요청이 등록됩니다\n\n"
            "**처리 과정:**\n"
            "1. 요청이 GitHub 리포지토리에 JSON 파일로 저장됩니다\n"
            "2. GitHub Actions가 자동으로 글을 생성합니다\n"
            "3. Writer → Reviewer → Validator 순서로 처리됩니다\n"
            "4. 최종적으로 `_posts/` 폴더에 마크다운 파일이 생성됩니다"
        ),
        inline=False,
    )

    embed.add_field(
        name="📂 카테고리 설명",
        value=(
            "**dev**: 개발 관련 글 (코드, 트러블슈팅, 기술 스택 등)\n"
            "**study**: 학습/공부 관련 글 (개념 정리, 학습 노트 등)\n"
            "**daily**: 일상/작업 로그 (짧은 실험, 관찰 등)\n"
            "**essay**: 에세이/분석 글 (데이터 분석, 인사이트 등)"
        ),
        inline=False,
    )

    embed.add_field(
        name="⚙️ 작동 원리",
        value=(
            "1. **요청 등록**: Discord에서 입력한 내용이 GitHub에 JSON 파일로 저장됩니다\n"
            "2. **자동 처리**: GitHub Actions가 요청을 감지하고 AI로 글을 생성합니다\n"
            "3. **품질 검증**: Reviewer Agent가 문체, 금지어, 이모지를 검토하고 수정합니다\n"
            "4. **자동 발행**: 검증된 글은 자동으로 블로그에 게시됩니다"
        ),
        inline=False,
    )

    embed.add_field(
        name="💡 팁",
        value=(
            "• **Topic**은 명확하고 구체적으로 작성하세요\n"
            "• **Situation**과 **Action**을 자세히 작성할수록 더 풍부한 글이 생성됩니다\n"
            "• **Memo**에 참고 링크나 추가 정보를 넣으면 더 정확한 글을 작성할 수 있습니다\n"
            "• 요청 후 GitHub Actions 로그에서 처리 상태를 확인할 수 있습니다"
        ),
        inline=False,
    )

    embed.set_footer(text="문제가 발생하면 관리자에게 문의하세요.")
    embed.timestamp = datetime.now(timezone.utc)

    return embed


class WriteModal(discord.ui.Modal, title="새 글 요청"):
    def __init__(self, category: str):
        super().__init__(timeout=300)
        self.category = category

        self.topic = discord.ui.TextInput(
            label="Topic (제목/주제)",
            style=discord.TextStyle.short,
            required=True,
            max_length=120,
        )
        self.situation = discord.ui.TextInput(
            label="Situation (상황/문제)",
            style=discord.TextStyle.long,
            required=False,
            max_length=2000,
        )
        self.action = discord.ui.TextInput(
            label="Action (해결/시도)",
            style=discord.TextStyle.long,
            required=False,
            max_length=2000,
        )
        self.memo = discord.ui.TextInput(
            label="Memo (기타 메모/링크)",
            style=discord.TextStyle.long,
            required=False,
            max_length=2000,
        )

        self.add_item(self.topic)
        self.add_item(self.situation)
        self.add_item(self.action)
        self.add_item(self.memo)

    async def on_submit(self, interaction: discord.Interaction):
        # GitHub API 호출이 오래 걸릴 수 있으므로 즉시 defer로 interaction 유지
        await interaction.response.defer(ephemeral=True)
        
        try:
            payload = {
                "Category": self.category,
                "Topic": self.topic.value.strip(),
                "Situation": self.situation.value.strip(),
                "Action": self.action.value.strip(),
                "Memo": self.memo.value.strip(),
                "source": "discord",
                "requested_at": datetime.now(timezone.utc).isoformat(),
                "user": str(interaction.user),
            }
            path, filename = commit_request_to_github(payload)
            
            # 요청 접수 메시지
            await interaction.followup.send(
                f"✅ 요청이 접수되었습니다.\n- 카테고리: {self.category}\n- 파일: `{path}`\n\n워크플로우 상태를 모니터링합니다...",
                ephemeral=True,
            )
            
            # 백그라운드에서 워크플로우 상태 모니터링 시작
            asyncio.create_task(monitor_workflow_status(interaction, filename))
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ 요청 처리 중 오류가 발생했습니다: {str(e)}", ephemeral=True
            )


class DiscordBot(discord.Client):
    def __init__(self):
        # 메시지 내용을 읽기 위해 message_content intent 필요
        intents = discord.Intents.default()
        intents.message_content = True  # 메시지 내용 읽기 권한
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"봇이 준비되었습니다! (Bot is ready!)")
        print(f"로그인한 사용자: {self.user}")
        print(f"서버 수: {len(self.guilds)}")
        print(f"[INFO] 일기 로그 수집 채널: #{DAILY_LOG_CHANNEL}")

    async def on_message(self, message: discord.Message):
        """
        메시지 수신 시 호출되는 이벤트 핸들러
        일기 로그 채널의 메시지를 수집하여 GitHub에 저장한다.
        """
        # 봇 자신의 메시지는 무시
        if message.author == self.user:
            return
        
        # 특정 채널만 처리
        if message.channel.name != DAILY_LOG_CHANNEL:
            return
        
        # 명령어는 무시 (슬래시 명령어는 별도 처리)
        if message.content.startswith('/'):
            return
        
        # 메시지 데이터 구성 (KST 변환)
        try:
            from zoneinfo import ZoneInfo
            kst = ZoneInfo("Asia/Seoul")
        except ImportError:
            try:
                import pytz
                kst = pytz.timezone('Asia/Seoul')
            except ImportError:
                # pytz도 없으면 UTC+9 직접 계산
                kst = None
        
        if kst:
            timestamp = message.created_at.replace(tzinfo=timezone.utc).astimezone(kst)
        else:
            # UTC+9 직접 계산
            timestamp = message.created_at.replace(tzinfo=timezone.utc) + timedelta(hours=9)
        
        message_data = {
            'id': str(int(message.created_at.timestamp() * 1000)),
            'content': message.content,
            'timestamp': timestamp.isoformat(),
            'mood': None,  # 추후 확장 가능
            'tags': None,  # 추후 확장 가능
            'location': None,  # 추후 확장 가능
            'author': str(message.author),
            'message_id': str(message.id),
            'channel_id': str(message.channel.id),
        }
        
        # 첨부 파일이 있으면 URL 추가
        if message.attachments:
            message_data['attachments'] = [att.url for att in message.attachments]
        
        # GitHub에 커밋 (비동기로 처리하여 메시지 응답 지연 방지)
        try:
            # 동기 함수이므로 별도 스레드에서 실행
            import threading
            thread = threading.Thread(
                target=commit_daily_log_to_github,
                args=(message_data,),
                daemon=True
            )
            thread.start()
            print(f"[INFO] 일기 로그 수집: {message_data['id']} - {message.content[:50]}")
        except Exception as e:
            print(f"[ERROR] 일기 로그 수집 실패: {e}")

    async def setup_hook(self):
        # 길드 스코프에만 명령을 등록하면 전파가 빠르다.
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))

            @self.tree.command(
                name="write",
                description="새 글 요청을 등록합니다.",
                guild=guild,
            )
            @app_commands.describe(
                category="카테고리 선택",
            )
            @app_commands.choices(
                category=[
                    app_commands.Choice(name="dev", value="dev"),
                    app_commands.Choice(name="study", value="study"),
                    app_commands.Choice(name="daily", value="daily"),
                    app_commands.Choice(name="essay", value="essay"),
                ]
            )
            async def write(interaction: discord.Interaction, category: app_commands.Choice[str]):
                modal = WriteModal(category.value)
                await interaction.response.send_modal(modal)

            @self.tree.command(
                name="help",
                description="봇 사용 방법을 안내합니다.",
                guild=guild,
            )
            async def help(interaction: discord.Interaction):
                embed = create_help_embed()
                await interaction.response.send_message(embed=embed, ephemeral=True)

            await self.tree.sync(guild=guild)
        else:
            # 글로벌 등록 (전파까지 최대 1시간 정도)
            @self.tree.command(
                name="write",
                description="새 글 요청을 등록합니다.",
            )
            @app_commands.describe(
                category="카테고리 선택",
            )
            @app_commands.choices(
                category=[
                    app_commands.Choice(name="dev", value="dev"),
                    app_commands.Choice(name="study", value="study"),
                    app_commands.Choice(name="daily", value="daily"),
                    app_commands.Choice(name="essay", value="essay"),
                ]
            )
            async def write(interaction: discord.Interaction, category: app_commands.Choice[str]):
                modal = WriteModal(category.value)
                await interaction.response.send_modal(modal)

            @self.tree.command(
                name="help",
                description="봇 사용 방법을 안내합니다.",
            )
            async def help(interaction: discord.Interaction):
                embed = create_help_embed()
                await interaction.response.send_message(embed=embed, ephemeral=True)

            @self.tree.command(
                name="list",
                description="대기 중인 요청 목록을 확인합니다.",
            )
            async def list_requests(interaction: discord.Interaction):
                await interaction.response.defer(ephemeral=True)
                try:
                    auth = Auth.Token(GITHUB_TOKEN)
                    gh = Github(auth=auth)
                    repo = gh.get_repo(GITHUB_REPO)
                    
                    try:
                        contents = repo.get_contents(REQUEST_DIR)
                        if not isinstance(contents, list):
                            contents = [contents]
                        
                        if not contents:
                            await interaction.followup.send("✅ 대기 중인 요청이 없습니다.", ephemeral=True)
                            return
                        
                        embed = discord.Embed(
                            title="📋 대기 중인 요청 목록",
                            description=f"총 {len(contents)}개의 요청이 대기 중입니다.",
                            color=0x5865F2,
                        )
                        
                        for i, file in enumerate(contents[:10], 1):
                            try:
                                content = file.decoded_content.decode('utf-8')
                                data = json.loads(content)
                                topic = data.get('Topic', 'N/A')
                                category = data.get('Category', 'N/A')
                                requested_at = data.get('requested_at', 'N/A')
                                
                                embed.add_field(
                                    name=f"{i}. {topic[:50]}",
                                    value=f"카테고리: {category}\n요청 시간: {requested_at[:19] if len(requested_at) > 19 else requested_at}",
                                    inline=False,
                                )
                            except Exception:
                                embed.add_field(
                                    name=f"{i}. {file.name}",
                                    value="파일 파싱 오류",
                                    inline=False,
                                )
                        
                        if len(contents) > 10:
                            embed.set_footer(text=f"외 {len(contents) - 10}개의 요청이 더 있습니다.")
                        
                        await interaction.followup.send(embed=embed, ephemeral=True)
                    except Exception as e:
                        if "404" in str(e):
                            await interaction.followup.send("✅ 대기 중인 요청이 없습니다.", ephemeral=True)
                        else:
                            await interaction.followup.send(f"❌ 오류 발생: {str(e)}", ephemeral=True)
                except Exception as e:
                    await interaction.followup.send(f"❌ 요청 목록 조회 실패: {str(e)}", ephemeral=True)

            @self.tree.command(
                name="status",
                description="최근 처리 결과를 확인합니다.",
            )
            async def status(interaction: discord.Interaction):
                await interaction.response.defer(ephemeral=True)
                try:
                    auth = Auth.Token(GITHUB_TOKEN)
                    gh = Github(auth=auth)
                    repo = gh.get_repo(GITHUB_REPO)
                    
                    try:
                        processed_contents = repo.get_contents(PROCESSED_DIR)
                        if not isinstance(processed_contents, list):
                            processed_contents = [processed_contents]
                        processed_count = len(processed_contents)
                    except Exception:
                        processed_count = 0
                    
                    try:
                        results_contents = repo.get_contents(RESULTS_DIR)
                        if not isinstance(results_contents, list):
                            results_contents = [results_contents]
                        
                        recent_results = sorted(results_contents, key=lambda x: x.name, reverse=True)[:5]
                        
                        embed = discord.Embed(
                            title="📊 처리 현황",
                            color=0x5865F2,
                        )
                        
                        embed.add_field(
                            name="처리 완료",
                            value=f"{processed_count}개",
                            inline=True,
                        )
                        
                        if recent_results:
                            status_text = ""
                            for result_file in recent_results:
                                try:
                                    content = result_file.decoded_content.decode('utf-8')
                                    data = json.loads(content)
                                    status_emoji = "✅" if data.get('status') == 'success' else "❌"
                                    topic = data.get('topic', 'N/A')[:30]
                                    status_text += f"{status_emoji} {topic}\n"
                                except Exception:
                                    pass
                            
                            if status_text:
                                embed.add_field(
                                    name="최근 처리 결과",
                                    value=status_text[:1024],
                                    inline=False,
                                )
                        else:
                            embed.add_field(
                                name="최근 처리 결과",
                                value="처리 결과가 없습니다.",
                                inline=False,
                            )
                        
                        await interaction.followup.send(embed=embed, ephemeral=True)
                    except Exception as e:
                        if "404" in str(e):
                            await interaction.followup.send("📊 아직 처리된 요청이 없습니다.", ephemeral=True)
                        else:
                            await interaction.followup.send(f"❌ 오류 발생: {str(e)}", ephemeral=True)
                except Exception as e:
                    await interaction.followup.send(f"❌ 상태 조회 실패: {str(e)}", ephemeral=True)

            await self.tree.sync()


def main():
    bot = DiscordBot()
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("❌ Discord 봇 토큰이 유효하지 않습니다. DISCORD_BOT_TOKEN을 확인하세요.")
    except Exception as e:
        print(f"❌ 봇 실행 중 오류 발생: {e}")


if __name__ == "__main__":
    main()

