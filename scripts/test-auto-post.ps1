# Auto Post 로컬 테스트 스크립트 (Windows PowerShell)
# 사용법: .\scripts\test-auto-post.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Auto Post 로컬 테스트 시작" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Python 확인
Write-Host "[1/5] Python 확인 중..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Python이 설치되어 있지 않습니다." -ForegroundColor Red
    Write-Host "Python 3.11 이상을 설치하세요: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] $pythonVersion" -ForegroundColor Green
Write-Host ""

# 환경 변수 확인
Write-Host "[2/5] GEMINI_API_KEY 확인 중..." -ForegroundColor Yellow
$apiKey = $env:GEMINI_API_KEY
if (-not $apiKey) {
    Write-Host "[ERROR] GEMINI_API_KEY 환경 변수가 설정되지 않았습니다." -ForegroundColor Red
    Write-Host ""
    Write-Host "다음 명령어로 환경 변수를 설정하세요:" -ForegroundColor Yellow
    Write-Host '  $env:GEMINI_API_KEY = "<YOUR_GEMINI_API_KEY>"' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "보안상 키를 스크립트에 하드코딩하지 마세요." -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] GEMINI_API_KEY가 설정되어 있습니다." -ForegroundColor Green
Write-Host ""

# 의존성 설치
Write-Host "[3/5] Python 패키지 설치 중..." -ForegroundColor Yellow
$requirementsPath = ".github\scripts\requirements.txt"
if (-not (Test-Path $requirementsPath)) {
    Write-Host "[ERROR] requirements.txt를 찾을 수 없습니다: $requirementsPath" -ForegroundColor Red
    exit 1
}

Write-Host "pip install 실행 중..." -ForegroundColor Gray
python -m pip install -r $requirementsPath
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] 패키지 설치에 실패했습니다." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] 패키지 설치 완료" -ForegroundColor Green
Write-Host ""

# 프로젝트 구조 확인
Write-Host "[4/5] 프로젝트 구조 확인 중..." -ForegroundColor Yellow
$postsDir = "_posts"
if (-not (Test-Path $postsDir)) {
    Write-Host "[WARN] _posts 디렉토리가 없습니다. 생성합니다..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $postsDir | Out-Null
}
Write-Host "[OK] 프로젝트 구조 확인 완료" -ForegroundColor Green
Write-Host ""

# 테스트 실행
Write-Host "[5/5] Auto Post 테스트 실행 중..." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$scriptPath = ".github\scripts\test_local.py"
python $scriptPath

$exitCode = $LASTEXITCODE
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "[SUCCESS] 테스트 완료!" -ForegroundColor Green
} else {
    Write-Host "[FAILED] 테스트 실패 (Exit Code: $exitCode)" -ForegroundColor Red
    Write-Host ""
    Write-Host "문제 해결:" -ForegroundColor Yellow
    Write-Host "1. GEMINI_API_KEY가 올바른지 확인" -ForegroundColor Gray
    Write-Host "2. 인터넷 연결 확인" -ForegroundColor Gray
    Write-Host "3. Python 패키지가 올바르게 설치되었는지 확인" -ForegroundColor Gray
    Write-Host "4. 에러 메시지를 자세히 확인" -ForegroundColor Gray
}
Write-Host "============================================================" -ForegroundColor Cyan

exit $exitCode

