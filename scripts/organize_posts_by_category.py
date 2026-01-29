#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카테고리별로 포스트를 정리하는 스크립트
Jekyll 컬렉션 디렉터리로 포스트를 이동합니다.
"""

import re
from pathlib import Path
from typing import Dict, List

# 프로젝트 루트
project_root = Path(__file__).parent.parent
posts_dir = project_root / "_posts"

# 카테고리별 컬렉션 디렉터리 매핑
collections = {
    "daily": "_posts_daily",
    "dev": "_posts_dev",
    "study": "_posts_study",
    "document": "_posts_document",
    "stock": "_posts_stock",
}

def extract_category(file_path: Path) -> str:
    """포스트 파일에서 category 추출"""
    try:
        content = file_path.read_text(encoding="utf-8")
        match = re.search(r'category:\s*(\w+)', content)
        if match:
            return match.group(1).lower()
    except Exception as e:
        print(f"[WARN] 파일 읽기 실패 ({file_path.name}): {e}")
    return "document"  # 기본값

def main():
    """메인 함수"""
    print("[INFO] 카테고리별 포스트 정리 시작...")
    
    # 컬렉션 디렉터리 생성
    for category, dir_name in collections.items():
        collection_dir = project_root / dir_name
        collection_dir.mkdir(parents=True, exist_ok=True)
        print(f"[OK] 디렉터리 확인: {dir_name}")
    
    # 포스트 파일 읽기 및 카테고리별로 이동
    moved_count = 0
    skipped_count = 0
    
    for post_file in posts_dir.glob("*.md"):
        category = extract_category(post_file)
        
        if category in collections:
            target_dir = project_root / collections[category]
            target_path = target_dir / post_file.name
            
            if not target_path.exists():
                post_file.rename(target_path)
                print(f"[OK] 이동: {post_file.name} -> {collections[category]}")
                moved_count += 1
            else:
                print(f"[SKIP] 이미 존재: {target_path.name}")
                skipped_count += 1
        else:
            print(f"[WARN] 알 수 없는 카테고리: {category} ({post_file.name})")
            skipped_count += 1
    
    print(f"\n[OK] 정리 완료!")
    print(f"[INFO] 이동: {moved_count}개, 스킵: {skipped_count}개")
    print(f"[INFO] Jekyll 컬렉션 설정이 _config.yml에 추가되었습니다.")

if __name__ == "__main__":
    main()
