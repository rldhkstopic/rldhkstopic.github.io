# rldhkstopic 블로그

## 로컬 서버 실행

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

## 배포

GitHub Pages에 자동으로 배포됩니다. `main` 브랜치에 푸시하면 자동으로 빌드됩니다.

```bash
git add .
git commit -m "변경사항"
git push origin main
```

배포 완료 후 `https://rldhkstopic.github.io`에서 확인할 수 있습니다.
