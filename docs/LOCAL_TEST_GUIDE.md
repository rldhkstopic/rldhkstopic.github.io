# 로컬 테스트 가이드

디스코드 봇 없이 로컬 컴퓨터에서 글 작성 기능을 테스트하는 방법을 안내합니다.

## 📋 사전 준비

### 1. Python 설치 확인

Python 3.11 이상이 설치되어 있어야 합니다.

```bash
python --version
```

### 2. GEMINI_API_KEY 환경 변수 설정

Gemini API 키를 환경 변수로 설정해야 합니다.

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

**Windows (CMD):**
```cmd
set GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

⚠️ **보안 주의**: API 키를 코드에 하드코딩하지 마세요!

### 3. Python 패키지 설치

프로젝트 루트에서 다음 명령어를 실행하세요:

```bash
pip install -r .github/scripts/requirements.txt
```

필요한 패키지:
- `google-genai>=0.2.0`
- `requests>=2.31.0`
- `python-dateutil>=2.8.2`

## 🚀 실행 방법

### 방법 1: PowerShell 스크립트 사용 (Windows 권장)

```powershell
.\scripts\test-discord-write.ps1
```

이 스크립트는 자동으로:
1. Python 설치 확인
2. 환경 변수 확인
3. 패키지 설치 확인
4. 테스트 실행

### 방법 2: Python 스크립트 직접 실행

```bash
python .github/scripts/test_discord_write.py
```

## 📝 사용 예시

### 실행 흐름

1. **카테고리 선택**
   ```
   카테고리를 선택하세요:
     1. dev (개발 관련)
     2. study (학습 내용)
     3. daily (일상 기록)
     4. document (문서화/분석)
   
   선택 (1-4): 1
   ```

2. **제목 입력**
   ```
   제목/주제를 입력하세요 (필수): FPGA 메모리 설계 고찰
   ```

3. **상황 입력** (선택)
   ```
   상황/문제 설명을 입력하세요 (선택, Enter로 건너뛰기):
   FPGA 프로젝트에서 BRAM과 Flash 메모리를 사용하는 방법을 정리하고 싶다.
   ```

4. **액션 입력** (선택)
   ```
   해결 방법/시도한 내용을 입력하세요 (선택, Enter로 건너뛰기):
   Vivado 문서를 참고하여 메모리 구조를 분석했다.
   ```

5. **메모 입력** (선택)
   ```
   기타 메모나 참고 링크를 입력하세요 (선택, Enter로 건너뛰기):
   https://www.xilinx.com/support/documentation/user_guides/ug473.pdf
   ```

6. **자동 처리**
   - 요청 JSON 파일 생성 (`_auto_post_requests/request_YYYYMMDD_HHMMSS.json`)
   - AI 에이전트 파이프라인 실행:
     - 조사 (ResearcherAgent)
     - 분석 (AnalystAgent)
     - 작성 (WriterAgent)
     - 검토 (ReviewerAgent)
     - 검증 (ValidatorAgent)
     - 포스트 생성 (PostCreatorAgent)
   - 최종 포스트 파일 생성 (`_posts/YYYY-MM-DD-제목.md`)

## 📂 생성되는 파일

### 요청 파일
- 위치: `_auto_post_requests/request_YYYYMMDD_HHMMSS.json`
- 내용: 사용자 입력이 JSON 형식으로 저장됨
- 처리 후: `_auto_post_requests_processed/`로 이동

### 포스트 파일
- 위치: `_posts/YYYY-MM-DD-제목.md`
- 형식: Jekyll Front Matter + Markdown 본문
- 작성 가이드: `docs/WRITING_STYLE_GUIDE.md` 참고

## 🔍 결과 확인

### 성공 시
```
[SUCCESS] 자동 포스팅 완료!
```

생성된 포스트는 `_posts/` 디렉토리에서 확인할 수 있습니다.

### 실패 시
에러 메시지를 확인하고 다음을 점검하세요:
1. GEMINI_API_KEY가 올바른지 확인
2. 인터넷 연결 확인
3. Python 패키지가 올바르게 설치되었는지 확인
4. 에러 메시지를 자세히 확인

## 📚 관련 문서

- [작성 스타일 가이드](./WRITING_STYLE_GUIDE.md)
- [디스코드 파이프라인 가이드](./DISCORD_WRITING_PIPELINE.md)
- [카테고리별 작성 가이드](./CATEGORY_WRITING_GUIDES.md)

## 💡 팁

### 카테고리별 특징

- **dev**: 코드와 실행 환경 정보가 필수
- **study**: 개념 설명과 예제 중심
- **daily**: 개인적 경험과 감정 묘사
- **document**: 데이터와 출처 명시 필수

### 입력 팁

- **제목**: 구체적이고 검색 가능한 키워드 포함
- **상황**: 왜 이 글을 쓰는지, 어떤 문제/관심사인지 명확히
- **액션**: 어떤 조사나 시도를 했는지 구체적으로
- **메모**: 참고 링크나 추가 정보 제공

### 로컬 Jekyll 서버로 미리보기

생성된 포스트를 로컬에서 미리 볼 수 있습니다:

```bash
bundle exec jekyll serve
```

브라우저에서 `http://localhost:4000` 접속

## ⚠️ 주의사항

1. **API 비용**: Gemini API 사용 시 비용이 발생할 수 있습니다.
2. **요청 제한**: API 사용량 제한이 있을 수 있으니 과도한 테스트는 피하세요.
3. **파일 관리**: 테스트 후 불필요한 요청 파일은 정리하세요.
4. **Git 커밋**: 생성된 포스트는 자동으로 커밋되지 않습니다. 필요시 수동으로 커밋하세요.

## 🐛 문제 해결

### "GEMINI_API_KEY 환경 변수가 설정되지 않았습니다"
→ 환경 변수를 올바르게 설정했는지 확인하세요.

### "Python이 설치되어 있지 않습니다"
→ Python 3.11 이상을 설치하세요.

### "패키지 설치에 실패했습니다"
→ 인터넷 연결을 확인하고, pip를 업그레이드하세요:
```bash
python -m pip install --upgrade pip
```

### "글 작성에 실패했습니다"
→ API 키가 올바른지, 인터넷 연결이 정상인지 확인하세요.
