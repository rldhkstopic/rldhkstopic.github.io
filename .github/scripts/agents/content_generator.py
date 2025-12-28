"""
콘텐츠 생성 에이전트
Google Gemini API를 사용하여 블로그 포스트 콘텐츠를 생성한다.
"""

import os
from typing import Dict, Optional
from google import genai


class ContentGeneratorAgent:
    """콘텐츠 생성 에이전트"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-1.5-flash"  # 빠르고 비용 효율적
        print(f"✅ Gemini 클라이언트 초기화 완료 (모델: {self.model_name})")
    
    def generate_content(self, topic: Dict) -> Optional[Dict]:
        """
        주제를 바탕으로 블로그 포스트 콘텐츠를 생성한다.
        
        Args:
            topic: 주제 정보 (title, description, category, tags 등)
            
        Returns:
            Dict: 생성된 콘텐츠 (title, content, category, tags, date 등)
        """
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_user_prompt(topic)
        
        # Gemini는 system instruction과 user prompt를 합쳐서 전달
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            # 새로운 SDK 사용
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config={
                    'temperature': 0.7,
                    'max_output_tokens': 3000,
                }
            )
            
            content_text = response.text
            
            # 생성된 콘텐츠 파싱
            parsed_content = self._parse_content(content_text, topic)
            
            return parsed_content
            
        except Exception as e:
            print(f"❌ 콘텐츠 생성 오류: {str(e)}")
            return None
    
    def _get_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        return """당신은 현업 수석 엔지니어이자, 팩트와 논리를 중시하는 테크니컬 라이터입니다. 
주어지는 주제를 바탕으로 웹페이지에 게시할 고품질의 기술 블로그 포스트를 Markdown 형식으로 작성하십시오.

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

**금지어:**
- "안녕하세요", "반갑습니다", "오늘은 ~를 알아보겠습니다" (인사 생략)
- "결론적으로", "요약하자면", "마지막으로" (접속사 생략)
- "매우", "획기적인", "놀라운" (감정적 형용사 생략)
- 이모지 사용 금지

**출력 형식:**
- Front Matter 없이 본문만 작성
- Markdown 형식으로 작성
- 최소 800자 이상 작성"""
    
    def _build_user_prompt(self, topic: Dict) -> str:
        """사용자 프롬프트 생성"""
        title = topic.get('title', '')
        description = topic.get('description', '')
        category = topic.get('category', 'document')
        tags = topic.get('tags', [])
        
        prompt = f"""다음 주제에 대해 블로그 포스트를 작성해주세요:

**제목:** {title}
**설명:** {description}
**카테고리:** {category}
**태그:** {', '.join(tags) if tags else '없음'}

위 주제에 대해 깊이 있게 분석하고 정리한 블로그 포스트를 작성해주세요. 
실제 데이터와 근거를 바탕으로 작성하고, 가능하면 최신 정보를 포함해주세요."""
        
        if topic.get('source_url'):
            prompt += f"\n\n**참고 링크:** {topic['source_url']}"
        
        return prompt
    
    def _parse_content(self, content_text: str, topic: Dict) -> Dict:
        """생성된 콘텐츠를 파싱하여 구조화"""
        from datetime import datetime
        
        return {
            'title': topic.get('title', ''),
            'content': content_text,
            'category': topic.get('category', 'document'),
            'tags': topic.get('tags', []),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'author': 'rldhkstopic',
            'source': topic.get('source', 'auto'),
            'source_url': topic.get('source_url', '')
        }

