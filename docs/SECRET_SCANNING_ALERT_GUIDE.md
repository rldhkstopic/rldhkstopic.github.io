# Secret Scanning 알림 처리 가이드

GitHub의 Secret Scanning이 활성화되어 있고 알림이 1개 있습니다. 이는 노출된 키가 감지되었다는 의미입니다.

## 현재 상태

✅ **Secret scanning alerts • Enabled** - 활성화됨 (좋음)
⚠️ **알림 1개** - 노출된 키가 감지됨 (처리 필요)

## 다음 단계

### 1단계: 노출된 키 확인

1. Security overview 페이지에서 **"View detected secrets"** 링크 클릭
2. 감지된 시크릿 목록 확인
3. 어떤 키가 노출되었는지 확인:
   - GEMINI_API_KEY인지
   - GitHub OAuth Client Secret인지
   - 다른 키인지

### 2단계: 노출된 키 처리

#### 옵션 A: 키가 이미 교체됨 (권장)

새 GEMINI_API_KEY로 교체했다면:

1. **"Revoke secret"** 또는 **"Mark as resolved"** 클릭
2. GitHub에서 제공하는 키 회수 링크 사용 (있는 경우)
3. Google AI Studio에서 이전 키 삭제/비활성화

#### 옵션 B: 키를 아직 교체하지 않음

1. **즉시 키 교체**
   - GEMINI_API_KEY: `docs/UPDATE_GEMINI_API_KEY.md` 참고
   - GitHub OAuth Client Secret: GitHub에서 새 Secret 생성

2. **노출된 키 회수**
   - Google AI Studio에서 이전 키 삭제
   - GitHub OAuth App에서 이전 Secret 삭제

3. **알림 해결 표시**
   - "Mark as resolved" 클릭

### 3단계: Git 히스토리 정리 (선택사항)

히스토리에서 키를 완전히 제거하려면:
- `docs/REMOVE_KEYS_FROM_HISTORY.md` 참고
- ⚠️ 주의: 히스토리 재작성은 모든 커밋 해시를 변경합니다

## 권장 조치

### 즉시 해야 할 일

1. ✅ **"View detected secrets" 클릭하여 확인**
2. ✅ **노출된 키를 새 키로 교체** (이미 진행 중)
3. ✅ **이전 키 회수/비활성화**
4. ✅ **알림 해결 표시**

### 추가 보안 조치

1. **Dependabot alerts 활성화** (권장)
   - 의존성 취약점 알림 받기
   - "Enable Dependabot alerts" 클릭

2. **Code scanning 활성화** (선택사항)
   - 코드 취약점 자동 검사
   - "Set up code scanning" 클릭

3. **Security policy 설정** (권장)
   - 보안 취약점 신고 방법 정의
   - "Set up a security policy" 클릭

## 예상되는 시나리오

### 시나리오 1: GEMINI_API_KEY 노출

감지된 키가 이전 GEMINI_API_KEY라면:
- ✅ 이미 새 키로 교체했으므로 이전 키만 회수하면 됨
- ✅ Google AI Studio에서 이전 키 삭제
- ✅ 알림 해결 표시

### 시나리오 2: GitHub OAuth Client Secret 노출

감지된 키가 Client Secret이라면:
- ⚠️ 즉시 새 Secret 생성 필요
- ⚠️ Vercel 환경 변수 업데이트 필요
- ⚠️ GitHub OAuth App에서 이전 Secret 삭제

## 확인 방법

알림을 해결한 후:
1. Security overview 페이지 새로고침
2. Secret scanning 알림이 0개가 되었는지 확인
3. "View detected secrets"에서 해결된 항목 확인

## 참고

- [GitHub Secret Scanning 문서](https://docs.github.com/en/code-security/secret-scanning)
- [노출된 키 제거 가이드](./REMOVE_KEYS_FROM_HISTORY.md)
- [새 키 업데이트 가이드](./UPDATE_GEMINI_API_KEY.md)

