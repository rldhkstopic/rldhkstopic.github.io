"""
작성 에이전트
분석 결과를 바탕으로 최종 블로그 포스트를 작성한다.
스타일 가이드를 준수하여 고품질의 글을 생성한다.
"""

import os
import re
from typing import Dict, Optional
from google import genai


class WriterAgent:
    """작성 에이전트 - 최종 글 작성"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "models/gemini-2.0-flash"
    
    def _is_korean_output(self, text: str) -> bool:
        """모델 출력이 한국어 본문으로서 최소 품질을 만족하는지 점검한다."""
        if not text:
            return False
        hangul_count = len(re.findall(r'[가-힣]', text))
        if hangul_count < 200:
            return False

        non_ws = len(re.sub(r'\s+', '', text))
        if non_ws == 0:
            return False
        # 한글이 지나치게 낮으면(영문/공백 위주) 실패로 간주
        if hangul_count / non_ws < 0.10:
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
        system_prompt = self._get_system_prompt()
        
        # 조사 및 분석 데이터 정리
        research_text = research_data.get('raw_research', '')[:2000] if research_data.get('raw_research') else ''
        analysis_text = analysis_data.get('insights', '')[:1500] if analysis_data.get('insights') else ''
        
        base_prompt = f"""{system_prompt}

**주제:**
제목: {topic.get('title', '')}
설명: {topic.get('description', '')}
카테고리: {topic.get('category', 'document')}

**조사 결과:**
{research_text}

**분석 인사이트:**
{analysis_text}

**작성 지시사항:**
1. 위 정보를 바탕으로 완전한 문장으로 블로그 포스트를 작성하세요.
2. 모든 문장은 반드시 "~다."로 끝나야 합니다.
3. 한글을 완전하고 자연스럽게 사용하세요.
4. 이모지는 절대 사용하지 마세요.
5. 최소 1500자 이상 작성하세요.
6. 전문가 의견은 blockquote 형식으로 인용하세요.
7. 외부 자료는 [^n] 형식으로 참조하고, 마지막에 ## References 섹션을 추가하세요.
"""
        
        try:
            content = ""

            # 모델이 비정상 출력(영문/공백 위주)하는 케이스가 있어, 최대 3회까지 재시도한다.
            for attempt in range(1, 4):
                print(f"  [작성] 블로그 포스트 작성 중... (시도 {attempt}/3)")

                writing_prompt = base_prompt
                if attempt >= 2:
                    # 한글 누락/공백 치환 방어를 위해 요구사항을 더 강하게 고정한다.
                    writing_prompt += """

**추가 제약(중요):**
- 출력은 반드시 한국어로 작성하되, 고유명사/기술용어(예: LLM, Transformer)만 최소한으로 영어를 허용한다.
- 본문에서 한국어가 공백으로 대체되거나, 영문/기호/공백 위주로 출력되면 실패로 간주한다.
"""

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=writing_prompt
                )
                content = (response.text or "").strip()

                # 후처리: 이모지 제거 및 문체 개선
                content = self._post_process(content)

                if len(content.strip()) < 800:
                    continue
                if not self._is_korean_output(content):
                    continue

                break

            # 최종 실패 처리
            if not content or len(content.strip()) < 800 or not self._is_korean_output(content):
                print("  [ERROR] 한국어 본문 생성에 실패했습니다. (영문/공백 위주 출력 또는 길이 부족)")
                return ""

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
            
            print(f"  [OK] 작성 완료 ({len(content)}자)")
            
            return content
            
        except Exception as e:
            print(f"  [ERROR] 작성 오류: {str(e)}")
            return ""
    
    def _post_process(self, content: str) -> str:
        """생성된 콘텐츠 후처리"""
        # 이모지 제거
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        content = emoji_pattern.sub('', content)
        
        # 문장 끝을 "~다."로 통일 (간단한 후처리)
        lines = content.split('\n')
        processed_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                processed_lines.append('')
                continue
            
            # 이미 "~다."로 끝나면 그대로
            if line.endswith('다.'):
                processed_lines.append(line)
            # 다른 종결어미가 있으면 "~다."로 변경 (간단한 경우만)
            elif line.endswith('요.') or line.endswith('어요.'):
                line = line[:-3] + '다.'
                processed_lines.append(line)
            elif line.endswith('습니다.'):
                line = line[:-5] + '다.'
                processed_lines.append(line)
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _get_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        return """당신은 현업 수석 엔지니어이자, 팩트와 논리를 중시하는 테크니컬 라이터입니다.
주어진 조사 및 분석 결과를 바탕으로 웹페이지에 게시할 고품질의 기술 블로그 포스트를 Markdown 형식으로 작성하십시오.

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

