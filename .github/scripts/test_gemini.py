#!/usr/bin/env python3
"""
Gemini API 테스트 스크립트
사용 가능한 모델 목록을 확인하고 간단한 테스트를 수행한다.
"""

import os
import sys
from google import genai

# API 키 확인
api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyAYXrmMz9eSCgW9JwDTkHaUKH8vFfYMKUs')
if not api_key:
    print("❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
    sys.exit(1)

import sys
import io

# Windows 콘솔 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("=" * 60)
print("Gemini API 테스트")
print("=" * 60)
print(f"API 키: {api_key[:20]}...")
print()

try:
    # 클라이언트 초기화
    print("[1단계] 클라이언트 초기화 중...")
    client = genai.Client(api_key=api_key)
    print("[OK] 클라이언트 초기화 완료")
    print()
    
    # 사용 가능한 모델 목록 확인
    print("[2단계] 사용 가능한 모델 목록 확인 중...")
    try:
        models = client.models.list()
        print("[OK] 모델 목록 조회 성공")
        print("\n사용 가능한 모델:")
        for model in models:
            print(f"  - {model.name}")
            if hasattr(model, 'display_name'):
                print(f"    (Display: {model.display_name})")
        print()
    except Exception as e:
        print(f"[WARN] 모델 목록 조회 실패: {str(e)}")
        print("직접 모델 이름을 시도합니다...")
        print()
    
    # 여러 모델 이름 시도 (실제 사용 가능한 모델)
    print("[3단계] 모델별 테스트 중...")
    test_models = [
        'models/gemini-2.0-flash',  # 가장 안정적
        'models/gemini-flash-latest',  # 최신 버전
        'models/gemini-2.5-flash',  # 최신 성능
        'models/gemini-2.0-flash-001',
    ]
    
    test_prompt = "안녕하세요. 간단히 인사만 해주세요."
    
    success = False
    for model_name in test_models:
        try:
            print(f"  모델 '{model_name}' 시도 중...", end=" ")
            response = client.models.generate_content(
                model=model_name,
                contents=test_prompt
            )
            print(f"[OK] 성공!")
            print(f"    응답: {response.text[:100]}...")
            print()
            success = True
            break
        except Exception as e:
            error_msg = str(e)
            if '404' in error_msg or 'NOT_FOUND' in error_msg:
                print(f"[FAIL] 모델을 찾을 수 없음")
            else:
                print(f"[ERROR] 오류: {error_msg[:50]}...")
    
    if not success:
        print("\n[WARN] 모든 모델 시도 실패")
    
    print("=" * 60)
    print("테스트 완료")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

