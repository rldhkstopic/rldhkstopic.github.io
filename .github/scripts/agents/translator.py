"""
번역 에이전트
한글 마크다운 글을 입력받아 기술 블로그에 적합한 영어로 번역한다.

역할:
- 한글 마크다운 글을 입력받아 기술 블로그에 적합한 영어로 번역
- 본문 번역: Gemini를 이용해 자연스러운 의역(Paraphrasing) 수행
  * 단어 단위 번역이 아닌 의미 기반 의역
  * 자연스러운 영어 표현으로 재구성
  * 원문의 의도와 맥락을 이해하고 영어로 자연스럽게 표현
- Front Matter 수정: title, description을 영어로 번역, lang: en 속성 추가, ref 속성 추가
- 카테고리/태그 영어 매핑
"""

import re
import os
import sys
from pathlib import Path
from typing import Dict, Optional
from google import genai

# 프로젝트 루트를 Python 경로에 추가
current_file = Path(__file__)
project_root = current_file.parent.parent.parent.parent
sys.path.insert(0, str(project_root / '.github' / 'scripts'))


class TranslatorAgent:
    """번역 에이전트 - 한글 글을 영어로 번역"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        # 모델은 환경/권한에 따라 가용성이 달라질 수 있으므로 폴백 체인을 둔다
        self.model_candidates = [
            os.getenv("GEMINI_TRANSLATOR_MODEL"),
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash-exp",
            "models/gemini-2.0-flash",
            "models/gemini-flash-latest",
        ]
        self.model_candidates = [m for m in self.model_candidates if m]
        self.model = self.model_candidates[0]
        
        # 카테고리/태그 영어 매핑
        self.category_map = {
            'dev': 'dev',
            'study': 'study',
            'daily': 'daily',
            'document': 'document',
        }
        
        self.tag_map = {
            'VHDL': 'VHDL',
            'FPGA': 'FPGA',
            'Vivado': 'Vivado',
            'Synthesis': 'Synthesis',
            '오류': 'Error',
            '문법': 'Syntax',
            '레퍼런스': 'Reference',
            '설계': 'Design',
            '아키텍처': 'Architecture',
            '회고': 'Retrospective',
            '일상': 'Daily Life',
            '일기': 'Diary',
        }
    
    def translate_post(self, korean_post_path: Path, ref_id: str) -> Optional[Dict]:
        """
        한글 마크다운 포스트를 영어로 번역한다.
        
        Args:
            korean_post_path: 한글 포스트 파일 경로
            ref_id: 한글/영문 글을 연결하는 고유 ID
            
        Returns:
            Dict: 번역된 콘텐츠 (title, content, front_matter 등) 또는 None
        """
        try:
            # 한글 포스트 읽기
            korean_content = korean_post_path.read_text(encoding='utf-8')
            
            # Front Matter와 본문 분리
            front_matter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', korean_content, re.DOTALL)
            if not front_matter_match:
                print(f"[ERROR] Front Matter를 찾을 수 없습니다: {korean_post_path}")
                return None
            
            front_matter_text = front_matter_match.group(1)
            body_text = front_matter_match.group(2)
            
            # Front Matter 파싱
            front_matter = self._parse_front_matter(front_matter_text)
            
            # 번역 프롬프트 생성
            translation_prompt = self._create_translation_prompt(
                title=front_matter.get('title', ''),
                body=body_text,
                category=front_matter.get('category', 'document'),
                tags=front_matter.get('tags', [])
            )
            
            # Gemini API로 번역 (의역 수행)
            print(f"[번역] 제목 및 본문 의역(Paraphrasing) 중...")
            response = self.client.models.generate_content(
                model=self.model,
                contents=translation_prompt
            )
            
            if not response or not response.text:
                print("[ERROR] 번역 응답이 비어있습니다.")
                return None
            
            translated_text = response.text.strip()
            
            # 번역된 텍스트에서 Front Matter와 본문 분리
            translated_match = re.match(r'^---\n(.*?)\n---\n(.*)$', translated_text, re.DOTALL)
            if not translated_match:
                # Front Matter가 없으면 본문만 번역된 것으로 간주
                translated_body = translated_text
                # Front Matter는 별도로 생성
                translated_front_matter = self._create_english_front_matter(
                    front_matter, ref_id, translated_body
                )
            else:
                translated_front_matter_text = translated_match.group(1)
                translated_body = translated_match.group(2)
                translated_front_matter = self._parse_front_matter(translated_front_matter_text)
                # ref_id 추가
                translated_front_matter['ref'] = ref_id
                translated_front_matter['lang'] = 'en'
            
            # 영어 제목이 없으면 본문에서 추출 시도
            if 'title' not in translated_front_matter or not translated_front_matter['title']:
                # 본문의 첫 번째 헤더를 제목으로 사용하거나 원본 제목을 번역
                title_prompt = f"Translate the following Korean title to English (technical blog style): {front_matter.get('title', '')}"
                title_response = self.client.models.generate_content(
                    model=self.model,
                    contents=title_prompt
                )
                if title_response and title_response.text:
                    translated_front_matter['title'] = title_response.text.strip().strip('"').strip("'")
                else:
                    translated_front_matter['title'] = front_matter.get('title', 'Untitled')
            
            return {
                'title': translated_front_matter.get('title', ''),
                'content': translated_body,
                'front_matter': translated_front_matter,
                'category': self.category_map.get(front_matter.get('category', 'document'), 'document'),
                'tags': [self.tag_map.get(tag, tag) for tag in front_matter.get('tags', [])],
                'date': front_matter.get('date', ''),
                'author': front_matter.get('author', 'rldhkstopic'),
            }
            
        except Exception as e:
            print(f"[ERROR] 번역 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_front_matter(self, front_matter_text: str) -> Dict:
        """Front Matter 텍스트를 딕셔너리로 파싱"""
        front_matter = {}
        for line in front_matter_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # key: value 형식 파싱
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # 따옴표 제거
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # 배열 처리 (tags: [tag1, tag2])
                if value.startswith('[') and value.endswith(']'):
                    value = value[1:-1]
                    tags = [t.strip().strip('"').strip("'") for t in value.split(',') if t.strip()]
                    front_matter[key] = tags
                else:
                    front_matter[key] = value
        
        return front_matter
    
    def _create_translation_prompt(self, title: str, body: str, category: str, tags: list) -> str:
        """번역 프롬프트 생성 - 기술 블로그에 적합한 영어 번역"""
        return f"""You are a technical translator specializing in translating Korean technical blog posts into professional English suitable for a technical blog audience.

**Your Role:**
Translate the following Korean technical blog post into English that maintains the analytical, fact-focused tone typical of technical blogs. The translation should read as if written natively in English by a technical writer.

**Translation Guidelines:**

1. **Tone & Style:**
   - Use clear, direct, and analytical English (similar to how Korean uses "~다." ending)
   - Maintain a professional, fact-focused tone without emotional expressions
   - Avoid greetings, conclusions, or transitional phrases like "In conclusion", "To summarize"
   - Keep the logical flow: [Situation/Problem] -> [Analysis/Approach] -> [Insights/Results]

2. **Technical Content Preservation:**
   - DO NOT translate code blocks (```...```) - keep them exactly as-is
   - DO NOT translate inline code (`...`) - keep them exactly as-is
   - DO NOT translate code comments - keep them exactly as-is
   - Preserve technical terms that are standard in English (VHDL, FPGA, Vivado, BRAM, API, etc.)
   - Keep technical abbreviations and acronyms as-is

3. **Format Preservation:**
   - Maintain all Markdown formatting (headers, lists, links, blockquotes, etc.)
   - Preserve the exact structure and hierarchy
   - Keep footnote references ([^n]) and reference sections intact
   - Maintain code block language identifiers

4. **Natural English Translation (Paraphrasing):**
   - **IMPORTANT: Use paraphrasing, not literal word-for-word translation**
   - Understand the meaning and intent, then express it naturally in English
   - Restructure sentences if needed to match natural English expression patterns
   - Use appropriate technical terminology in English
   - Ensure the translation reads smoothly as if written natively in English
   - Maintain the author's analytical perspective and logical flow
   - Avoid awkward literal translations that sound like machine translation

5. **Category-Specific Considerations:**
   - **dev**: Focus on technical accuracy, preserve code examples, maintain problem-solving narrative
   - **document**: Maintain analytical tone, preserve data references, keep expert quotes
   - **study**: Keep educational structure, preserve concept explanations
   - **daily**: If personal experience, maintain first-person perspective naturally

**Original Korean Post:**

Title: {title}

Category: {category}
Tags: {', '.join(tags) if tags else 'None'}

Body:
{body}

**Output Format:**
Provide the translated content in the same Markdown format, starting with Front Matter:

---
layout: post
title: "[Translated English Title]"
date: [same date]
author: rldhkstopic
category: {category}
tags: [translated tags]
lang: en
ref: [will be added separately]
---

[Translated body content here - maintain exact Markdown structure]
"""
    
    def _create_english_front_matter(self, korean_front_matter: Dict, ref_id: str, translated_body: str) -> Dict:
        """영어 Front Matter 생성"""
        # 제목 번역
        title = korean_front_matter.get('title', '')
        if title:
            title_prompt = f"Translate this Korean technical blog title to English: {title}"
            try:
                title_response = self.client.models.generate_content(
                    model=self.model,
                    contents=title_prompt
                )
                if title_response and title_response.text:
                    title = title_response.text.strip().strip('"').strip("'")
            except:
                pass
        
        # Front Matter 생성
        english_front_matter = {
            'layout': 'post',
            'title': title or 'Untitled',
            'date': korean_front_matter.get('date', ''),
            'author': korean_front_matter.get('author', 'rldhkstopic'),
            'category': self.category_map.get(korean_front_matter.get('category', 'document'), 'document'),
            'lang': 'en',
            'ref': ref_id,
            'views': korean_front_matter.get('views', 0),
        }
        
        # 태그 번역
        tags = korean_front_matter.get('tags', [])
        if tags:
            english_tags = []
            for tag in tags:
                english_tag = self.tag_map.get(tag, tag)
                # 태그가 한글이면 번역 시도
                if re.search(r'[가-힣]', tag):
                    tag_prompt = f"Translate this Korean tag to English (keep it short, one or two words): {tag}"
                    try:
                        tag_response = self.client.models.generate_content(
                            model=self.model,
                            contents=tag_prompt
                        )
                        if tag_response and tag_response.text:
                            english_tag = tag_response.text.strip().strip('"').strip("'")
                    except:
                        pass
                english_tags.append(english_tag)
            english_front_matter['tags'] = english_tags
        
        # 기타 필드 복사
        for key in ['subcategory', 'series', 'series_order', 'permalink']:
            if key in korean_front_matter:
                english_front_matter[key] = korean_front_matter[key]
        
        return english_front_matter


def generate_ref_id(post_path: Path) -> str:
    """포스트 파일명에서 고유 ref ID 생성"""
    # 파일명에서 날짜 제거하고 나머지를 해시로 변환
    filename = post_path.stem
    # 날짜 부분 제거 (YYYY-MM-DD-)
    if re.match(r'^\d{4}-\d{2}-\d{2}-', filename):
        filename = filename[11:]  # 날짜 부분 제거
    
    # 간단한 해시 생성 (파일명 기반)
    import hashlib
    ref_id = hashlib.md5(filename.encode('utf-8')).hexdigest()[:12]
    return f"post-{ref_id}"
