# Vercel 환경 변수 설정 가이드

GitHub OAuth를 위한 Vercel 환경 변수 설정 방법이다.

## 환경 변수 설정

### 1. 첫 번째 환경 변수 (Client ID)

**Key:**
```
GITHUB_CLIENT_ID
```

**Value:**
```
[GitHub OAuth App에서 발급받은 Client ID를 입력하세요]
```

**설정:**
- Environments: **All Environments** 선택 (또는 Production, Preview, Development 모두 체크)
- Sensitive: Disabled (Client ID는 공개 가능)

### 2. 두 번째 환경 변수 (Client Secret)

**Key:**
```
GITHUB_CLIENT_SECRET
```

**Value:**
```
[GitHub OAuth App에서 발급받은 Client Secret을 입력하세요]
⚠️ 보안: 이 값은 절대 공개 저장소에 커밋하지 마세요!
```

**설정:**
- Environments: **Production과 Preview만 선택** (Development는 선택하지 않음)
  - ⚠️ **중요:** Sensitive 환경 변수는 Development 환경에서 생성할 수 없음
- Sensitive: **Enabled** (토글 켜기) ⚠️ **중요: Client Secret은 반드시 Sensitive로 설정**

## 단계별 설정 방법

1. **첫 번째 변수 추가:**
   - Key 필드에 `GITHUB_CLIENT_ID` 입력
   - Value 필드에 [GitHub OAuth App에서 발급받은 Client ID] 입력
   - Environments: All Environments 선택
   - Sensitive: Disabled (기본값)

2. **"Add Another" 버튼 클릭**

3. **두 번째 변수 추가:**
   - Key 필드에 `GITHUB_CLIENT_SECRET` 입력
   - Value 필드에 [GitHub OAuth App에서 발급받은 Client Secret] 입력
   - ⚠️ **보안 주의**: Client Secret은 절대 공개 저장소에 커밋하지 마세요!
   - Environments: **Production과 Preview만 선택** (Development는 선택하지 않음)
     - ⚠️ Sensitive 변수는 Development 환경에서 생성 불가
   - Sensitive: **Enabled로 토글 켜기** ⚠️

4. **Save 버튼 클릭**

## 중요 사항

### Key vs Value 구분

- **Key**: 환경 변수의 이름 (코드에서 `process.env.GITHUB_CLIENT_ID`로 접근)
- **Value**: 실제 값 (Client ID나 Client Secret)

### Sensitive 설정

- **Client ID**: Sensitive Disabled (공개 가능)
- **Client Secret**: Sensitive Enabled (보안 필수)

Sensitive를 Enabled로 설정하면:
- 저장 후 Value를 다시 볼 수 없음
- 팀원도 값을 확인할 수 없음
- 보안이 강화됨

## 확인 방법

환경 변수 저장 후:
1. **Deployments** 탭으로 이동
2. 최신 배포의 **...** 메뉴 클릭
3. **Redeploy** 선택 (환경 변수 적용)
4. 배포 완료 후 `/admin/` 페이지에서 로그인 테스트

## 문제 해결

### "Sensitive environment variables cannot be created in the Development environment" 오류

**원인:** Vercel은 Sensitive 환경 변수를 Development 환경에서 생성할 수 없도록 제한한다.

**해결:**
1. Environments 드롭다운에서 **Development 체크 해제**
2. **Production**과 **Preview**만 선택
3. Sensitive 토글을 Enabled로 설정
4. Save 클릭

**참고:**
- Client ID는 Development 환경에도 추가 가능 (Sensitive Disabled)
- Client Secret은 Production과 Preview 환경에만 추가 가능 (Sensitive Enabled)

### "GitHub OAuth credentials not configured" 오류

- 환경 변수 Key 이름이 정확한지 확인 (`GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`)
- 환경 변수 저장 후 배포가 재실행되었는지 확인
- Vercel 대시보드에서 환경 변수가 올바르게 설정되었는지 확인

### 환경 변수가 적용되지 않음

- 환경 변수 저장 후 **새 배포가 필요함**
- Settings → Environment Variables에서 변수가 표시되는지 확인
- 배포 로그에서 환경 변수가 로드되었는지 확인

