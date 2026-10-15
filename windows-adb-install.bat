@echo off
setlocal EnableDelayedExpansion
title Universal ADB ^& Fastboot Installer for Windows

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [*] Requesting Administrator privileges...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ErrorActionPreference = 'Stop';" ^
    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;" ^
    "Clear-Host;" ^
    "Write-Host '==================================================' -ForegroundColor Cyan;" ^
    "Write-Host '  Universal ADB & Fastboot Installer for Windows  ' -ForegroundColor Cyan;" ^
    "Write-Host '==================================================' -ForegroundColor Cyan;" ^
    "$installed = $false;" ^
    "if (Get-Command winget -ErrorAction SilentlyContinue) {" ^
    "    Write-Host '[*] Installing via Winget...' -ForegroundColor Green;" ^
    "    winget install --id Google.PlatformTools --accept-package-agreements --accept-source-agreements -e;" ^
    "    if ($LASTEXITCODE -eq 0) { $installed = $true }" ^
    "}" ^
    "if (-not $installed -and (Get-Command choco -ErrorAction SilentlyContinue)) {" ^
    "    Write-Host '[*] Installing via Chocolatey...' -ForegroundColor Green;" ^
    "    choco install adb -y;" ^
    "    if ($LASTEXITCODE -eq 0) { $installed = $true }" ^
    "}" ^
    "if (-not $installed -and (Get-Command scoop -ErrorAction SilentlyContinue)) {" ^
    "    Write-Host '[*] Installing via Scoop...' -ForegroundColor Green;" ^
    "    scoop install adb;" ^
    "    if ($LASTEXITCODE -eq 0) { $installed = $true }" ^
    "}" ^
    "if (-not $installed) {" ^
    "    Write-Host '[*] Downloading directly from Google Repository...' -ForegroundColor Yellow;" ^
    "    $url = 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip';" ^
    "    $zipPath = Join-Path $env:TEMP 'platform-tools.zip';" ^
    "    $installDir = 'C:\adb';" ^
    "    (New-Object System.Net.WebClient).DownloadFile($url, $zipPath);" ^
    "    if (Test-Path $installDir) { Remove-Item -Path $installDir -Recurse -Force };" ^
    "    Add-Type -AssemblyName System.IO.Compression.FileSystem;" ^
    "    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipPath, $installDir);" ^
    "    Remove-Item $zipPath -Force;" ^
    "    $targetPath = Join-Path $installDir 'platform-tools';" ^
    "    $sysPath = [Environment]::GetEnvironmentVariable('Path', 'Machine');" ^
    "    if ($sysPath -notlike \"*$targetPath*\") {" ^
    "        [Environment]::SetEnvironmentVariable('Path', \"$sysPath;$targetPath\", 'Machine');" ^
    "    }" ^
    "}" ^
    "$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';C:\adb\platform-tools';" ^
    "if (Get-Command adb -ErrorAction SilentlyContinue) {" ^
    "    Write-Host '[✓] Installation completed and verified!' -ForegroundColor Green;" ^
    "    adb --version | Select-Object -First 2;" ^
    "} else {" ^
    "    Write-Host '[X] Verification Failed!' -ForegroundColor Red;" ^
    "    exit 1;" ^
    "}"

echo.
pause
