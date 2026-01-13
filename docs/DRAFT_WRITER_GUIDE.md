# Draft Writer 사용 가이드

Gemini API를 사용한 블로그 포스트 자동 생성 스크립트 사용법입니다.

## 설치

### 1. Python 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 Gemini API 키를 설정하세요:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**API 키 발급 방법:**
1. https://makersuite.google.com/app/apikey 접속
2. "Create API Key" 클릭
3. 생성된 API 키를 `.env` 파일에 입력

## 사용법

### 기본 실행

```bash
python draft_writer.py
```

스크립트를 실행하면 주제나 메모를 입력하라는 프롬프트가 나타납니다. 여러 줄 입력이 가능하며, 빈 줄을 입력하면 입력이 종료됩니다.

### 입력 예시

```
FPGA에서 SPI 통신을 구현하는 방법
RS232 트리거를 받아서 4개의 EEPROM을 병렬로 읽어서 BRAM에 로드하는 설계
```

### 실행 과정

스크립트는 3단계로 글을 생성합니다:

1. **Step 1: 구성 작가 (The Drafter)**
   - 입력받은 메모를 바탕으로 논리적인 글의 뼈대와 초안 작성
   - 팩트와 정보 전달 위주로 서론-본론-결론 구조 구성

2. **Step 2: 페르소나 에디터 (The Persona)**
   - Step 1의 글을 특정 말투로 리라이팅
   - 10년 차 임베디드 시스템 엔지니어의 시니컬한 기술 블로거 톤 적용
   - '음/함' 체나 자연스러운 구어체 사용

3. **Step 3: 교정 및 포맷팅 (The Polisher)**
   - 최종 문법 검수 및 Jekyll Front Matter 추가
   - 마크다운 포맷 정리
   - 카테고리와 태그 자동 추천

### 출력

생성된 포스트는 `_posts/YYYY-MM-DD-영문키워드.md` 형식으로 저장됩니다.

## 생성된 파일 확인 및 수정

생성된 포스트는 자동으로 Jekyll Front Matter가 포함되어 있지만, 필요에 따라 다음을 수정할 수 있습니다:

- `category`: dev/daily/document/study 중 선택
- `tags`: 내용에 맞는 태그 추가/수정
- `title`: 제목 수정
- 본문 내용: 필요시 추가 수정

## GitHub에 업로드

```bash
git add _posts/YYYY-MM-DD-*.md
git commit -m "[v0.0.X] Add new post: 제목"
git push origin main
```

GitHub Pages가 자동으로 빌드하여 블로그에 반영합니다.

## 주의사항

- `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다
- API 키는 절대 공개 저장소에 커밋하지 마세요
- 생성된 포스트는 자동으로 완벽하지 않을 수 있으니, 반드시 검토 후 게시하세요
- Gemini API 사용량에 따라 비용이 발생할 수 있습니다 (무료 티어 한도 확인)
