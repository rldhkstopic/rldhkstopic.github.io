# Git 히스토리에서 API 키 제거 가이드

Git 히스토리에 이미 커밋된 API 키는 단순히 파일을 수정하는 것만으로는 제거되지 않습니다. 히스토리 전체에서 키를 완전히 제거해야 합니다.

## ⚠️ 중요 경고

**이 작업은 Git 히스토리를 재작성합니다.**
- 모든 커밋 해시가 변경됩니다
- 협업 중이라면 팀원들과 반드시 협의하세요
- **반드시 백업을 먼저 생성하세요**

## 방법 1: git filter-branch 사용 (권장)

### 1단계: 백업 생성
```bash
# 현재 상태 백업
git clone --mirror . ../backup-repo.git
```

### 2단계: 히스토리에서 키 제거
```bash
# GEMINI_API_KEY 제거
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .github/scripts/test_local.py" \
  --prune-empty --tag-name-filter cat -- --all

# 특정 키 값 제거 (더 정확한 방법)
git filter-branch --force --tree-filter \
  "sed -i '' 's/<LEAKED_OLD_GEMINI_KEY>/REMOVED_API_KEY/g' .github/scripts/test_local.py 2>/dev/null || true" \
  --prune-empty --tag-name-filter cat -- --all

# 문서에서 Client Secret 제거
git filter-branch --force --tree-filter \
  "sed -i '' 's/<LEAKED_OLD_GITHUB_OAUTH_CLIENT_SECRET>/REMOVED_CLIENT_SECRET/g' docs/VERCEL_ENV_VARS_SETUP.md 2>/dev/null || true" \
  --prune-empty --tag-name-filter cat -- --all
```

### 3단계: 원격 저장소에 강제 푸시
```bash
# ⚠️ 주의: 이 작업은 되돌릴 수 없습니다!
git push origin --force --all
git push origin --force --tags
```

## 방법 2: BFG Repo-Cleaner 사용 (더 빠름)

BFG는 git filter-branch보다 빠르고 사용하기 쉽습니다.

### 1단계: BFG 설치
```bash
# Java가 필요합니다
# Windows: https://rtyley.github.io/bfg-repo-cleaner/ 에서 다운로드
# 또는 Chocolatey: choco install bfg
```

### 2단계: 키가 포함된 파일 목록 생성
`keys-to-remove.txt` 파일 생성:
```
<LEAKED_OLD_GEMINI_KEY>
<LEAKED_OLD_GITHUB_OAUTH_CLIENT_SECRET>
```

### 3단계: BFG 실행
```bash
# 히스토리에서 키 제거
java -jar bfg.jar --replace-text keys-to-remove.txt

# 정리
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### 4단계: 원격 저장소에 강제 푸시
```bash
git push origin --force --all
```

## 방법 3: GitHub Secret Scanning 활용

GitHub는 자동으로 노출된 키를 감지합니다:
1. GitHub 리포지토리 → **Settings** → **Security** → **Secret scanning**
2. 노출된 키가 감지되면 알림을 받습니다
3. 키를 교체하고 히스토리를 정리하세요

## 방법 4: 새 저장소로 이전 (가장 안전)

히스토리를 완전히 새로 시작하는 방법:

```bash
# 새 브랜치 생성
git checkout --orphan clean-main

# 모든 파일 추가 (히스토리 없이)
git add .
git commit -m "Initial commit (cleaned history)"

# 기존 main 삭제 및 새 main으로 교체
git branch -D main
git branch -m main

# 강제 푸시
git push origin --force main
```

## 작업 후 확인

### 1. 히스토리에서 키 검색
```bash
# 키가 완전히 제거되었는지 확인
git log --all --full-history --source -S "<LEAKED_OLD_GEMINI_KEY>"
git log --all --full-history --source -S "<LEAKED_OLD_GITHUB_OAUTH_CLIENT_SECRET>"
```

결과가 없으면 성공입니다.

### 2. 노출된 키 교체
히스토리에서 제거한 후에도 **반드시 새 키로 교체**해야 합니다:
- GEMINI_API_KEY: Google AI Studio에서 새 키 생성
- GitHub OAuth Client Secret: GitHub에서 새 Secret 생성

## 예방 조치

앞으로 키가 노출되지 않도록:
1. ✅ `.gitignore`에 키 파일 패턴 추가 (완료)
2. ✅ `pre-commit` hook으로 커밋 전 검사 (완료)
3. ✅ GitHub Secret Scanning 활성화
4. ✅ 코드 리뷰 시 키 검사
5. ✅ 환경 변수만 사용

## 참고 자료

- [GitHub: Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [git filter-branch 문서](https://git-scm.com/docs/git-filter-branch)

