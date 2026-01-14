#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
경제 뉴스 실시간 수집 및 Discord 전송 봇

환경 변수:
- DISCORD_BOT_TOKEN : Discord Bot Token
- DISCORD_GUILD_ID  : (선택) 슬래시 명령 등록할 길드 ID (숫자)
- NEWS_CHANNEL      : 뉴스 전송 채널 이름 (기본: "경제뉴스")
- NEWS_CHECK_INTERVAL : 뉴스 체크 간격(초) (기본: 300 = 5분)
- ECONOMIC_NEWS_RSS_FEEDS : RSS 피드 URL 목록 (콤마로 구분)
"""

import os
import asyncio
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Set
import discord
from discord import app_commands
from google import genai

# .env 파일 지원
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")
NEWS_CHANNEL = os.getenv("NEWS_CHANNEL", "경제뉴스")
NEWS_CHECK_INTERVAL = int(os.getenv("NEWS_CHECK_INTERVAL", "300"))  # 5분
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ECONOMIC_NEWS_RSS_FEEDS = os.getenv("ECONOMIC_NEWS_RSS_FEEDS", "").strip()

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN이 설정되지 않았습니다.")

# 기본 RSS 피드 목록
DEFAULT_FEEDS = [
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://feeds.bloomberg.com/technology/news.rss",
    "https://feeds.bloomberg.com/politics/news.rss",
    # 추가 RSS 피드는 환경 변수로 설정
]

if ECONOMIC_NEWS_RSS_FEEDS:
    feed_urls = [u.strip() for u in ECONOMIC_NEWS_RSS_FEEDS.split(",") if u.strip()]
else:
    feed_urls = DEFAULT_FEEDS


class NewsCollector:
    """뉴스 수집 및 요약 클래스"""
    
    def __init__(self):
        self.seen_links: Set[str] = set()
        self.client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
    
    def fetch_rss_items(self, url: str, hours: int = 24) -> List[Dict]:
        """RSS 피드에서 최근 N시간 내 뉴스 항목 수집"""
        items = []
        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "rldhkstopic-news-collector/1.0"})
            if resp.status_code != 200:
                return items
            
            root = ET.fromstring(resp.text)
            channel = root.find("channel")
            if channel is None:
                return items
            
            tz = ZoneInfo("Asia/Seoul")
            cutoff_time = datetime.now(tz) - timedelta(hours=hours)
            
            for item in channel.findall("item"):
                title_el = item.find("title")
                link_el = item.find("link")
                pub_el = item.find("pubDate")
                desc_el = item.find("description")
                
                title = (title_el.text or "").strip() if title_el is not None else ""
                link = (link_el.text or "").strip() if link_el is not None else ""
                pub = (pub_el.text or "").strip() if pub_el is not None else ""
                desc = (desc_el.text or "").strip() if desc_el is not None else ""
                
                if not title or not link:
                    continue
                
                # 중복 체크
                if link in self.seen_links:
                    continue
                
                # 시간 필터링
                try:
                    dt = parsedate_to_datetime(pub)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
                    dt_kst = dt.astimezone(tz)
                    
                    if dt_kst < cutoff_time:
                        continue
                except Exception:
                    continue
                
                self.seen_links.add(link)
                items.append({
                    "title": title,
                    "link": link,
                    "summary": desc,
                    "published_at": dt_kst.isoformat(),
                    "source": self._extract_source(url),
                })
        except Exception as e:
            print(f"[ERROR] RSS 수집 실패 ({url}): {e}")
        
        return items
    
    def _extract_source(self, url: str) -> str:
        """URL에서 뉴스 소스 추출"""
        if "bloomberg" in url.lower():
            return "블룸버그"
        elif "daum" in url.lower():
            return "다음경제"
        elif "investing" in url.lower():
            return "Investing"
        elif "hankyung" in url.lower():
            return "한국경제"
        elif "reuters" in url.lower():
            return "로이터"
        elif "wsj" in url.lower():
            return "WSJ"
        else:
            return "기타"
    
    def summarize_news(self, items: List[Dict]) -> str:
        """뉴스 항목들을 요약"""
        if not items:
            return ""
        
        if not self.client:
            # Gemini API가 없으면 간단한 요약
            return f"총 {len(items)}건의 뉴스가 수집되었습니다."
        
        try:
            news_text = "\n\n".join([
                f"[{i+1}] {item['title']}\n{item.get('summary', '')[:200]}"
                for i, item in enumerate(items[:10])  # 최대 10개만
            ])
            
            prompt = f"""다음 경제 뉴스 항목들을 간단히 요약해주세요. 각 뉴스의 핵심 내용을 1-2문장으로 정리하세요.

{news_text}

요약 형식:
- 각 뉴스마다 제목과 핵심 내용을 1-2문장으로 요약
- 한국어로 작성
- 이모지 사용 금지"""
            
            response = self.client.models.generate_content(
                model="models/gemini-2.0-flash-exp",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"[ERROR] 뉴스 요약 실패: {e}")
            return f"총 {len(items)}건의 뉴스가 수집되었습니다."
    
    def collect_new_news(self) -> List[Dict]:
        """모든 RSS 피드에서 새로운 뉴스 수집"""
        all_items = []
        for url in feed_urls:
            items = self.fetch_rss_items(url, hours=24)
            all_items.extend(items)
        
        # 시간순 정렬
        all_items.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        return all_items


class NewsBot(discord.Client):
    """뉴스 수집 및 전송 Discord 봇"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.collector = NewsCollector()
        self.news_channel = None
        self.is_running = False
    
    async def on_ready(self):
        print(f"봇이 준비되었습니다! (Bot is ready!)")
        print(f"로그인한 사용자: {self.user}")
        print(f"서버 수: {len(self.guilds)}")
        
        # 뉴스 채널 찾기
        for guild in self.guilds:
            for channel in guild.channels:
                if channel.name == NEWS_CHANNEL:
                    self.news_channel = channel
                    print(f"[INFO] 뉴스 채널 찾음: #{NEWS_CHANNEL}")
                    break
        
        if not self.news_channel:
            print(f"[WARN] 뉴스 채널을 찾을 수 없습니다: #{NEWS_CHANNEL}")
        
        # 뉴스 수집 태스크 시작
        if not self.is_running:
            self.is_running = True
            asyncio.create_task(self.news_collection_loop())
    
    async def news_collection_loop(self):
        """주기적으로 뉴스 수집 및 전송"""
        await self.wait_until_ready()
        
        while self.is_running:
            try:
                if not self.news_channel:
                    await asyncio.sleep(60)
                    continue
                
                # 새로운 뉴스 수집
                new_items = self.collector.collect_new_news()
                
                if new_items:
                    print(f"[INFO] 새로운 뉴스 {len(new_items)}건 수집")
                    
                    # 뉴스별로 개별 전송 또는 배치 전송
                    for item in new_items[:5]:  # 최대 5개씩
                        embed = discord.Embed(
                            title=item['title'][:256],
                            description=item.get('summary', '')[:2000] or "요약 없음",
                            url=item['link'],
                            color=0x5865F2,
                            timestamp=datetime.fromisoformat(item['published_at'].replace('Z', '+00:00'))
                        )
                        embed.set_footer(text=f"출처: {item.get('source', '알 수 없음')}")
                        
                        try:
                            await self.news_channel.send(embed=embed)
                            await asyncio.sleep(2)  # Rate limit 방지
                        except Exception as e:
                            print(f"[ERROR] 메시지 전송 실패: {e}")
                
                await asyncio.sleep(NEWS_CHECK_INTERVAL)
            except Exception as e:
                print(f"[ERROR] 뉴스 수집 루프 오류: {e}")
                await asyncio.sleep(60)
    
    async def setup_hook(self):
        """슬래시 명령어 등록"""
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()


def main():
    bot = NewsBot()
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("❌ Discord 봇 토큰이 유효하지 않습니다.")
    except Exception as e:
        print(f"❌ 봇 실행 중 오류 발생: {e}")


if __name__ == "__main__":
    main()
