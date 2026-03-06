param(
    [switch]$SkipDownload
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting Geckowo comics pipeline..." -ForegroundColor Cyan

# Step 1: Download raw files (unless skipping)
if (-not $SkipDownload) {
    Write-Host "Downloading comics..." -ForegroundColor Cyan
    py (Join-Path $scriptDir "download_geckowo_comics.py")
}

# Step 2: Extract metadata (newest-first numbering)
Write-Host "Extracting metadata..." -ForegroundColor Cyan
py (Join-Path $scriptDir "extract_comic_metadata.py")

# Step 3: Apply numbering to filenames
Write-Host "Renaming files with reverse-chron numbers..." -ForegroundColor Cyan
py (Join-Path $scriptDir "rename_comics.py")

Write-Host "Pipeline complete!" -ForegroundColor Green
