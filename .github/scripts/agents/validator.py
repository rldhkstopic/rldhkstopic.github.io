"""
검증 에이전트
생성된 콘텐츠가 스타일 가이드를 준수하는지 검증한다.
"""

import re
from typing import Dict, List


class ValidatorAgent:
    """콘텐츠 검증 에이전트"""
    
    def __init__(self):
        self.forbidden_words = [
            '안녕하세요', '반갑습니다', '오늘은', '매우', '획기적인', 
            '놀라운', '결론적으로', '요약하자면', '마지막으로'
        ]
        self.min_content_length = 800
        self.valid_categories = ['daily', 'dev', 'document', 'study']
    
    def validate(self, content: Dict) -> Dict:
        """
        콘텐츠를 검증한다.
        
        Args:
            content: 검증할 콘텐츠 (title, content, category, tags 등)
            
        Returns:
            Dict: 검증 결과 (valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        # 필수 필드 검증
        if not content.get('title') or not content['title'].strip():
            errors.append('제목이 없습니다.')
        
        if not content.get('content') or len(content['content']) < self.min_content_length:
            errors.append(f'본문이 너무 짧습니다 (최소 {self.min_content_length}자 필요).')
        
        # 카테고리 검증
        category = content.get('category', '')
        if category not in self.valid_categories:
            errors.append(f'유효하지 않은 카테고리: {category}')
        
        # 금지어 검증
        content_text = content.get('content', '').lower()
        for word in self.forbidden_words:
            if word in content_text:
                warnings.append(f'금지어 "{word}"가 포함되어 있습니다.')
        
        # 이모지 검증
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
        if emoji_pattern.search(content.get('content', '')):
            warnings.append('이모지가 포함되어 있습니다.')
        
        # 문체 검증 (끝맺음)
        content_lines = content.get('content', '').split('\n')
        sentence_endings = [line.strip()[-1] for line in content_lines if line.strip()]
        if sentence_endings:
            # "~다."로 끝나는 문장 비율 확인
            da_ending_count = sum(1 for ending in sentence_endings if ending == '다')
            if len(sentence_endings) > 0 and da_ending_count / len(sentence_endings) < 0.3:
                warnings.append('문체가 스타일 가이드와 다를 수 있습니다. ("~다."로 끝나는 문장 비율이 낮음)')
        
        # 참조 링크 검증
        if '[^' in content.get('content', '') and '## References' not in content.get('content', ''):
            warnings.append('참조 인덱스([^n])가 있지만 References 섹션이 없습니다.')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

