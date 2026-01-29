# 카테고리별로 포스트를 디렉터리로 정리하는 스크립트
# Jekyll은 _posts 내부 서브디렉터리를 지원하지 않으므로,
# 카테고리별 컬렉션 디렉터리를 생성합니다.

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$postsDir = Join-Path $projectRoot "_posts"

# 카테고리별 컬렉션 디렉터리 생성
$collections = @{
    "daily" = "_posts_daily"
    "dev" = "_posts_dev"
    "study" = "_posts_study"
    "document" = "_posts_document"
    "stock" = "_posts_stock"
}

Write-Host "카테고리별 포스트 정리 시작..." -ForegroundColor Cyan

# 컬렉션 디렉터리 생성
foreach ($category in $collections.Keys) {
    $collectionDir = Join-Path $projectRoot $collections[$category]
    if (-not (Test-Path $collectionDir)) {
        New-Item -ItemType Directory -Path $collectionDir -Force | Out-Null
        Write-Host "[OK] 디렉터리 생성: $collectionDir" -ForegroundColor Green
    }
}

# 포스트 파일 읽기 및 카테고리별로 이동
$movedCount = 0
$skippedCount = 0

Get-ChildItem -Path $postsDir -Filter "*.md" | ForEach-Object {
    $file = $_
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # Front Matter에서 category 추출
    if ($content -match '(?s)---\s+.*?category:\s*(\w+)') {
        $category = $matches[1].ToLower()
        
        if ($collections.ContainsKey($category)) {
            $targetDir = Join-Path $projectRoot $collections[$category]
            $targetPath = Join-Path $targetDir $file.Name
            
            if (-not (Test-Path $targetPath)) {
                Move-Item -Path $file.FullName -Destination $targetPath -Force
                Write-Host "[OK] 이동: $($file.Name) -> $($collections[$category])" -ForegroundColor Green
                $movedCount++
            } else {
                Write-Host "[SKIP] 이미 존재: $targetPath" -ForegroundColor Yellow
                $skippedCount++
            }
        } else {
            Write-Host "[WARN] 알 수 없는 카테고리: $category ($($file.Name))" -ForegroundColor Yellow
            $skippedCount++
        }
    } else {
        Write-Host "[WARN] category를 찾을 수 없음: $($file.Name)" -ForegroundColor Yellow
        $skippedCount++
    }
}

Write-Host "`n정리 완료!" -ForegroundColor Cyan
Write-Host "이동: $movedCount개, 스킵: $skippedCount개" -ForegroundColor Cyan
Write-Host "`n주의: Jekyll 컬렉션 설정이 _config.yml에 추가되어야 합니다." -ForegroundColor Yellow
