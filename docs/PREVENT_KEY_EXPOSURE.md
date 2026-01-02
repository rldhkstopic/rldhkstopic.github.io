# API 키 노출 방지 가이드

이 문서는 API 키가 Git 히스토리에 다시 노출되지 않도록 하는 예방 조치를 설명합니다.

## 현재 적용된 보호 조치

### 1. ✅ .gitignore 업데이트
API 키가 포함될 수 있는 파일 패턴을 `.gitignore`에 추가했습니다:
- `*.key`, `*.secret`
- `*_api_key*`, `*_secret*`
- `.env`, `.env.local`
- `secrets.json`, `credentials.json`

### 2. ✅ Pre-commit Hook
커밋 전에 자동으로 API 키를 검사합니다:
- **Linux/Mac**: `.git/hooks/pre-commit` (bash 스크립트)
- **Windows**: `.git/hooks/pre-commit.ps1` (PowerShell 스크립트)

검사하는 패턴:
- Google API 키: `AIza...`
- GitHub 토큰: `ghp_...`, `gho_...` 등
- 일반적인 시크릿: 40자리 hex 문자열
- 하드코딩된 자격증명

### 3. ✅ 수동 검사 스크립트
`scripts/check-secrets.ps1` - 커밋 전에 수동으로 실행 가능

## 사용 방법

### Pre-commit Hook 테스트

```bash
# 테스트 파일 생성
echo 'GEMINI_API_KEY = "<DUMMY_KEY_FOR_TEST>"' > test-key.txt

# 스테이징
git add test-key.txt

# 커밋 시도 (hook이 차단해야 함)
git commit -m "test"
```

예상 결과: 커밋이 차단되고 에러 메시지가 표시됩니다.

### 수동 검사 (Windows)

```powershell
# PowerShell에서 실행
.\scripts\check-secrets.ps1
```

## Hook 비활성화 (비상시)

**⚠️ 권장하지 않음**: 보안상의 이유로 hook을 비활성화하지 마세요.

비상시에만:
```bash
# 한 번만 건너뛰기
git commit --no-verify -m "message"

# Hook 완전히 비활성화 (권장하지 않음)
chmod -x .git/hooks/pre-commit
```

## 추가 보안 조치

### 1. GitHub Secret Scanning 활성화

GitHub 리포지토리에서:
1. **Settings** → **Security** → **Secret scanning**
2. **Enable secret scanning** 활성화
3. 노출된 키가 감지되면 자동으로 알림을 받습니다

### 2. 코드 리뷰 시 확인

Pull Request를 만들 때:
- API 키가 포함된 파일이 있는지 확인
- 환경 변수 사용 여부 확인
- 문서에 실제 키 값이 없는지 확인

### 3. 정기적인 감사

```bash
# 히스토리에서 키 검색
git log --all --full-history -S "AIzaSy" --source -- "*"

# 현재 작업 디렉토리에서 키 검색
grep -r "AIzaSy" . --exclude-dir=.git
```

## 문제 해결

### Hook이 작동하지 않음

**Windows에서:**
```powershell
# PowerShell 실행 정책 확인
Get-ExecutionPolicy

# 필요시 변경 (관리자 권한 필요)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/Mac에서:**
```bash
# 실행 권한 확인
ls -l .git/hooks/pre-commit

# 실행 권한 부여
chmod +x .git/hooks/pre-commit
```

### False Positive (잘못된 경고)

Hook이 예시 코드나 주석을 키로 인식하는 경우:
- 주석에 `# example` 또는 `# placeholder` 추가
- 문서에 `TODO` 또는 `주의` 키워드 추가

## 모범 사례

1. ✅ **절대 하드코딩하지 않기**
   ```python
   # 나쁜 예
   api_key = "AIzaSy..."
   
   # 좋은 예
   api_key = os.getenv('GEMINI_API_KEY')
   ```

2. ✅ **환경 변수 사용**
   - 로컬: `.env` 파일 (`.gitignore`에 추가)
   - GitHub Actions: Secrets
   - Vercel: Environment Variables

3. ✅ **문서에 실제 키 포함하지 않기**
   ```markdown
   # 나쁜 예
   GITHUB_CLIENT_SECRET=<YOUR_CLIENT_SECRET>
   
   # 좋은 예
   GITHUB_CLIENT_SECRET=[GitHub OAuth App에서 발급받은 Client Secret]
   ```

4. ✅ **정기적인 키 로테이션**
   - 3-6개월마다 키 교체
   - 노출 의심 시 즉시 교체

## 참고 자료

- [GitHub: Secret scanning](https://docs.github.com/en/code-security/secret-scanning)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Git Hooks 문서](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)

