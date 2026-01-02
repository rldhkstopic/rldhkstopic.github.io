"""
연구 에이전트
주제에 대한 심층 조사 및 정보 수집을 담당한다.
Gemini Deep Research를 활용하여 다양한 소스에서 정보를 수집한다.
"""

import os
from typing import Dict, List, Optional
from google import genai


class ResearcherAgent:
    """연구 에이전트 - 정보 수집 및 조사"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        # 일반 조사용 모델 (안정적이고 빠름)
        self.search_model = "models/gemini-2.0-flash"
    
    def research_topic(self, topic: Dict) -> Dict:
        """
        주제에 대한 심층 조사를 수행한다.
        
        Args:
            topic: 주제 정보 (title, description, category, tags 등)
            
        Returns:
            Dict: 조사 결과 (sources, key_findings, data_points, expert_quotes 등)
        """
        title = topic.get('title', '')
        description = topic.get('description', '')
        
        research_prompt = f"""다음 주제에 대해 심층 조사를 수행하고, 결과를 한국어로 정리해주세요:

**주제:** {title}
**설명:** {description}

⚠️ 중요: 모든 조사 결과는 반드시 한국어로 작성하세요.

다음 정보를 수집하고 정리해주세요:

1. **핵심 사실 및 데이터**
   - 최신 통계, 수치, 연구 결과
   - 시장 동향 및 트렌드
   - 기술적 세부사항

2. **전문가 의견 및 인용**
   - 해당 분야 전문가의 발언
   - 연구기관, 기업의 공식 입장
   - 인용 가능한 구체적인 발언

3. **관련 사례 및 사례 연구**
   - 실제 적용 사례
   - 성공/실패 사례
   - 비교 분석

4. **참고 자료 및 출처**
   - 신뢰할 수 있는 출처의 링크
   - 논문, 리포트, 공식 문서
   - 최신 뉴스 및 기사

출력 형식:
- 각 항목을 명확히 구분하여 정리
- 출처는 반드시 URL과 함께 명시
- 데이터는 구체적인 수치와 함께 제시
- 전문가 의견은 직접 인용 형식으로 제공
"""
        
        try:
            print(f"  [연구] 조사 시작...")
            # 일반 모델 사용 (Deep Research는 별도 API 필요)
            # gemini-2.0-flash가 안정적이고 빠름
            response = self.client.models.generate_content(
                model=self.search_model,
                contents=research_prompt
            )
            research_result = response.text
            print(f"  [OK] 조사 완료")
            
            # 조사 결과 파싱
            parsed_result = self._parse_research(research_result, topic)
            
            return parsed_result
            
        except Exception as e:
            print(f"  [ERROR] 조사 오류: {str(e)}")
            return {
                'sources': [],
                'key_findings': [],
                'data_points': [],
                'expert_quotes': [],
                'raw_research': ''
            }
    
    def _parse_research(self, research_text: str, topic: Dict) -> Dict:
        """조사 결과를 구조화하여 파싱"""
        # 간단한 파싱 (실제로는 더 정교한 파싱 필요)
        lines = research_text.split('\n')
        
        sources = []
        key_findings = []
        data_points = []
        expert_quotes = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 섹션 감지
            if '출처' in line or '참고' in line or '링크' in line:
                current_section = 'sources'
            elif '사실' in line or '데이터' in line or '통계' in line:
                current_section = 'findings'
            elif '인용' in line or '의견' in line or '발언' in line:
                current_section = 'quotes'
            
            # URL 추출
            if 'http' in line:
                sources.append(line)
            
            # 데이터 포인트 추출 (숫자 포함)
            if any(char.isdigit() for char in line) and ('%' in line or '억' in line or '만' in line or '원' in line):
                data_points.append(line)
            
            # 인용문 추출
            if line.startswith('"') or line.startswith("'") or '—' in line or ':' in line:
                if len(line) > 20:  # 짧은 인용은 제외
                    expert_quotes.append(line)
        
        return {
            'sources': sources[:10],  # 최대 10개
            'key_findings': key_findings[:20] if key_findings else lines[:20],
            'data_points': data_points[:10],
            'expert_quotes': expert_quotes[:5],
            'raw_research': research_text
        }

