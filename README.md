# rldhkstopic 블로그

## 사전 요구사항

Jekyll을 실행하기 위해 Ruby와 Bundler가 필요합니다.

### Windows에서 Ruby 설치

1. [RubyInstaller](https://rubyinstaller.org/downloads/)에서 Ruby+Devkit 버전을 다운로드합니다.
2. 설치 프로그램을 실행하고 "Add Ruby executables to your PATH" 옵션을 선택합니다.
3. 설치 완료 후 새로운 PowerShell 창을 열고 다음 명령어로 설치를 확인합니다:
```bash
ruby --version
```

4. Bundler를 설치합니다:
```bash
gem install bundler
```

### 다중 프로젝트 환경에서 버전 관리

여러 프로젝트를 관리할 때 버전 충돌을 방지하기 위한 전략이다.

**Bundler의 기본 격리 메커니즘**

Bundler는 `Gemfile.lock`을 통해 각 프로젝트의 gem 버전을 고정한다. `bundle install`을 실행하면:
- `Gemfile.lock`에 명시된 정확한 버전이 설치된다
- 다른 프로젝트의 `Gemfile.lock`과 독립적으로 작동한다
- 시스템 gem과 충돌하지 않도록 격리된 환경에서 실행된다

**프로젝트별 gem 격리 (권장)**

각 프로젝트의 gem을 완전히 분리하려면 `vendor/bundle`에 설치한다:

```bash
bundle config set --local path 'vendor/bundle'
bundle install
```

이렇게 하면:
- 각 프로젝트의 `vendor/bundle` 디렉토리에 gem이 설치된다
- 프로젝트 간 gem 버전이 완전히 격리된다
- `.gitignore`에 `vendor/`가 포함되어 있어 버전 관리에서 제외된다

**Ruby 버전 관리 (선택사항)**

여러 프로젝트에서 서로 다른 Ruby 버전이 필요한 경우, Windows에서 `rbenv-win`을 사용할 수 있다:

1. [rbenv-win](https://github.com/ccmywish/rbenv-win) 설치
2. 프로젝트 루트에 `.ruby-version` 파일 생성:
```bash
echo 3.3.0 > .ruby-version
```
3. 해당 프로젝트에서만 지정된 Ruby 버전이 사용된다

**현재 프로젝트 설정 확인**

현재 프로젝트는 `Gemfile.lock`에 Jekyll 4.4.1이 고정되어 있다. 다른 프로젝트에서 다른 버전을 사용해도 충돌하지 않는다.

### Cursor 에디터 터미널에서 Ruby 인식 문제

Windows 터미널에서는 `ruby -v`가 작동하지만 Cursor 터미널에서는 인식되지 않는 경우, 다음 방법을 시도하세요:

**방법 1: Cursor 재시작 (권장)**
- Cursor를 완전히 종료한 후 다시 실행합니다. 새로 시작된 프로세스는 업데이트된 환경 변수를 로드합니다.

**방법 2: 현재 세션에서 PATH 수동 추가**
Windows 터미널에서 다음 명령어로 Ruby 경로를 확인합니다:
```bash
where.exe ruby
```

확인된 경로(예: `C:\Ruby33-x64\bin`)를 Cursor 터미널에서 임시로 추가합니다:
```bash
$env:PATH += ";C:\Ruby33-x64\bin"
```

**방법 3: PowerShell 프로필에 PATH 추가**
PowerShell 프로필을 편집하여 Ruby 경로를 영구적으로 추가합니다:
```bash
notepad $PROFILE
```

프로필 파일에 다음을 추가합니다:
```powershell
$env:PATH += ";C:\Ruby33-x64\bin"  # 실제 Ruby 경로로 변경
```

## 로컬 서버 실행

로컬 서버는 **개발 및 테스트용**으로만 사용된다. Vercel 배포와는 별개로 작동한다.

### 1. 의존성 설치
```bash
bundle install
```

### 2. 서버 실행
```bash
bundle exec jekyll serve
```

서버가 실행되면 `http://localhost:4000`에서 확인할 수 있습니다.

### 3. 서버 중지
터미널에서 `Ctrl + C`를 누르세요.

### ⚠️ 로컬 서버와 Vercel 배포의 관계

- **로컬 서버 (`bundle exec jekyll serve`)**: 로컬 컴퓨터에서만 작동하는 개발 서버
  - Vercel과 **연동되지 않음**
  - 코드 수정이 Vercel에 자동 반영되지 않음
  - 로컬에서만 변경사항 확인 가능

- **Vercel 배포**: GitHub 저장소와 연동되어 자동 배포
  - GitHub에 푸시하면 자동으로 배포 시작
  - 로컬 서버 실행 여부와 무관하게 작동
  - 배포된 사이트는 전 세계에서 접근 가능

## 배포

### GitHub Pages 배포

GitHub Pages에 자동으로 배포됩니다. `main` 브랜치에 푸시하면 자동으로 빌드됩니다.

```bash
git add .
git commit -m "변경사항"
git push origin main
```

배포 완료 후 `https://rldhkstopic.github.io`에서 확인할 수 있습니다.

### Vercel 배포

Vercel을 사용하여 배포할 수 있다. GitHub Pages와 동시에 사용하거나 대체 배포 플랫폼으로 사용할 수 있다.

#### 1. Vercel 프로젝트 연결

**단계별 가이드:**

1. **Vercel 로그인**
   - [Vercel](https://vercel.com)에 GitHub 계정으로 로그인

2. **프로젝트 Import**
   - 대시보드에서 **Add New Project** 클릭
   - GitHub 저장소 목록에서 프로젝트 선택
   - **Import** 클릭

3. **프로젝트 설정 화면**

   Vercel이 `Gemfile`과 `_config.yml`을 감지하여 **Jekyll 프리셋을 자동 선택**한다. 이는 정상 동작이다.

   **프로젝트 이름 오류 해결:**
   - Vercel 프로젝트 이름은 **소문자만 허용**된다
   - 자동 입력된 이름에 대문자가 포함되어 있으면 빨간색 오류 메시지가 표시된다
   - **Project Name** 필드의 값을 소문자로 변경한다
   - 예: `rldhkstopicPage` → `rldhkstopic-page` 또는 `rldhkstopicpage`
   - 허용되는 문자: 소문자, 숫자, `.`, `_`, `-` (단, `---` 연속 사용 불가)

   **중요:** `vercel.json` 파일이 있으면 해당 설정이 UI 설정보다 우선순위가 높다. 따라서 UI에서 보이는 값과 관계없이 `vercel.json`의 설정이 사용된다.

   **설정 확인 사항:**
   - **Framework Preset**: `Jekyll` (자동 선택됨, 그대로 두어도 됨)
   - **Project Name**: 소문자로 변경 (오류가 있으면 수정)
   - **Root Directory**: `./` (기본값, 변경 불필요)
   - **Build Command**: `bundle install && bundle exec jekyll build` (vercel.json에서 자동 로드됨)
   - **Output Directory**: `_site` (vercel.json에서 자동 로드됨)
   - **Install Command**: `gem install bundler && bundle install` (vercel.json에서 자동 로드됨)

   **참고:** UI에서 Jekyll 프리셋이 선택되어 있어도, 프로젝트 루트의 `vercel.json` 파일이 있으면 해당 파일의 설정이 우선 적용된다. UI의 값은 참고용으로만 보인다.

4. **환경 변수 설정 (선택사항)**
   - 이 단계에서는 환경 변수를 설정하지 않아도 된다
   - 배포 후 Settings에서 추가할 수 있다

5. **Deploy 클릭**
   - **Deploy** 버튼을 클릭하여 첫 배포 시작
   - 배포가 완료되면 배포 URL이 표시된다

#### 2. 환경 변수 설정 (선택사항)

GitHub OAuth 로그인 기능을 사용하려면:

1. **GitHub OAuth App 생성** (필수)
   - [GitHub Settings → Developer settings → OAuth Apps](https://github.com/settings/developers)
   - **New OAuth App** 클릭
   - **Authorization callback URL**: `https://your-project.vercel.app/admin/`
   - Client ID와 Client Secret 생성

2. **Vercel 환경 변수 설정**
   - 프로젝트 → **Settings** → **Environment Variables**
   - 다음 변수 추가:
     - `GITHUB_CLIENT_ID`: GitHub OAuth App의 Client ID
     - `GITHUB_CLIENT_SECRET`: GitHub OAuth App의 Client Secret

**자세한 설정 방법:** [GitHub OAuth 설정 가이드 (Vercel 배포용)](docs/GITHUB_OAUTH_VERCEL_SETUP.md) 참고

#### 3. 배포

**Vercel은 GitHub 저장소와 연동되어 자동으로 배포한다.**

### 자동 배포 (권장)

GitHub에 푸시하면 Vercel이 자동으로 배포를 시작한다:

```bash
git add .
git commit -m "변경사항"
git push origin main
```

**배포 프로세스:**
1. GitHub에 푸시
2. Vercel이 변경사항 감지 (보통 몇 초 내)
3. 자동으로 빌드 시작
4. 빌드 완료 후 배포 (보통 1-3분 소요)
5. 배포 완료 후 사이트 자동 업데이트

**배포 상태 확인:**
- Vercel 대시보드 → **Deployments** 탭에서 실시간 배포 상태 확인
- 배포 완료 후 배포 URL에서 변경사항 확인

### 수동 배포 (선택사항)

Vercel CLI를 사용하여 수동으로 배포할 수도 있다:

```bash
# Vercel CLI 설치 (최초 1회)
npm i -g vercel

# 배포
vercel
```

### 배포 시점 정리

| 작업 | 로컬 서버 | Vercel 배포 |
|------|----------|------------|
| 코드 수정 | 즉시 반영 (서버 재시작 불필요) | 반영 안 됨 |
| `bundle exec jekyll serve` 실행 | 로컬에서만 접근 가능 | 영향 없음 |
| GitHub에 푸시 | 영향 없음 | **자동 배포 시작** |
| 배포 완료 | - | 전 세계에서 접근 가능 |

**요약:**
- 로컬 서버: 개발/테스트용 (로컬에서만 작동)
- Vercel 배포: GitHub 푸시 시 자동 배포 (전 세계 접근 가능)
- 두 개는 **완전히 별개**로 작동함

배포 완료 후 Vercel 대시보드에서 배포 URL을 확인할 수 있다. 기본 도메인은 `https://your-project.vercel.app` 형식이다.

#### 4. 커스텀 도메인 설정 (선택사항)

1. Vercel 대시보드 → 프로젝트 → **Settings** → **Domains**
2. 원하는 도메인 추가
3. DNS 설정에 따라 도메인을 연결

#### Vercel 설정 파일

프로젝트 루트의 `vercel.json` 파일에 빌드 설정이 포함되어 있다:

- **buildCommand**: Jekyll 빌드 명령어 (`bundle install && bundle exec jekyll build`)
- **outputDirectory**: 빌드 출력 디렉토리 (`_site`)
- **installCommand**: 의존성 설치 명령어 (`gem install bundler && bundle install`)
- **framework**: `null`로 설정하여 커스텀 빌드 사용

**설정 우선순위:**
1. `vercel.json` 파일의 설정 (최우선)
2. Vercel UI에서 수동으로 입력한 설정
3. Vercel의 자동 감지된 프리셋 설정

따라서 UI에서 Jekyll 프리셋이 선택되어 있어도, `vercel.json`이 있으면 해당 파일의 설정이 적용된다. UI의 값은 무시되므로 걱정할 필요가 없다.

#### GitHub Pages와 Vercel 동시 사용

두 플랫폼을 동시에 사용할 수 있다:
- GitHub Pages: `https://rldhkstopic.github.io`
- Vercel: `https://your-project.vercel.app` 또는 커스텀 도메인

`_config.yml`의 `url` 설정은 GitHub Pages용이므로, Vercel에서는 환경 변수나 빌드 시 동적 설정을 사용할 수 있다.

#### Vercel 기능 활용

Vercel은 블로그에 다양한 기능을 제공한다. 자세한 내용은 [Vercel 기능 활용 가이드](docs/VERCEL_FEATURES_GUIDE.md)를 참고한다.

**주요 기능:**

1. **Speed Insights** - 웹사이트 성능 모니터링 (Core Web Vitals 측정)
   - Vercel 대시보드 → Speed Insights 탭에서 활성화
   - LCP, FID, CLS 지표 자동 측정

2. **Analytics** - 웹 분석 도구 (GA4 보완)
   - Vercel 대시보드 → Analytics 탭에서 활성화
   - 실시간 방문자 통계 확인

3. **Preview Deployments** - PR별 미리보기 배포
   - GitHub PR 생성 시 자동으로 미리보기 URL 생성
   - 실제 배포 전 변경사항 검토 가능

4. **Custom Headers** - 보안 헤더 (이미 적용됨)
   - `vercel.json`에 보안 헤더 설정 포함
   - XSS, 클릭재킹 방지 등

5. **Deployment Regions** - 배포 지역 설정
   - 한국 사용자 최적화: 서울 리전(`icn1`) 선택 권장
   - Settings → General → Region에서 설정

6. **Edge Functions** - 전역 서버리스 함수
   - `api/github-oauth.js`는 이미 서버리스 함수로 구현됨
   - 전 세계 엣지 서버에서 실행되어 빠른 응답 제공

자세한 설정 방법과 활용 예시는 `docs/VERCEL_FEATURES_GUIDE.md`를 참고한다.

**빠른 설정 가이드:** Vercel 대시보드에서 설정해야 할 항목은 [Vercel 설정 체크리스트](docs/VERCEL_SETUP_CHECKLIST.md)를 참고한다.
