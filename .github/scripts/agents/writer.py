"""
작성 에이전트
분석 결과를 바탕으로 최종 블로그 포스트를 작성한다.
스타일 가이드를 준수하여 고품질의 글을 생성한다.
"""

import io
import os
import re
import sys
from pathlib import Path
from typing import Dict
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
        
        Args:
            topic: 주제 정보
            research_data: 조사 데이터
            analysis_data: 분석 데이터
            
        Returns:
            str: 작성된 블로그 포스트 본문
        """
        category = topic.get('category', 'document')
        system_prompt = self._get_system_prompt(category)
        
        # 조사 및 분석 데이터 정리
        research_text = research_data.get('raw_research', '')[:2000] if research_data.get('raw_research') else ''
        analysis_text = analysis_data.get('insights', '')[:1500] if analysis_data.get('insights') else ''
        
        # Bloomberg 다이제스트는 별도 프롬프트 사용 (카테고리보다 우선)
        if (topic.get("source") == "bloomberg_rss") or (topic.get("type") == "bloomberg_digest"):
            base_prompt = self._get_bloomberg_digest_prompt(topic, research_text, analysis_text, system_prompt)
        # Daily 카테고리는 별도의 프롬프트 사용
        elif category == 'daily':
            base_prompt = self._get_daily_prompt(topic, research_text, analysis_text, system_prompt)
        else:
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
        
        try:
            content = ""
            last_error: str | None = None

            # 모델이 비정상 출력(영문/공백 위주)하는 케이스가 있어, 최대 3회까지 재시도한다.
            for attempt in range(1, 4):
                print(f"  [작성] 블로그 포스트 작성 중... (시도 {attempt}/3, 모델: {self.model})")

                writing_prompt = base_prompt
                if attempt >= 2:
                    # 한글 누락/공백 치환 방어를 위해 요구사항을 더 강하게 고정한다.
                    writing_prompt += """

**⚠️ 매우 중요한 추가 제약:**
- 출력은 **반드시 한국어(한글)로만** 작성하세요. 영어로 작성하면 즉시 실패입니다.
- 모든 문장은 한글로 작성하세요. 영어 문장은 절대 사용하지 마세요.
- 고유명사나 기술 용어(예: "CSV", "API", "JSON")만 최소한으로 영어를 허용합니다.
- 본문에서 한국어가 공백으로 대체되거나, 영문/기호/공백 위주로 출력되면 실패로 간주합니다.
- 예시: "CSV 파일을 사용한다" (O), "Use CSV file" (X)
"""

                # API 호출 (모델이 없으면 후보 모델로 폴백)
                try:
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=writing_prompt
                    )
                    content = (response.text or "").strip()
                    
                    # 응답이 비어있거나 너무 짧으면 에러 출력
                    if not content:
                        print(f"  [ERROR] API 응답이 비어있습니다.")
                        continue
                    if len(content) < 100:
                        print(f"  [ERROR] API 응답이 너무 짧습니다: {len(content)}자")
                        print(f"  [DEBUG] 응답 내용: {content}")
                        continue
                    
                    # 디버깅: 생성된 내용의 일부와 한글 통계 출력
                    preview = content[:300] if len(content) > 300 else content
                    hangul_count = len(re.findall(r'[가-힣]', content))
                    text_wo_code = re.sub(r'```[\s\S]*?```', '', content)
                    hangul_count_wo_code = len(re.findall(r'[가-힣]', text_wo_code))
                    non_ws = len(re.sub(r'\s+', '', text_wo_code))
                    hangul_ratio = (hangul_count_wo_code / non_ws * 100) if non_ws > 0 else 0
                    
                    print(f"  [DEBUG] 생성된 내용 미리보기: {preview}...")
                    print(f"  [DEBUG] 전체 길이: {len(content)}자")
                    print(f"  [DEBUG] 한글 수 (전체): {hangul_count}자")
                    print(f"  [DEBUG] 한글 수 (코드 제외): {hangul_count_wo_code}자")
                    print(f"  [DEBUG] 한글 비율 (코드 제외): {hangul_ratio:.1f}%")
                except Exception as e:
                    last_error = str(e)
                    # 모델 미존재/권한 문제(404/NOT_FOUND)면 다음 후보로 폴백한다.
                    err_upper = last_error.upper()
                    if ("404" in err_upper) or ("NOT_FOUND" in err_upper):
                        next_model = None
                        for m in self.model_candidates:
                            if m == self.model:
                                continue
                            next_model = m
                            break
                        if next_model:
                            print(f"  [WARN] 모델 호출 실패(모델 미존재/권한 가능): {self.model} -> {next_model}")
                            self.model = next_model
                            continue
                    print(f"  [ERROR] API 호출 실패: {last_error}")
                    continue

                # 후처리: 이모지 제거 및 문체 개선
                content = self._post_process(content)

                # 디버깅: 생성된 내용 일부 출력
                if attempt == 1:
                    preview = content[:200] if len(content) > 200 else content
                    print(f"  [DEBUG] 생성된 내용 미리보기: {preview}...")
                    text_wo_code = re.sub(r"```[\s\S]*?```", "", content)
                    hangul_count = len(re.findall(r"[가-힣]", text_wo_code))
                    non_ws = len(re.sub(r"\s+", "", text_wo_code))
                    hangul_ratio = (hangul_count / non_ws * 100) if non_ws > 0 else 0
                    print(f"  [DEBUG] 한글 수(코드 제외): {hangul_count}, 한글 비율(코드 제외): {hangul_ratio:.1f}%")

                if len(content.strip()) < 800:
                    print(f"  [WARN] 길이 부족: {len(content.strip())}자")
                    continue
                # 검증 전 상세 통계 출력
                text_wo_code = re.sub(r"```[\s\S]*?```", "", content)
                hangul_count = len(re.findall(r"[가-힣]", text_wo_code))
                non_ws = len(re.sub(r"\s+", "", text_wo_code))
                hangul_ratio = (hangul_count / non_ws * 100) if non_ws > 0 else 0
                
                # 종결어미 통계
                lines = text_wo_code.split('\n')
                valid_sentences = 0
                total_sentences = 0
                for line in lines:
                    line = line.strip()
                    if len(line) < 10 or line.startswith('#') or line.startswith('-') or line.startswith('*'):
                        continue
                    total_sentences += 1
                    if re.search(r'다\s*(\[.*?\])?\.$', line) or line.endswith('다.'):
                        valid_sentences += 1
                sentence_ratio = (valid_sentences / total_sentences * 100) if total_sentences > 0 else 0
                
                print(f"  [DEBUG] 검증 전 통계:")
                print(f"    - 전체 길이: {len(content)}자")
                print(f"    - 한글 수 (코드 제외): {hangul_count}자")
                print(f"    - 한글 비율 (코드 제외): {hangul_ratio:.1f}%")
                print(f"    - '~다.'로 끝나는 문장: {valid_sentences}/{total_sentences} ({sentence_ratio:.1f}%)")
                
                if not self._is_korean_output(content):
                    print(f"  [ERROR] 한국어 검증 실패!")
                    print(f"  [DEBUG] 검증 실패 내용 샘플 (처음 800자):")
                    print(f"    {content[:800]}")
                    if len(content) > 1000:
                        print(f"  [DEBUG] 검증 실패 내용 샘플 (중간 800자):")
                        print(f"    {content[len(content)//2:len(content)//2+800]}")
                    print(f"  [DEBUG] 검증 실패 내용 샘플 (끝 800자):")
                    print(f"    {content[-800:] if len(content) > 800 else content}")
                    
                    # GitHub Actions에서 디버깅을 위해 임시 파일로 저장
                    try:
                        import tempfile
                        temp_dir = Path(tempfile.gettempdir())
                        debug_file = temp_dir / f"failed_content_attempt_{attempt}.txt"
                        debug_file.write_text(content, encoding="utf-8")
                        print(f"  [DEBUG] 검증 실패 내용이 임시 파일에 저장되었습니다: {debug_file}")
                    except Exception as e:
                        print(f"  [WARN] 임시 파일 저장 실패: {e}")
                    
                    continue

                break

            # 1차 시도 실패 시 레거시 fallback(간단 프롬프트)도 수행한다.
            if not content or len(content.strip()) < 800 or not self._is_korean_output(content):
                if last_error:
                    print(f"  [WARN] 1차 작성 실패. 마지막 오류: {last_error}")
                print("  [WARN] 1차 작성 실패. 간단 프롬프트로 재시도한다.")
                content = ""

            # 응답이 비어있거나 너무 짧으면 재시도(레거시 fallback)
            if not content or len(content) < 500:
                print(f"  [WARN] 응답이 너무 짧습니다 ({len(content)}자). 재시도...")
                simple_prompt = f"""다음 주제에 대해 블로그 포스트를 작성해주세요:

**제목:** {topic.get('title', '')}
**설명:** {topic.get('description', '')}

조사 결과:
{research_data.get('raw_research', '')[:1000]}

분석 인사이트:
{analysis_data.get('insights', '')[:500]}

"~다."로 끝나는 건조한 문체로, 최소 1200자 이상 한국어로 작성해주세요. 이모지는 절대 사용하지 마세요."""
                
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=simple_prompt
                )
                content = response.text
            
            # 응답 검증
            if not content or len(content.strip()) < 500:
                print(f"  [WARN] 응답이 너무 짧습니다 ({len(content)}자). 재시도...")
                # 더 간단한 프롬프트로 재시도
                simple_prompt = f"""다음 주제에 대해 완전한 블로그 포스트를 작성해주세요:

제목: {topic.get('title', '')}
설명: {topic.get('description', '')}

조사 결과 요약:
{research_text[:800]}

분석 요약:
{analysis_text[:500]}

**중요:**
- 모든 문장을 완전하게 작성하세요
- "~다."로 끝나는 문체를 사용하세요
- 이모지는 절대 사용하지 마세요
- 최소 1500자 이상 작성하세요
- 한글을 자연스럽게 사용하세요"""
                
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=simple_prompt
                )
                content = response.text
            
            # 후처리: 이모지 제거 및 문체 개선
            content = self._post_process(content)
            
            # 내용 검증
            if len(content.strip()) < 500:
                print(f"  [ERROR] 최종 콘텐츠가 너무 짧습니다 ({len(content)}자)")
                return ""

            if not self._is_korean_output(content):
                print("  [ERROR] 최종 콘텐츠의 한국어 품질 검증에 실패했습니다.")
                return ""
            
            print(f"  [OK] 작성 완료 ({len(content)}자)")
            
            return content
            
        except Exception as e:
            print(f"  [ERROR] 작성 오류: {str(e)}")
            return ""
    
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

        return f"""당신은 한국어 금융/시장 리서치 노트를 작성하는 애널리스트다.

**⚠️ 매우 중요: 모든 출력은 반드시 한국어(한글)로만 작성해야 한다.**

**주제:**
제목: {title}
설명: {desc}

**입력 데이터(전일 Bloomberg RSS 수집 결과):**
{research_text}

**분석 인사이트(참고용, 필요 시 재구성):**
{analysis_text}

**작성 요구사항(절대 위반 금지):**
1. 모든 문장은 "~다."로 끝나는 건조한 평서문을 사용한다.
2. 이모지, 인사말, 과장 표현을 사용하지 않는다.
3. RSS 제목/요약/링크를 바탕으로만 작성한다. 기사 전문을 재현하거나 장문 인용하지 않는다.
4. "전일(한국시간 기준)" 범위의 뉴스만 다룬다.
5. 최소 1800자 이상 작성한다.
6. 반드시 아래 구조를 따른다.

**필수 구조:**
### 전일 이슈 개요
- 4~8개 테마로 묶어 정리한다.
- 각 테마마다 2~5개 항목을 불릿으로 요약한다(제목을 그대로 길게 복사하지 말고 의미 중심으로 바꿔 쓴다).

### 테마별 해석(전문가 소견)
- 각 테마마다 '영향 경로', '리스크', '관찰 포인트'를 포함한다.
- 각 테마마다 아래 형식의 코멘트를 1개 이상 포함한다.
  > "코멘트 문장"
  > — *리서치 노트(작성자)*

### 체크리스트(다음 거래일 관찰 포인트)
- 5~10개 항목을 짧게 정리한다.

## References
- 입력 데이터에 포함된 링크를 `[^n]` 각주로 정리한다.

{system_prompt}
"""
    
    def _get_daily_prompt(self, topic: Dict, research_text: str, analysis_text: str, system_prompt: str) -> str:
        """Daily 카테고리 전용 프롬프트 생성"""
        return f"""당신은 블로거의 개인적인 경험을 기록하는 에세이 작가입니다.

**⚠️ 매우 중요: 이 요청에 대한 모든 응답은 반드시 한국어(한글)로만 작성해야 합니다.**

**주제:**
제목: {topic.get('title', '')}
설명: {topic.get('description', '')}
카테고리: daily (일상/회고)

**참고 자료 (아래 내용을 바탕으로 개인 경험을 서술하세요):**
{research_text[:1500]}

**분석 인사이트 (참고용):**
{analysis_text[:1000]}

**작성 규칙 (Daily 카테고리 특화):**
1. **1인칭 시점 유지:** '나', '내가', '나는', '내 생각에는' 등 개인의 관점에서 서술하세요. 3인칭 관찰자 시점("분석한다", "논한다")은 절대 사용하지 마세요.
2. **감정 묘사 필수:** 단순히 사실만 나열하지 말고, 그때 느꼈던 감정(기쁨, 당황, 후회, 짜증, 놀라움 등)을 구체적으로 적으세요.
3. **현장감:** 뉴스 기사 같은 말투("~했다고 한다", "~라고 전해진다")를 피하고, 일기장이나 친구에게 말하는 듯한 문체("~했다", "~였다", "~했다")를 사용하세요.
4. **구체적인 묘사:** "대중교통 시스템 마비" 같은 추상적 표현 대신, "지하철역까지 가는 데만 30분이 걸려서 발이 퉁퉁 부었다"는 식의 구체적인 묘사를 사용하세요.
5. **구조:** [상황(어디서 무엇을 겪었나)] -> [행동(무슨 일이 있었고 어떻게 했나)] -> [회고(무엇을 느꼈고 다음엔 어떻게 할 것인가)]
6. **문체:** "~다."로 끝나는 문체를 사용하되, 건조하지 않고 개인적인 느낌이 드러나도록 작성하세요.
7. **최소 1500자 이상 작성하세요.**
8. **이모지는 사용하지 마세요.**

**금지 사항:**
- "본고는", "분석한다", "시사한다", "논한다" 같은 딱딱한 논문조 표현 절대 금지
- 3인칭 관찰자 시점 절대 금지
- 뉴스 기사나 보고서 같은 객관적 서술 금지
- 감정 없이 팩트만 나열하는 것 금지

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

