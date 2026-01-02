#!/usr/bin/env python3
"""
로컬 테스트용 스크립트
환경 변수로 GEMINI_API_KEY를 설정하고 실행하세요.
예: set GEMINI_API_KEY=your_key (Windows) 또는 export GEMINI_API_KEY=your_key (Linux/Mac)
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / '.github' / 'scripts'))

# API 키는 환경 변수로 설정해야 함
# 예: set GEMINI_API_KEY=your_key (Windows) 또는 export GEMINI_API_KEY=your_key (Linux/Mac)
# ⚠️ 보안: API 키를 코드에 하드코딩하지 마세요!

# 메인 스크립트 실행
from auto_post import main

if __name__ == '__main__':
    main()

