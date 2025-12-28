"""
작성 에이전트
분석 결과를 바탕으로 최종 블로그 포스트를 작성한다.
스타일 가이드를 준수하여 고품질의 글을 생성한다.
"""

import os
from typing import Dict, Optional
from google import genai


class WriterAgent:
    """작성 에이전트 - 최종 글 작성"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "models/gemini-2.0-flash"
    
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
        
        writing_prompt = f"""{system_prompt}

**주제 정보:**
- 제목: {topic.get('title', '')}
- 설명: {topic.get('description', '')}
- 카테고리: {topic.get('category', 'document')}
- 태그: {', '.join(topic.get('tags', []))}

**조사 결과:**
{research_data.get('raw_research', '')[:1500]}

**분석 인사이트:**
{analysis_data.get('insights', '')[:1000]}

**작성 요청:**
위 정보를 바탕으로 전문적이고 깊이 있는 블로그 포스트를 작성해주세요.

**구조:**
1. 도입부: 상황/동기 → 액션 → 환경/제약사항
2. 본문: 
   - 핵심 사실 및 데이터 제시
   - 전문가 의견 인용 (blockquote 형식)
   - 분석 및 해석
   - 사례 및 비교
3. 마무리: 작업 완료 상태나 다음 단계 메모

**참조 처리:**
- 외부 자료 언급 시 [^n] 형식 사용
- 글 마지막에 ## References 섹션 추가
- 출처 링크 포함

**주의사항:**
- "~다."로 끝나는 건조한 문체
- 감정 배제, 이모지 금지
- 데이터와 사실 중심
- 최소 1200자 이상 작성
"""
        
        try:
            print(f"  [작성] 블로그 포스트 작성 중...")
            response = self.client.models.generate_content(
                model=self.model,
                contents=writing_prompt
            )
            
            content = response.text
            print(f"  [OK] 작성 완료 ({len(content)}자)")
            
            return content
            
        except Exception as e:
            print(f"  [ERROR] 작성 오류: {str(e)}")
            return ""
    
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
- 이모지 사용 금지

**출력 형식:**
- Front Matter 없이 본문만 작성
- Markdown 형식으로 작성
- 최소 1200자 이상 작성"""

