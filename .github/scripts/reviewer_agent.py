#!/usr/bin/env python3
"""
ReviewerAgent
작성 에이전트 결과물을 한 번 더 다듬는 편집자 역할.
- 문체: 모든 문장은 "~다."로 끝나는 건조한 평서문
- 금지: 해요체, 이모지, 과도한 접속사("결론적으로", "마지막으로" 등)
- 구조: 긴 문단 분할, 소제목 보강
- 카테고리별 점검:
    dev   : 코드/트러블슈팅 과정 명료성
    daily : 감성 묘사 줄이고 사실 위주
    document/study/기타: 분석/근거 위주
"""

import os
import re
from typing import Optional
from google import genai


class ReviewerAgent:
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY 가 설정되지 않았습니다.")
        self.client = genai.Client(api_key=key)
        # 안정적 모델 우선
        self.model = "models/gemini-2.0-flash"

    def review(self, draft_content: str, category: str = "document") -> str:
        if not draft_content:
            return ""

        cat = (category or "document").lower()
        cat_rule = {
            "dev": "- 코드 흐름과 트러블슈팅 과정을 단계별로 명료하게 정리하라.\n- 코드/에러 메시지는 필요한 최소한만 남기되 설명은 한국어로 풀어라.",
            "daily": """- **1인칭 시점 유지:** '나', '내가', '나는' 등 개인의 관점을 유지하라. 3인칭 관찰자 시점("분석한다", "논한다")은 절대 사용하지 마라.
- **감정 묘사 강화:** 단순히 사실만 나열하지 말고, 그때 느꼈던 감정(기쁨, 당황, 후회, 짜증 등)을 구체적으로 서술하라.
- **현장감 강화:** "대중교통 시스템 마비" 같은 추상적 표현 대신, "지하철역까지 가는 데만 30분이 걸려서 발이 퉁퉁 부었다"는 식의 구체적인 묘사를 사용하라.
- **개인적인 경험 중심:** 뉴스 기사나 보고서 같은 객관적 서술을 피하고, 일기장에 쓰는 것처럼 개인적인 경험과 느낌을 중심으로 서술하라.
- **금지:** "본고는", "분석한다", "시사한다" 같은 딱딱한 논문조 표현 절대 금지.""",
        }.get(cat, "- 데이터/근거 기반으로 타당성을 보강하라.")

        prompt = f"""
너는 한국어 기술 블로그의 편집자다. 아래 초안을 아래 규칙에 맞게 다듬어라.

[문체 규칙]
- 모든 문장은 반드시 "~다."로 끝나는 건조한 평서문. 해요체 금지.
- 이모지 전면 삭제.
- "결론적으로", "마지막으로" 같은 접속사는 삭제하거나 문장을 재구성.

[구조 조정]
- 문단이 너무 길면 짧게 나누고, 필요하면 소제목을 보강한다.
- References/각주 형식은 유지하되 불필요한 감탄/인사말 제거.

[카테고리별 점검]
{cat_rule}

[입력 초안]
{draft_content}

[출력 형식]
- Markdown 본문만 출력한다.
- 모든 문장은 "~다."로 끝나야 한다.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            text = (response.text or "").strip()
            text = self._post_process(text)
            return text if text else draft_content
        except Exception:
            # 실패 시 원본을 그대로 반환 (안전)
            return draft_content

    def _post_process(self, content: str) -> str:
        # 이모지 제거
        content = re.sub(r"[\U00010000-\U0010ffff]", "", content)
        lines = content.split("\n")
        processed = []
        for line in lines:
            original_line = line
            line = line.strip()
            if not line:
                processed.append("")
                continue
            
            # 제목/헤더는 건드리지 않음 (#으로 시작)
            if line.startswith('#'):
                processed.append(original_line)
                continue
            
            # 리스트 항목은 건드리지 않음 (-, *, 숫자로 시작)
            if re.match(r'^[-*•]\s+', line) or re.match(r'^\d+[.)]\s+', line):
                processed.append(original_line)
                continue
            
            # 인용문(blockquote)은 건드리지 않음
            if line.startswith('>'):
                processed.append(original_line)
                continue
            
            # 코드 블록은 건드리지 않음
            if line.startswith('```'):
                processed.append(original_line)
                continue
            
            # 종결어미 정리 (자연스러운 문장만)
            if line.endswith("요."):
                line = original_line[:-2] + "다."
            elif line.endswith("어요."):
                line = original_line[:-3] + "다."
            elif line.endswith("습니다."):
                line = original_line[:-4] + "다."
            elif line.endswith("다."):
                # 이미 "다."로 끝나면 그대로
                line = original_line
            else:
                # 이미 적절한 종결어미가 있으면 그대로 유지
                # (예: "~이다.", "~했다.", "~였다.", "~임", "~음" 등)
                if re.search(r'[다했였임음]$', line) or line.endswith('.') or line.endswith('!'):
                    line = original_line
                else:
                    # 종결어미가 없는 경우에만 "다." 추가 (하지만 너무 짧은 줄은 제외)
                    if len(line) > 10:
                        line = original_line + "다."
                    else:
                        line = original_line
            
            # 금지 접속사 제거
            line = re.sub(r"\b(결론적으로|마지막으로)\b", "", line)
            processed.append(line)
        return "\n".join(processed)

