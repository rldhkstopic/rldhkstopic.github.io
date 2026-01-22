# _posts 폴더 내 파일을 카테고리별로 정리하는 PowerShell 스크립트

$postsDir = "_posts"
if (-not (Test-Path $postsDir)) {
    Write-Host "[ERROR] $postsDir 디렉토리가 없습니다." -ForegroundColor Red
    exit 1
}

$categoryFiles = @{}

# 모든 .md 파일 처리
Get-ChildItem -Path $postsDir -Filter "*.md" -File | ForEach-Object {
    $file = $_
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # Front matter에서 category 추출
    if ($content -match '(?s)---\s+category:\s+(\S+)') {
        $category = $matches[1].Trim()
    } elseif ($content -match '(?s)category:\s+(\S+)') {
        $category = $matches[1].Trim()
    } else {
        $category = "uncategorized"
    }
    
    if (-not $categoryFiles.ContainsKey($category)) {
        $categoryFiles[$category] = @()
    }
    $categoryFiles[$category] += $file
}

# 카테고리별 폴더 생성 및 파일 이동
$movedCount = 0
foreach ($category in $categoryFiles.Keys) {
    $categoryDir = Join-Path $postsDir $category
    if (-not (Test-Path $categoryDir)) {
        New-Item -ItemType Directory -Path $categoryDir | Out-Null
    }
    
    Write-Host "`n[$category] $($categoryFiles[$category].Count)개 파일" -ForegroundColor Cyan
    
    foreach ($file in $categoryFiles[$category]) {
        $dest = Join-Path $categoryDir $file.Name
        if (Test-Path $dest) {
            Write-Host "  [SKIP] $($file.Name) (이미 존재)" -ForegroundColor Yellow
        } else {
            Move-Item -Path $file.FullName -Destination $dest
            Write-Host "  [MOVE] $($file.Name) -> $category/" -ForegroundColor Green
            $movedCount++
        }
    }
}

Write-Host "`n[OK] 총 $movedCount 개 파일 이동 완료" -ForegroundColor Green
Write-Host "[INFO] 카테고리별 폴더 구조:" -ForegroundColor Cyan
foreach ($category in ($categoryFiles.Keys | Sort-Object)) {
    Write-Host "  _posts/$category/ ($($categoryFiles[$category].Count)개)" -ForegroundColor White
}
