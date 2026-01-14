"""
포스트 생성 에이전트
검증된 콘텐츠를 Jekyll 포스트 형식의 마크다운 파일로 생성한다.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class PostCreatorAgent:
    """포스트 파일 생성 에이전트"""
    
    def __init__(self):
        # 프로젝트 루트 찾기
        # auto_post.py는 automation/scripts/에 있고, 프로젝트 루트는 그 위 2단계
        current_file = Path(__file__)
        # agents/post_creator.py -> scripts/agents/ -> scripts/ -> automation/ -> 프로젝트 루트
        project_root = current_file.parent.parent.parent.parent
        self.posts_dir = project_root / '_posts'
        self.posts_dir.mkdir(parents=True, exist_ok=True)
    
    def create_post(self, content: Dict, topic: Dict) -> Optional[str]:
        """
        콘텐츠를 Jekyll 포스트 파일로 생성한다.
        
        Args:
            content: 생성된 콘텐츠
            topic: 원본 주제 정보
            
        Returns:
            str: 생성된 파일 경로 (성공 시), None (실패 시)
        """
        try:
            # 파일명 생성
            date_str = content.get('date', datetime.now().strftime('%Y-%m-%d'))
            title_slug = self._create_slug(content.get('title', 'untitled'))
            filename = f"{date_str}-{title_slug}.md"
            filepath = self.posts_dir / filename
            
            # 이미 존재하는 파일인지 확인
            if filepath.exists():
                # 같은 날짜에 같은 제목이면 스킵
                print(f"[WARN] 파일이 이미 존재합니다: {filename}")
                return None
            
            # Front Matter 생성
            front_matter = self._create_front_matter(content)
            
            # 본문 처리
            body = content.get('content', '').strip()
            
            # References 섹션이 없으면 추가
            if '[^' in body and '## References' not in body:
                body += '\n\n## References\n\n'
                # 간단한 참조 추가 (실제로는 더 정교한 파싱 필요)
                if topic.get('source_url'):
                    body += f"[^1]: {topic['source_url']}\n"
            
            # 전체 마크다운 생성
            markdown_content = front_matter + '\n\n' + body
            
            # 파일 저장 (UTF-8 인코딩 명시)
            try:
                filepath.write_text(markdown_content, encoding='utf-8')
            except Exception as e:
                print(f"[ERROR] 파일 저장 오류: {str(e)}")
                # 대체 방법 시도
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
            
            # 상대 경로 반환 (_posts/파일명.md)
            return str(filepath.relative_to(self.posts_dir.parent))
            
        except Exception as e:
            print(f"❌ 포스트 생성 오류: {str(e)}")
            return None
    
    def _create_slug(self, title: str) -> str:
        """제목을 파일명 슬러그로 변환"""
        # 한글은 유지, 특수문자는 하이픈으로
        slug = re.sub(r'[^\w\s가-힣-]', '', title)
        # 공백을 하이픈으로
        slug = re.sub(r'\s+', '-', slug)
        # 연속된 하이픈 제거
        slug = re.sub(r'-+', '-', slug)
        # 앞뒤 하이픈 제거
        slug = slug.strip('-')
        
        return slug
    
    def _create_front_matter(self, content: Dict) -> str:
        """Jekyll Front Matter 생성"""
        date_str = content.get('date', datetime.now().strftime('%Y-%m-%d'))
        time_str = datetime.now().strftime('%H:%M:%S')
        
        # f-string 안에서 백슬래시를 사용할 수 없으므로 미리 처리
        title = content.get('title', '').replace('"', '\\"')
        author = content.get('author', 'rldhkstopic')
        category = content.get('category', 'document')
        
        front_matter = f"""---
layout: post
title: "{title}"
date: {date_str} {time_str} +0900
author: {author}
category: {category}"""
        
        # 태그 추가
        tags = content.get('tags', [])
        if tags:
            tags_str = ', '.join([f'"{tag}"' for tag in tags])
            front_matter += f"\ntags: [{tags_str}]"
        
        front_matter += "\nviews: 0\n---"
        
        return front_matter

