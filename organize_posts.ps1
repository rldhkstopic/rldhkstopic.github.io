# _posts folder organization script
$postsDir = "_posts"
if (-not (Test-Path $postsDir)) {
    Write-Host "[ERROR] $postsDir directory not found" -ForegroundColor Red
    exit 1
}

$categoryFiles = @{}

Get-ChildItem -Path $postsDir -Filter "*.md" -File | ForEach-Object {
    $file = $_
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
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

$movedCount = 0
foreach ($category in $categoryFiles.Keys) {
    $categoryDir = Join-Path $postsDir $category
    if (-not (Test-Path $categoryDir)) {
        New-Item -ItemType Directory -Path $categoryDir | Out-Null
    }
    
    Write-Host "[$category] $($categoryFiles[$category].Count) files" -ForegroundColor Cyan
    
    foreach ($file in $categoryFiles[$category]) {
        $dest = Join-Path $categoryDir $file.Name
        if (Test-Path $dest) {
            Write-Host "  [SKIP] $($file.Name)" -ForegroundColor Yellow
        } else {
            Move-Item -Path $file.FullName -Destination $dest
            Write-Host "  [MOVE] $($file.Name) -> $category/" -ForegroundColor Green
            $movedCount++
        }
    }
}

Write-Host "`n[OK] Moved $movedCount files" -ForegroundColor Green
