# PowerShell script to check for exposed API keys before commit
# Usage: .\scripts\check-secrets.ps1

$ErrorActionPreference = "Stop"

# API key patterns to detect
$patterns = @(
    "AIza[0-9A-Za-z_-]{35}",
    "sk-[0-9A-Za-z]{32,}",
    "ghp_[0-9A-Za-z]{36}",
    "[0-9a-f]{40}",
    "client_secret.*=.*[0-9a-fA-F]{40}",
    "GEMINI_API_KEY.*=.*AIza"
)

# Files to check (staged files)
$stagedFiles = git diff --cached --name-only --diff-filter=ACM

if ($stagedFiles.Count -eq 0) {
    Write-Host "No staged files to check." -ForegroundColor Green
    exit 0
}

$foundSecrets = $false

foreach ($file in $stagedFiles) {
    # Skip binary files
    if (git diff --cached --numstat $file | Select-String "^-") {
        continue
    }
    
    # Get file content
    $content = git show ":$file" 2>$null
    if (-not $content) {
        continue
    }
    
    # Check each pattern
    foreach ($pattern in $patterns) {
        if ($content -match $pattern) {
            Write-Host "❌ ERROR: Potential API key or secret detected in $file" -ForegroundColor Red
            Write-Host "   Pattern matched: $pattern" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "⚠️  보안: API 키나 시크릿을 커밋하지 마세요!" -ForegroundColor Red
            Write-Host "   환경 변수나 GitHub Secrets를 사용하세요." -ForegroundColor Yellow
            Write-Host ""
            $foundSecrets = $true
        }
    }
}

if ($foundSecrets) {
    exit 1
}

Write-Host "✅ No secrets detected in staged files." -ForegroundColor Green
exit 0

