# 일기 글 재생성 스크립트
# 모든 날짜별로 일기 글을 재생성합니다.

$dates = @(
    "2026-01-03",
    "2026-01-09",
    "2026-01-10",
    "2026-01-12",
    "2026-01-13",
    "2026-01-14"
)

Write-Host "일기 글 재생성 시작..." -ForegroundColor Green
Write-Host "총 $($dates.Count)개 날짜 처리 예정" -ForegroundColor Yellow
Write-Host ""

foreach ($date in $dates) {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "날짜: $date" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    python automation/scripts/daily_diary_agent.py $date
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $date 일기 생성 완료" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] $date 일기 생성 실패" -ForegroundColor Red
    }
    
    Write-Host ""
    Start-Sleep -Seconds 2
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "모든 일기 글 재생성 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
