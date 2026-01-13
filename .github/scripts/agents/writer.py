"""
작성 에이전트
분석 결과를 바탕으로 최종 블로그 포스트를 작성한다.
스타일 가이드를 준수하여 고품질의 글을 생성한다.
"""

import io
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from google import genai

# Windows 콘솔에서 한글 출력이 깨지는 문제 완화 (UTF-8 강제)
if sys.platform.startswith("win"):
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        else:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
        else:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    except Exception:
        pass


class WriterAgent:
    """작성 에이전트 - 최종 글 작성"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        # 모델은 환경/권한에 따라 가용성이 달라질 수 있으므로 폴백 체인을 둔다.
        # - 일부 환경에서는 특정 모델이 404/NOT_FOUND로 실패할 수 있다.
        # - 이 경우 다음 후보로 자동 폴백한다.
        self.model_candidates = [
            os.getenv("GEMINI_WRITER_MODEL"),
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash-exp",
            "models/gemini-2.0-flash",
            "models/gemini-flash-latest",
        ]
        self.model_candidates = [m for m in self.model_candidates if m]
        self.model = self.model_candidates[0]
    
    def _is_korean_output(self, text: str) -> bool:
        """
        모델 출력이 한국어 본문으로서 최소 품질을 만족하는지 점검한다.
        
        검증 항목:
        1. 기본 한글 비율 검사 (150자 이상, 20% 이상)
        2. 종결어미 검사 (문장의 50% 이상이 '~다.'로 끝나야 함)
        3. 앞/뒤 분할 검사 (Language Switching 방지)
        """
        if not text:
            return False
        
        # 1. 코드 블록 제거 (한글 비율 왜곡 방지)
        text_wo_code = re.sub(r"```[\s\S]*?```", "", text)

        # 2. 기본 한글 비율 검사 (기준 상향: 150자, 20%)
        hangul_count = len(re.findall(r"[가-힣]", text_wo_code))
        non_ws = len(re.sub(r"\s+", "", text_wo_code))
        
        if non_ws == 0:
            return False
        
        if hangul_count < 150:
            print(f"  [WARN] 한글 수 부족: {hangul_count}자 (최소 150자 필요)")
            return False
        
        hangul_ratio = hangul_count / non_ws
        if hangul_ratio < 0.2:
            print(f"  [WARN] 한글 비율 부족: {hangul_ratio*100:.1f}% (최소 20% 필요)")
            return False

        # 3. 종결어미 검사 (문체 통일성 보장)
        lines = text_wo_code.split('\n')
        valid_sentences = 0
        total_sentences = 0
        
        for line in lines:
            line = line.strip()
            # 짧은 제목이나 빈 줄, 특수문자는 건너뜀
            if len(line) < 10 or line.startswith('#') or line.startswith('-') or line.startswith('*'):
                continue
            
            total_sentences += 1
            # 문장 끝이 '다.'로 끝나는지 정규식 체크 ('다.' 뒤에 각주[1] 등이 올 수도 있음 고려)
            if re.search(r'다\s*(\[.*?\])?\.$', line) or line.endswith('다.'):
                valid_sentences += 1
        
        # 본문 문장 중 50% 이상이 '~다.'로 끝나야 합격
        if total_sentences > 0:
            sentence_ratio = valid_sentences / total_sentences
            if sentence_ratio < 0.5:
                print(f"  [WARN] 문체 검증 실패: '~다.'로 끝나는 문장 비율이 낮음 ({valid_sentences}/{total_sentences}, {sentence_ratio*100:.1f}%)")
                return False

        # 4. 앞/뒤 분할 검사 (Language Switching 방지)
        length = len(text_wo_code)
        if length > 0:
            quarter = max(length // 4, 100)  # 최소 100자 단위
            
            first_part = text_wo_code[:quarter]
            last_part = text_wo_code[-quarter:]
            
            # 끝부분에도 한글이 충분히 있는지 확인
            last_hangul_count = len(re.findall(r"[가-힣]", last_part))
            if last_hangul_count < 20:
                print(f"  [WARN] 후반부 한글 부족 (언어 전환 의심): {last_hangul_count}자")
                return False

        return True

    def write(self, topic: Dict, research_data: Dict, analysis_data: Dict) -> str:
        """
        조사 및 분석 결과를 바탕으로 블로그 포스트를 작성한다.
        3-Tier Agent Pipeline을 사용하여 고품질의 글을 생성한다.
        
        Args:
            topic: 주제 정보
            research_data: 조사 데이터
            analysis_data: 분석 데이터
            
        Returns:
            str: 작성된 블로그 포스트 본문 (Front Matter 제외)
        """
        category = topic.get('category', 'document')
        
        # 조사 및 분석 데이터 정리
        research_text = research_data.get('raw_research', '')[:2000] if research_data.get('raw_research') else ''
        analysis_text = analysis_data.get('insights', '')[:1500] if analysis_data.get('insights') else ''
        
        # Bloomberg 다이제스트는 기존 방식 유지 (특수한 구조 필요)
        if (topic.get("source") == "bloomberg_rss") or (topic.get("type") == "bloomberg_digest"):
            return self._write_bloomberg_digest(topic, research_text, analysis_text)
        
        # Daily 카테고리는 기존 방식 유지 (특수한 문체 필요)
        if category == 'daily':
            return self._write_daily(topic, research_text, analysis_text)
        
        # 일반 글 작성: 3-Tier Pipeline 사용
        return self._write_with_3tier(topic, research_text, analysis_text)
    
    def _write_with_3tier(self, topic: Dict, research_text: str, analysis_text: str) -> str:
        """
        3-Tier Pipeline을 사용한 일반 글 작성
        """
        # 메모 구성: 조사 결과와 분석 인사이트를 합쳐서 초안 메모로 사용
        memo = f"""**주제:**
제목: {topic.get('title', '')}
설명: {topic.get('description', '')}
카테고리: {topic.get('category', 'document')}

**조사 결과:**
{research_text}

**분석 인사이트:**
{analysis_text}
"""
        
        title = topic.get('title', '')
        category = topic.get('category', 'document')
        
        print("\n[3-Tier Pipeline] 글 작성 시작...")
        
        # Step 1: 구성 작가 (The Drafter)
        print("\n[Step 1] 구성 작가: 글의 뼈대와 초안 작성 중...")
        draft = self._draft_with_research(memo, title, research_text, analysis_text)
        if not draft:
            print("  [ERROR] Step 1 실패")
            return ""
        print(f"  [OK] Step 1 완료 ({len(draft)}자)")
        
        # Step 2: 페르소나 에디터 (The Persona)
        print("\n[Step 2] 페르소나 에디터: 말투 리라이팅 중...")
        rewritten = self._rewrite_with_persona(draft)
        if not rewritten:
            print("  [WARN] Step 2 실패, Step 1 결과 사용")
            rewritten = draft
        print(f"  [OK] Step 2 완료 ({len(rewritten)}자)")
        
        # Step 3: 교정 및 포맷팅 (The Polisher) - Front Matter는 제외하고 본문만 반환
        print("\n[Step 3] 교정 및 포맷팅: 최종 검수 중...")
        polished = self._polish_content(rewritten)
        if not polished:
            print("  [WARN] Step 3 실패, Step 2 결과 사용")
            polished = rewritten
        print(f"  [OK] Step 3 완료 ({len(polished)}자)")
        
        # 최종 검증
        if not self._is_korean_output(polished):
            print("  [WARN] 한국어 검증 실패, 하지만 결과 반환")
        
        print("\n[3-Tier Pipeline] 글 작성 완료!")
        return polished
    
    def _write_bloomberg_digest(self, topic: Dict, research_text: str, analysis_text: str) -> str:
        """Bloomberg 다이제스트는 기존 방식 유지"""
        system_prompt = self._get_system_prompt('document')
        base_prompt = self._get_bloomberg_digest_prompt(topic, research_text, analysis_text, system_prompt)
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=base_prompt
            )
            content = (response.text or "").strip()
            content = self._post_process(content)
            return content
        except Exception as e:
            print(f"  [ERROR] Bloomberg 다이제스트 작성 오류: {str(e)}")
            return ""
    
    def _write_daily(self, topic: Dict, research_text: str, analysis_text: str) -> str:
        """Daily 카테고리는 기존 방식 유지"""
        system_prompt = self._get_system_prompt('daily')
        base_prompt = self._get_daily_prompt(topic, research_text, analysis_text, system_prompt)
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=base_prompt
            )
            content = (response.text or "").strip()
            content = self._post_process(content)
            return content
        except Exception as e:
            print(f"  [ERROR] Daily 작성 오류: {str(e)}")
            return ""
    
    def _draft_with_research(self, memo: str, title: str, research_text: str, analysis_text: str) -> str:
        """
        Step 1: 구성 작가 (The Drafter) - 조사 데이터 포함 버전
        입력받은 메모와 조사/분석 데이터를 바탕으로 논리적인 글의 뼈대와 초안 작성.
        """
        prompt = f"""너는 구성 작가야. 팩트와 정보 전달 위주로 서론-본론-결론 구조를 잡아줘.

**입력 메모:**
{memo}

**제목 (참고용):**
{title if title else "(제목 없음)"}

**조사 결과:**
{research_text[:1500]}

**분석 인사이트:**
{analysis_text[:1000]}

**작성 요구사항:**
1. 서론-본론-결론 구조로 논리적인 글의 뼈대를 잡아줘.
2. 팩트와 정보 전달에 집중해줘. 조사 결과와 분석 인사이트를 적절히 활용해줘.
3. 최소 1500자 이상 작성해줘.
4. 모든 문장은 "~다."로 끝나야 해.
5. 이모지는 사용하지 마.
6. Markdown 형식으로 작성해줘 (Front Matter 제외).
7. 전문가 의견은 blockquote 형식으로 인용해줘.
8. 외부 자료는 [^n] 형식으로 참조하고, 마지막에 ## References 섹션을 추가해줘.

**출력:**
Front Matter 없이 본문만 작성해줘."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            content = (response.text or "").strip()
            
            if not content or len(content) < 500:
                print(f"  [WARN] 초안이 너무 짧음: {len(content)}자")
                return ""
            
            return content
        except Exception as e:
            print(f"  [ERROR] Step 1 오류: {str(e)}")
            return ""
    
    def _polish_content(self, content: str) -> str:
        """
        Step 3: 교정 및 포맷팅 (The Polisher) - Front Matter 제외 버전
        최종 문법 검수 및 마크다운 정리 (본문만 반환).
        """
        prompt = f"""너는 교정 및 포맷팅 전문가야.

**작업:**
1. 아래 글의 문법을 검수하고 교정해줘.
2. 현업 개발 용어로 단어 교정해줘.
3. 마크다운(Code block, H2, H3) 정리해줘.
4. "~다." 문체는 유지해줘.
5. 이모지는 제거해줘.

**원본 글:**
{content}

**출력:**
Front Matter 없이 교정된 본문만 작성해줘."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            polished = (response.text or "").strip()
            
            if not polished or len(polished) < 500:
                print(f"  [WARN] 교정 결과가 너무 짧음: {len(polished)}자, 원본 사용")
                polished = content
            
            # 이모지 제거 및 후처리
            polished = self._post_process(polished)
            
            return polished
        except Exception as e:
            print(f"  [ERROR] Step 3 오류: {str(e)}")
            # 오류 시 원본 반환 (이모지 제거만 수행)
            return self._post_process(content)
            # 프롬프트를 더 간단하고 명확하게 구성
            # ⚠️ 매우 중요: 프롬프트 맨 앞에 한국어 작성 지시를 명확히 배치
            # 조사/분석 결과가 영어일 경우를 대비해 한국어로 번역 요청을 명시
            base_prompt = f"""당신은 한국어로만 글을 쓰는 기술 블로그 작가입니다.

**⚠️ 매우 중요: 이 요청에 대한 모든 응답은 반드시 한국어(한글)로만 작성해야 합니다.**

**⚠️ 필수 규칙 (절대 위반 금지):**
1. 모든 응답은 반드시 한국어(한글)로만 작성하세요. 영어 문장은 절대 사용하지 마세요.
2. 영어 단어는 고유명사나 기술 용어(예: "CSV", "API", "Chaos Communication Congress")만 최소한으로 허용합니다.
3. 조사 결과나 분석 인사이트가 영어로 되어 있어도, 반드시 한국어로 번역하여 설명하세요.
4. 영어 제목이나 영어 설명이 있어도, 본문은 반드시 한국어로 작성하세요.
5. 예시:
   - ✅ 올바른 예: "Chaos Communication Congress는 해커 컨퍼런스다."
   - ❌ 잘못된 예: "Chaos Communication Congress is a hacker conference."

**주제:**
제목: {topic.get('title', '')}
설명: {topic.get('description', '')}
카테고리: {topic.get('category', 'document')}

**조사 결과 (아래 영어 내용을 한국어로 번역하여 설명):**
{research_text[:1500]}

**분석 인사이트 (아래 영어 내용을 한국어로 번역하여 설명):**
{analysis_text[:1000]}

**중요:** 위 조사 결과와 분석 인사이트가 영어로 되어 있어도, 반드시 한국어로 번역하여 설명하세요.

**작성 요구사항:**
1. 반드시 한국어(한글)로만 작성하세요. 영어 문장은 절대 사용하지 마세요.
2. 모든 문장은 "~다."로 끝나야 합니다.
3. 최소 1500자 이상 작성하세요.
4. 이모지는 사용하지 마세요.
5. 전문가 의견은 blockquote 형식으로 인용하세요.
6. 외부 자료는 [^n] 형식으로 참조하고, 마지막에 ## References 섹션을 추가하세요.

**[번역 전략]**: 조사 자료가 영어일 경우, 내용을 완전히 이해한 후 **당신의 언어(한국어)로 다시 서술**하십시오. 영어를 그대로 복사해서 붙여넣거나 번역투로 쓰지 마십시오. 영어 원문을 한국어로 자연스럽게 재구성하여 작성하세요.

**[실패 조건]**: 문단 중간에 갑자기 영어가 등장하거나, 코드 설명이 영어로 되어 있으면 작성이 실패한 것으로 간주됩니다. 서론은 한글로 잘 쓰다가 본론부터 영어로 바뀌는 경우도 실패입니다.

{system_prompt}
"""
        
        # 일반 글 작성은 3-Tier Pipeline 사용
        return self._write_with_3tier(topic, research_text, analysis_text)
    
    def _post_process(self, content: str) -> str:
        """생성된 콘텐츠 후처리"""
        # 이모지 제거
        emoji_pattern = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)
        content = emoji_pattern.sub("", content)
        
        # 문장 끝을 "~다."로 통일 (제목/헤더/리스트는 제외)
        lines = content.split('\n')
        processed_lines = []
        for line in lines:
            original_line = line
            line = line.strip()
            if not line:
                processed_lines.append('')
                continue
            
            # 제목/헤더는 건드리지 않음 (#으로 시작)
            if line.startswith('#'):
                processed_lines.append(original_line)
                continue
            
            # 리스트 항목은 건드리지 않음 (-, *, 숫자로 시작)
            if re.match(r'^[-*•]\s+', line) or re.match(r'^\d+[.)]\s+', line):
                processed_lines.append(original_line)
                continue
            
            # "무엇이 새로웠나", "1차 영향 경로", "리스크" 같은 가이드 문구는 건드리지 않음
            if re.search(r'(무엇이 새로웠나|영향 경로|리스크.*관찰 포인트)', line):
                processed_lines.append(original_line)
                continue
            
            # 인용문(blockquote)은 건드리지 않음
            if line.startswith('>'):
                processed_lines.append(original_line)
                continue
            
            # 코드 블록은 건드리지 않음
            if line.startswith('```'):
                processed_lines.append(original_line)
                continue
            
            # 이미 "~다."로 끝나면 그대로
            if line.endswith('다.'):
                processed_lines.append(original_line)
            # 다른 종결어미가 있으면 "~다."로 변경 (간단한 경우만)
            elif line.endswith("요."):
                processed_lines.append(original_line[:-2] + "다.")
            elif line.endswith("어요."):
                processed_lines.append(original_line[:-3] + "다.")
            elif line.endswith('습니다.'):
                processed_lines.append(original_line[:-4] + "다.")
            else:
                # 이미 적절한 종결어미가 있거나, 문장이 아닌 경우 그대로 유지
                # (예: "~이다.", "~했다.", "~였다." 등은 이미 적절함)
                if re.search(r'[다했였임음]$', line) or line.endswith('.') or line.endswith('!'):
                    processed_lines.append(original_line)
                else:
                    # 종결어미가 없는 경우에만 "다." 추가 (하지만 너무 짧은 줄은 제외)
                    if len(line) > 10:
                        processed_lines.append(original_line + "다.")
                    else:
                        processed_lines.append(original_line)
        
        return '\n'.join(processed_lines)

    def _get_bloomberg_digest_prompt(self, topic: Dict, research_text: str, analysis_text: str, system_prompt: str) -> str:
        """Bloomberg 전일 뉴스 다이제스트 전용 프롬프트 생성"""
        title = topic.get("title", "")
        desc = topic.get("description", "")
        
        # 프롬프트 파일 읽기
        prompt_file = Path(__file__).parent.parent / "prompts" / "bloomberg_daily_digest.md"
        base_prompt = ""
        if prompt_file.exists():
            base_prompt = prompt_file.read_text(encoding="utf-8")
        else:
            # 폴백: 기본 프롬프트
            base_prompt = """너는 여러 경제 뉴스 소스에서 수집된 전일(한국시간 기준) 뉴스 항목을 바탕으로, 한국어 분석 글을 작성하는 현업 애널리스트/리서처다."""
        
        return f"""{base_prompt}

**⚠️ 매우 중요: 모든 출력은 반드시 한국어(한글)로만 작성해야 한다.**

**주제:**
제목: {title}
설명: {desc}

**입력 데이터(전일 여러 경제 뉴스 소스 수집 결과):**
{research_text}

**분석 인사이트(참고용, 필요 시 재구성):**
{analysis_text}

**작성 요구사항(절대 위반 금지):**
1. 모든 문장은 "~다."로 끝나는 건조한 평서문을 사용한다.
2. **불릿 리스트 항목 끝에 "다"를 붙이지 않는다.** 예: "미국 국내 정치 및 사회적 갈등" (O), "미국 국내 정치 및 사회적 갈등다" (X)
3. 이모지, 인사말, 과장 표현을 사용하지 않는다.
4. RSS 제목/요약/링크를 바탕으로만 작성한다. 기사 전문을 재현하거나 장문 인용하지 않는다.
5. "전일(한국시간 기준)" 범위의 뉴스만 다룬다.
6. **최소 3000자 이상의 상세하고 직관적인 분석**을 작성한다.
7. 각 테마별로 최소 500자 이상의 상세한 분석을 제공한다.
8. 인용구에는 "리서치 노트(작성자)" 같은 형식화된 출처를 붙이지 않는다. 필요시 간단한 출처만 명시한다.
9. References 섹션의 링크 끝에 "다"를 붙이지 않는다.
10. 반드시 아래 구조를 따른다.

**필수 구조:**
### 전일 이슈 개요
- 4~8개 테마로 묶어 정리한다.
- 각 테마마다 2~5개 항목을 불릿으로 요약한다(제목을 그대로 길게 복사하지 말고 의미 중심으로 바꿔 쓴다).
- **불릿 항목은 명사형이나 짧은 구로 작성하며, 끝에 "다"를 붙이지 않는다.**

### 테마별 해석(전문가 소견)
- 각 테마마다 '영향 경로', '리스크', '관찰 포인트'를 포함한다.
- 각 테마마다 배경 설명과 맥락을 충분히 제공한다.
- 각 테마별로 최소 500자 이상의 상세한 분석을 제공한다.
- **절대 금지: "무엇이 새로웠나다.", "1차 영향 경로다.", "리스크다." 같은 형식으로 작성하지 않는다. 자연스러운 문장으로 서술한다.**
- 전문가 코멘트는 선택사항이며, 포함할 경우 아래 형식을 사용한다(리서치 노트 같은 형식화된 표현 사용 금지):
  > "코멘트 문장"
  > — *간단한 출처*

### 체크리스트(다음 거래일 관찰 포인트)
- 5~10개 항목을 짧게 정리한다.
- 불릿 항목이므로 끝에 "다"를 붙이지 않는다.

## References
- 입력 데이터에 포함된 링크를 `[^n]` 각주로 정리한다.
- 각 링크 끝에 "다"를 붙이지 않는다.

{system_prompt}
"""
    
    def _get_daily_prompt(self, topic: Dict, research_text: str, analysis_text: str, system_prompt: str) -> str:
        """Daily 카테고리 전용 프롬프트 생성"""
        return f"""당신은 블로거의 개인적인 경험을 자연스럽고 편안하게 기록하는 일기 작가입니다.

**⚠️ 매우 중요: 이 요청에 대한 모든 응답은 반드시 한국어(한글)로만 작성해야 합니다.**

**주제:**
제목: {topic.get('title', '')}
설명: {topic.get('description', '')}
카테고리: daily (일상/회고)

**참고 자료 (아래 내용을 바탕으로 개인 경험을 서술하세요):**
{research_text[:1500]}

**분석 인사이트 (참고용):**
{analysis_text[:1000]}

**작성 규칙 (Daily 카테고리 특화 - 매우 중요):**

0. **제목 형식 (필수):** 제목은 반드시 "[YYYY-MM-DD] 요약 제목" 형식으로 작성하세요. 요약 제목은 일기 내용의 핵심을 10-20자 내외로 간결하게 표현하세요.
   - ✅ 좋은 예: "[2026-01-09] 야근 후 무거운 아침과 선임의 조언"
   - ✅ 좋은 예: "[2026-01-09] 당황스러운 질문과 깨달음"
   - ❌ 나쁜 예: "2026년 01월 09일 일기"
   - ❌ 나쁜 예: "[2026-01-09] 일기"

1. **1인칭 시점 유지:** '나', '내가', '나는', '내 생각에는' 등 개인의 관점에서 서술하세요. 3인칭 관찰자 시점("분석한다", "논한다")은 절대 사용하지 마세요.

2. **자연스러운 구어체 문체 (가장 중요):**
   - "~다." 문체보다는 "~했다", "~였다", "~했었다" 같은 자연스러운 과거형을 주로 사용하세요.
   - "~했음", "~했었는데", "~했더니", "~해서" 같은 구어체 어미를 자연스럽게 사용하세요.
   - 짧고 간결한 문장을 선호하세요. 길고 복잡한 문장은 피하세요.
   - 친구에게 말하거나 일기장에 쓰는 듯한 편안하고 자연스러운 톤을 유지하세요.
   - ✅ 좋은 예: "어제 10시까지 야근해서 그런지 아침에 몸이 무거웠다. 9시 반쯤 되어서야 집에서 출발했다."
   - ❌ 나쁜 예: "어제 10시까지 야근한 결과, 아침에 몸이 무거웠음을 확인했다. 9시 반이 되어서야 집에서 출발할 수 있었다."

3. **감정 묘사 필수:** 단순히 사실만 나열하지 말고, 그때 느꼈던 감정(기쁨, 당황, 후회, 짜증, 놀라움, 불편함 등)을 구체적으로 적으세요.

4. **현장감:** 뉴스 기사 같은 말투("~했다고 한다", "~라고 전해진다")를 피하고, 일기장이나 친구에게 말하는 듯한 문체를 사용하세요.

5. **구체적인 묘사:** "대중교통 시스템 마비" 같은 추상적 표현 대신, "지하철역까지 가는 데만 30분이 걸려서 발이 퉁퉁 부었다"는 식의 구체적인 묘사를 사용하세요.

6. **구조:** [상황(어디서 무엇을 겪었나)] -> [행동(무슨 일이 있었고 어떻게 했나)] -> [회고(무엇을 느꼈고 다음엔 어떻게 할 것인가)]

7. **민감 정보 필터링 (필수):**
   - **실명 제거**: 사람 이름은 "A 선임", "B 선임", "수석님", "팀원" 등으로 일반화하세요.
   - **회사/프로젝트명 일반화**: 구체적인 회사명이나 프로젝트명은 일반적인 표현으로 변경하세요.
   - **업무 세부사항 완화**: 민감한 업무 내용은 핵심만 남기고 구체적인 수치나 명칭은 생략하세요.
   - ✅ 좋은 예: "수석님께 하드웨어 조립체 견적 관련해서 여쭤봤다"
   - ❌ 나쁜 예: "김수석님께 포선조립체 견적 관련해서 여쭤봤다" (실명 포함)

8. **최소 1500자 이상 작성하세요.**

9. **이모지는 사용하지 마세요.**

**금지 사항:**
- "본고는", "분석한다", "시사한다", "논한다", "~임을 확인했다", "~인 것으로 보인다" 같은 딱딱한 논문조/보고서조 표현 절대 금지
- 3인칭 관찰자 시점 절대 금지
- 뉴스 기사나 보고서 같은 객관적 서술 금지
- 감정 없이 팩트만 나열하는 것 금지
- 과도하게 격식있는 문어체 사용 금지

**작성 예시:**
```
어제 10시까지 야근해서 그런지 아침에 몸이 무거웠다. 9시 반쯤 되어서야 집에서 출발했다. 출근하는 내내 어제 일이 머릿속을 맴돌았다. 시스템 확정 짓는 과정에서 질문을 받았는데, 내가 제어하는 모듈인데도 구체적인 내용을 제대로 이해하지 못해 당황했었다. 특히 파일 구조나 제어 방식에 대해 제대로 파악하지 못하고 있었던 게 그대로 드러난 것 같아 마음이 불편했다.
```

{system_prompt}
"""

    def _get_system_prompt(self, category: str = 'document') -> str:
        """시스템 프롬프트 생성"""
        if category == 'daily':
            return """당신은 블로거의 개인적인 경험을 기록하는 에세이 작가입니다.
일기장에 쓰는 것처럼 솔직하고 생생하게 개인의 경험을 서술하세요."""
        
        return """당신은 현업 수석 엔지니어이자, 팩트와 논리를 중시하는 테크니컬 라이터입니다.
주어진 조사 및 분석 결과를 바탕으로 웹페이지에 게시할 고품질의 기술 블로그 포스트를 Markdown 형식으로 작성하십시오.

**⚠️ 매우 중요: 출력 언어는 반드시 한국어(한글)로만 작성하세요. 영어로 작성하면 안 됩니다.**

**문체 규칙:**
- "~다."로 끝나는 건조하고 분석적인 문체 사용
- 감정 배제, 이모지 금지
- "AI가 말했다"가 아니라 "데이터를 분석해 본 결과 ~임이 확인되었다"와 같이 주도적 연구 시점 유지

**구조:**
1. [현상/문제 인식] → 2. [데이터/근거 분석] → 3. [전문가 의견 대조] → 4. [인사이트 도출]

**도입부:**
- 거창한 정의로 시작하지 않음
- 패턴: [상황/동기] -> [액션] -> [환경/제약사항]

**본문:**
- 소제목은 간결하게(명사형) 작성
- 1, 2, 3 번호 매기기 리스트보다는 줄글(Paragraph) 우선
- 섹션 간 연결: 각 섹션이 끝나기 전에 다음 섹션으로 자연스럽게 이어지는 전환 문장 추가

**인덱싱(불릿/번호) 규칙(예외):**
- 불릿(`-`)과 번호(`1.`, `2.`)로 나열하는 항목은 **명사형/구**로 작성한다.
- 리스트 항목 끝에 **`~다.`를 붙이지 않는다.** 필요하면 `:`로 끊어 짧게 쓴다.

**결말:**
- "결론" 섹션을 따로 만들지 않음
- 작업이 끝난 상태나, 다음 단계에 대한 짧은 메모로 툭 던지듯 마무리

**참조:**
- 외부 자료나 데이터의 출처를 언급할 때는 반드시 대괄호 숫자 인덱스 [^n] 사용
- 글의 맨 마지막에 ## References 섹션을 만들고, 모든 링크를 정리
- 형식: [^1]: [문서 제목/웹사이트명](URL) - 간단한 설명

**전문가 의견 인용:**
- 전문가 발언은 반드시 blockquote 형식 사용
- 인용문 아래에 발언 주체 명시
- 예시:
  > "발언 내용"
  > — *발언자 이름 (소속)*

**금지어:**
- "안녕하세요", "반갑습니다", "오늘은 ~를 알아보겠습니다" (인사 생략)
- "결론적으로", "요약하자면", "마지막으로" (접속사 생략)
- "매우", "획기적인", "놀라운" (감정적 형용사 생략)
- 이모지 사용 금지 (절대 사용하지 마세요)

**출력 형식:**
- Front Matter 없이 본문만 작성
- Markdown 형식으로 작성
- 최소 1200자 이상 작성
- 모든 문장은 반드시 "~다."로 끝나야 함"""
    
    # ============================================================
    # 3-Tier Agent Pipeline (로컬 테스트용)
    # ============================================================
    
    def write_with_3tier_pipeline(self, memo: str, title: str = "", category: str = "dev") -> str:
        """
        3단계 파이프라인을 사용하여 블로그 포스트를 작성한다.
        
        Args:
            memo: 작성할 내용에 대한 메모/초안
            title: 포스트 제목 (선택사항)
            category: 카테고리 (기본값: "dev")
            
        Returns:
            str: 완성된 블로그 포스트 (Front Matter 포함)
        """
        print("\n[3-Tier Pipeline] 글 작성 시작...")
        
        # Step 1: 구성 작가 (The Drafter)
        print("\n[Step 1] 구성 작가: 글의 뼈대와 초안 작성 중...")
        draft = self._draft(memo, title)
        if not draft:
            print("  [ERROR] Step 1 실패")
            return ""
        print(f"  [OK] Step 1 완료 ({len(draft)}자)")
        
        # Step 2: 페르소나 에디터 (The Persona)
        print("\n[Step 2] 페르소나 에디터: 말투 리라이팅 중...")
        rewritten = self._rewrite_with_persona(draft)
        if not rewritten:
            print("  [ERROR] Step 2 실패")
            return ""
        print(f"  [OK] Step 2 완료 ({len(rewritten)}자)")
        
        # Step 3: 교정 및 포맷팅 (The Polisher)
        print("\n[Step 3] 교정 및 포맷팅: 최종 검수 및 Front Matter 추가 중...")
        final = self._polish_and_format(rewritten, title, category)
        if not final:
            print("  [ERROR] Step 3 실패")
            return ""
        print(f"  [OK] Step 3 완료 ({len(final)}자)")
        
        print("\n[3-Tier Pipeline] 글 작성 완료!")
        return final
    
    def _draft(self, memo: str, title: str = "") -> str:
        """
        Step 1: 구성 작가 (The Drafter)
        입력받은 메모를 바탕으로 논리적인 글의 뼈대와 초안 작성.
        """
        prompt = f"""너는 구성 작가야. 팩트와 정보 전달 위주로 서론-본론-결론 구조를 잡아줘.

**입력 메모:**
{memo}

**제목 (참고용):**
{title if title else "(제목 없음)"}

**작성 요구사항:**
1. 서론-본론-결론 구조로 논리적인 글의 뼈대를 잡아줘.
2. 팩트와 정보 전달에 집중해줘.
3. 최소 1500자 이상 작성해줘.
4. 모든 문장은 "~다."로 끝나야 해.
5. 이모지는 사용하지 마.
6. Markdown 형식으로 작성해줘 (Front Matter 제외).

**출력:**
Front Matter 없이 본문만 작성해줘."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            content = (response.text or "").strip()
            
            if not content or len(content) < 500:
                print(f"  [WARN] 초안이 너무 짧음: {len(content)}자")
                return ""
            
            return content
        except Exception as e:
            print(f"  [ERROR] Step 1 오류: {str(e)}")
            return ""
    
    def _rewrite_with_persona(self, draft: str) -> str:
        """
        Step 2: 페르소나 에디터 (The Persona)
        Step 1의 글을 '특정 말투'로 리라이팅(Rewriting).
        """
        prompt = f"""너는 10년 차 임베디드 시스템 엔지니어이자 시니컬한 기술 블로거다.

**시스템 지시:**
- 절대 '습니다/합니다' 체를 쓰지 마. '음/함' 체나 자연스러운 구어체를 섞어 써. (예: "이건 좀 아닌 듯.", "결국 해결함.")
- "소개합니다", "알아보겠습니다" 같은 전형적인 블로그 멘트 삭제.
- 개발자의 '냉소적인 위트'를 섞어서 문장 호흡을 짧게 끊어쳐.
- "~다." 문체는 유지하되, 더 자연스럽고 구어체 느낌으로 바꿔줘.

**원본 초안:**
{draft}

**작업:**
위 초안을 위의 말투로 리라이팅해줘. 내용은 유지하되, 말투만 바꿔줘.

**출력:**
Front Matter 없이 본문만 작성해줘."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            content = (response.text or "").strip()
            
            if not content or len(content) < 500:
                print(f"  [WARN] 리라이팅 결과가 너무 짧음: {len(content)}자")
                return draft  # 실패 시 원본 반환
            
            return content
        except Exception as e:
            print(f"  [ERROR] Step 2 오류: {str(e)}")
            return draft  # 실패 시 원본 반환
    
    def _polish_and_format(self, content: str, title: str = "", category: str = "dev") -> str:
        """
        Step 3: 교정 및 포맷팅 (The Polisher)
        최종 문법 검수 및 Jekyll Front Matter 추가.
        """
        # 제목이 없으면 첫 번째 헤딩에서 추출 시도
        if not title:
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            if not title:
                title = "Untitled Post"
        
        # 날짜 생성
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S +0900")
        date_short = now.strftime("%Y-%m-%d")
        
        # 파일명 생성 (제목에서)
        filename = re.sub(r'[^\w\s-]', '', title)
        filename = re.sub(r'[-\s]+', '-', filename)
        filename = f"{date_short}-{filename}.md"
        
        prompt = f"""너는 교정 및 포맷팅 전문가야.

**작업:**
1. 아래 글의 문법을 검수하고 교정해줘.
2. 현업 개발 용어로 단어 교정해줘.
3. 마크다운(Code block, H2, H3) 정리해줘.
4. "~다." 문체는 유지해줘.

**원본 글:**
{content}

**출력:**
Front Matter 없이 교정된 본문만 작성해줘."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            polished = (response.text or "").strip()
            
            if not polished or len(polished) < 500:
                print(f"  [WARN] 교정 결과가 너무 짧음: {len(polished)}자, 원본 사용")
                polished = content
            
            # Front Matter 생성
            front_matter = f"""---
layout: post
title: "{title}"
date: {date_str}
author: rldhkstopic
category: {category}
tags: []
views: 0
---

"""
            
            return front_matter + polished
        except Exception as e:
            print(f"  [ERROR] Step 3 오류: {str(e)}")
            # 오류 시 Front Matter만 추가
            front_matter = f"""---
layout: post
title: "{title}"
date: {date_str}
author: rldhkstopic
category: {category}
tags: []
views: 0
---

"""
            return front_matter + content

