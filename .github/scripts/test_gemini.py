#!/usr/bin/env python3
"""
Gemini API 테스트 스크립트
사용 가능한 모델 목록을 확인하고 간단한 테스트를 수행한다.
"""

import os
import sys
from google import genai

def test_gemini_api():
    """Gemini API 테스트"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    print("=" * 60)
    print("Gemini API 테스트 시작")
    print("=" * 60)
    
    try:
        # 클라이언트 초기화
        client = genai.Client(api_key=api_key)
        print("✅ 클라이언트 초기화 완료")
        
        # 사용 가능한 모델 목록 확인
        print("\n[1단계] 사용 가능한 모델 목록 조회 중...")
        try:
            models = client.models.list()
            print(f"✅ 모델 목록 조회 성공")
            print("\n사용 가능한 모델:")
            for model in models:
                print(f"  - {model.name}")
                if hasattr(model, 'display_name'):
                    print(f"    Display Name: {model.display_name}")
                if hasattr(model, 'supported_generation_methods'):
                    print(f"    지원 메서드: {model.supported_generation_methods}")
                print()
        except Exception as e:
            print(f"⚠️  모델 목록 조회 실패: {str(e)}")
            print("직접 모델 이름을 시도합니다...")
        
        # 여러 모델 이름 시도
        print("\n[2단계] 모델별 테스트...")
        test_models = [
            'gemini-pro',
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'models/gemini-pro',
            'models/gemini-1.5-pro',
            'models/gemini-1.5-flash',
        ]
        
        working_model = None
        for model_name in test_models:
            try:
                print(f"\n모델 '{model_name}' 테스트 중...")
                response = client.models.generate_content(
                    model=model_name,
                    contents="안녕하세요. 간단히 인사만 해주세요."
                )
                print(f"✅ 모델 '{model_name}' 성공!")
                print(f"응답: {response.text[:100]}...")
                working_model = model_name
                break
            except Exception as e:
                error_msg = str(e)
                print(f"❌ 모델 '{model_name}' 실패: {error_msg[:200]}")
                continue
        
        if working_model:
            print("\n" + "=" * 60)
            print(f"✅ 작동하는 모델 발견: {working_model}")
            print("=" * 60)
            return working_model
        else:
            print("\n" + "=" * 60)
            print("❌ 작동하는 모델을 찾을 수 없습니다.")
            print("=" * 60)
            return None
            
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    result = test_gemini_api()
    sys.exit(0 if result else 1)

