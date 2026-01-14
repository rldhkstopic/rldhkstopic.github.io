"""
분석 에이전트
수집된 정보를 분석하고 인사이트를 도출한다.
데이터를 해석하고 패턴을 찾아내는 역할을 담당한다.
"""

import os
from typing import Dict, Optional
from google import genai


class AnalystAgent:
    """분석 에이전트 - 데이터 분석 및 인사이트 도출"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "models/gemini-2.0-flash"
    
    def analyze(self, research_data: Dict, topic: Dict) -> Dict:
        """
        조사 결과를 분석하고 인사이트를 도출한다.
        
        Args:
            research_data: ResearcherAgent가 수집한 조사 데이터
            topic: 원본 주제 정보
            
        Returns:
            Dict: 분석 결과 (insights, patterns, conclusions 등)
        """
        analysis_prompt = f"""다음 조사 결과를 분석하여 인사이트를 도출해주세요:

**주제:** {topic.get('title', '')}

**수집된 정보:**
{research_data.get('raw_research', '')[:2000]}

**분석 요청사항:**

1. **핵심 인사이트**
   - 데이터에서 발견된 주요 패턴
   - 예상치 못한 발견사항
   - 중요한 트렌드

2. **데이터 해석**
   - 통계 및 수치의 의미
   - 비교 분석 결과
   - 시사점

3. **전문가 의견 종합**
   - 다양한 관점의 통합
   - 합의점과 이견
   - 주류 의견과 소수 의견

4. **결론 및 제안**
   - 분석 결과 요약
   - 향후 전망
   - 실무적 시사점

출력 형식:
- 객관적이고 분석적인 톤 유지
- 데이터 기반 결론 제시
- 감정적 표현 배제
- 구체적이고 실용적인 인사이트 제공
"""
        
        try:
            print(f"  [분석] 데이터 분석 중...")
            response = self.client.models.generate_content(
                model=self.model,
                contents=analysis_prompt
            )
            
            analysis_result = response.text
            
            print(f"  [OK] 분석 완료")
            
            return {
                'insights': analysis_result,
                'key_patterns': self._extract_patterns(analysis_result),
                'conclusions': self._extract_conclusions(analysis_result)
            }
            
        except Exception as e:
            print(f"  [ERROR] 분석 오류: {str(e)}")
            return {
                'insights': '',
                'key_patterns': [],
                'conclusions': []
            }
    
    def _extract_patterns(self, text: str) -> list:
        """텍스트에서 패턴 추출"""
        patterns = []
        lines = text.split('\n')
        for line in lines:
            if '패턴' in line or '트렌드' in line or '경향' in line:
                if len(line.strip()) > 10:
                    patterns.append(line.strip())
        return patterns[:5]
    
    def _extract_conclusions(self, text: str) -> list:
        """텍스트에서 결론 추출"""
        conclusions = []
        lines = text.split('\n')
        for line in lines:
            if '결론' in line or '시사점' in line or '의미' in line:
                if len(line.strip()) > 10:
                    conclusions.append(line.strip())
        return conclusions[:5]

