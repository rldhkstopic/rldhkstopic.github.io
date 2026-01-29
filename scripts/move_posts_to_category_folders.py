#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 _posts_* 디렉터리의 포스트를 _posts/{category}/ 구조로 이동
"""

import re
import shutil
from pathlib import Path
from collections import defaultdict

def main():
    posts_dir = Path("_posts")
    posts_dir.mkdir(exist_ok=True)
    
    # 기존 _posts_* 디렉터리에서 파일 이동
    category_mapping = {
        "_posts_daily": "daily",
        "_posts_dev": "dev",
        "_posts_stock": "stock",
        "_posts_document": "document",
        "_posts_study": "study",
    }
    
    moved_count = 0
    
    for old_dir_name, category in category_mapping.items():
        old_dir = Path(old_dir_name)
        if not old_dir.exists():
            continue
        
        category_dir = posts_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"{old_dir_name} -> _posts/{category}/")
        
        for post_file in old_dir.glob("*.md"):
            dest_path = category_dir / post_file.name
            if dest_path.exists():
                print(f"  [SKIP] 이미 존재: {post_file.name}")
                continue
            
            shutil.move(str(post_file), str(dest_path))
            print(f"  [OK] 이동: {post_file.name}")
            moved_count += 1
    
    # 루트 _posts에 남아있는 파일들도 카테고리별로 분류
    if posts_dir.exists():
        categories = defaultdict(list)
        
        for post_file in posts_dir.glob("*.md"):
            try:
                content = post_file.read_text(encoding="utf-8")
                match = re.search(r'^category:\s*(\S+)', content, re.MULTILINE)
                if match:
                    category = match.group(1)
                else:
                    category = "uncategorized"
                
                categories[category].append(post_file)
            except Exception as e:
                print(f"[WARN] 파일 읽기 실패 ({post_file.name}): {e}")
                continue
        
        for category, files in categories.items():
            if category == "uncategorized":
                continue  # uncategorized는 루트에 유지
            
            category_dir = posts_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            for file in files:
                dest_path = category_dir / file.name
                if dest_path.exists():
                    print(f"  [SKIP] 이미 존재: {file.name}")
                    continue
                
                file.rename(dest_path)
                print(f"  [OK] 이동: {file.name} -> {category}/")
                moved_count += 1
    
    print(f"\n완료! 총 {moved_count}개 파일이 이동되었습니다.")
    print(f"\n주의: Jekyll은 기본적으로 _posts 하위 디렉터리를 인식하지 않을 수 있습니다.")
    print(f"_config.yml에서 collections를 설정하거나 플러그인이 필요할 수 있습니다.")

if __name__ == "__main__":
    main()
