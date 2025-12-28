#!/usr/bin/env python3
"""
Gemini API 사용 가능한 모델 목록 확인 스크립트
"""

import os
import sys
from google import genai

def main():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    print("=" * 60)
    print("Gemini API 모델 테스트")
    print("=" * 60)
    
    try:
        client = genai.Client(api_key=api_key)
        print("✅ 클라이언트 초기화 성공\n")
        
        # 사용 가능한 모델 목록 조회
        print("사용 가능한 모델 목록 조회 중...")
        try:
            models = client.models.list()
            print(f"✅ 모델 목록 조회 성공: {len(list(models))}개 모델 발견\n")
            
            print("사용 가능한 모델:")
            for model in models:
                print(f"  - {model.name}")
                if hasattr(model, 'supported_generation_methods'):
                    print(f"    지원 메서드: {model.supported_generation_methods}")
                print()
        except Exception as e:
            print(f"⚠️  모델 목록 조회 실패: {str(e)}\n")
        
        # 여러 모델 이름으로 테스트
        test_models = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'models/gemini-pro',
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro-latest',
        ]
        
        print("=" * 60)
        print("모델별 테스트")
        print("=" * 60)
        
        test_prompt = "안녕하세요"
        
        for model_name in test_models:
            try:
                print(f"\n모델 '{model_name}' 테스트 중...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=test_prompt
                )
                print(f"✅ 성공! 응답: {response.text[:50]}...")
                print(f"✅ 사용 가능한 모델: {model_name}")
                break
            except Exception as e:
                error_msg = str(e)
                if '404' in error_msg or 'NOT_FOUND' in error_msg:
                    print(f"❌ 모델을 찾을 수 없음")
                else:
                    print(f"⚠️  오류: {error_msg[:100]}")
                continue
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

