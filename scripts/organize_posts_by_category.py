#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카테고리별로 포스트를 분류하는 스크립트
"""

import re
from pathlib import Path
from collections import defaultdict

def main():
    posts_dir = Path("_posts")
    categories = defaultdict(list)
    
    print("포스트 카테고리 분석 중...")
    
    # 모든 포스트 파일 읽기
    for post_file in posts_dir.glob("*.md"):
        try:
            content = post_file.read_text(encoding="utf-8")
            
            # Front Matter에서 category 추출
            match = re.search(r'^category:\s*(\S+)', content, re.MULTILINE)
            if match:
                category = match.group(1)
            else:
                category = "uncategorized"
            
            categories[category].append(post_file)
        except Exception as e:
            print(f"[WARN] 파일 읽기 실패 ({post_file.name}): {e}")
            continue
    
    print(f"\n카테고리별 포스트 개수:")
    for cat in sorted(categories.keys()):
        print(f"  {cat}: {len(categories[cat])}개")
    
    print(f"\n카테고리별 폴더 생성 및 파일 이동 중...")
    
    for category, files in categories.items():
        category_dir = posts_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        print(f"  생성: {category_dir}")
        
        for file in files:
            dest_path = category_dir / file.name
            file.rename(dest_path)
            print(f"    이동: {file.name} -> {category}/")
    
    print(f"\n완료! 카테고리별로 포스트가 분류되었습니다.")
    print(f"\n주의: Jekyll은 기본적으로 _posts 하위 디렉터리를 인식하지 않을 수 있습니다.")
    print(f"Jekyll 설정(_config.yml)에서 collections를 사용하거나 플러그인이 필요할 수 있습니다.")

if __name__ == "__main__":
    main()
