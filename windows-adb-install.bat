@echo off
setlocal EnableDelayedExpansion
title Universal ADB ^& Fastboot Installer for Windows

:: 1. Check for Administrator Privileges and Auto-Elevate if needed
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [*] Requesting Administrator privileges...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: 2. Run the main installation logic via embedded PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ErrorActionPreference = 'Stop';" ^
    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;" ^
    "Clear-Host;" ^
    "Write-Host '==================================================' -ForegroundColor Cyan;" ^
    "Write-Host '  Universal ADB & Fastboot Installer for Windows  ' -ForegroundColor Cyan;" ^
    "Write-Host '==================================================' -ForegroundColor Cyan;" ^
    "$os = (Get-WmiObject Win32_OperatingSystem).Caption;" ^
    "Write-Host \"[*] System Detected: $os\" -ForegroundColor Yellow;" ^
    "$installed = $false;" ^
    "if (Get-Command winget -ErrorAction SilentlyContinue) {" ^
    "    Write-Host '[*] Package Manager Detected: Winget' -ForegroundColor Yellow;" ^
    "    Write-Host '[*] Installing Android Platform Tools via Winget...' -ForegroundColor Green;" ^
    "    winget install --id Google.PlatformTools --accept-package-agreements --accept-source-agreements -e;" ^
    "    if ($LASTEXITCODE -eq 0) { $installed = $true }" ^
    "}" ^
    "if (-not $installed -and (Get-Command choco -ErrorAction SilentlyContinue)) {" ^
    "    Write-Host '[*] Package Manager Detected: Chocolatey' -ForegroundColor Yellow;" ^
    "    Write-Host '[*] Installing ADB via Chocolatey...' -ForegroundColor Green;" ^
    "    choco install adb -y;" ^
    "    if ($LASTEXITCODE -eq 0) { $installed = $true }" ^
    "}" ^
    "if (-not $installed -and (Get-Command scoop -ErrorAction SilentlyContinue)) {" ^
    "    Write-Host '[*] Package Manager Detected: Scoop' -ForegroundColor Yellow;" ^
    "    Write-Host '[*] Installing ADB via Scoop...' -ForegroundColor Green;" ^
    "    scoop install adb;" ^
    "    if ($LASTEXITCODE -eq 0) { $installed = $true }" ^
    "}" ^
    "if (-not $installed) {" ^
    "    Write-Host '[*] Using Direct Official Google Repository (Compatible with Win 7/8/10/11)...' -ForegroundColor Yellow;" ^
    "    $url = 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip';" ^
    "    $zipPath = Join-Path $env:TEMP 'platform-tools.zip';" ^
    "    $installDir = 'C:\adb';" ^
    "    Write-Host '[*] Downloading latest platform-tools from Google...' -ForegroundColor Green;" ^
    "    (New-Object System.Net.WebClient).DownloadFile($url, $zipPath);" ^
    "    Write-Host '[*] Extracting files to C:\adb...' -ForegroundColor Green;" ^
    "    if (Test-Path $installDir) { Remove-Item -Path $installDir -Recurse -Force };" ^
    "    Add-Type -AssemblyName System.IO.Compression.FileSystem;" ^
    "    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipPath, $installDir);" ^
    "    Remove-Item $zipPath -Force;" ^
    "    $targetPath = Join-Path $installDir 'platform-tools';" ^
    "    $sysPath = [Environment]::GetEnvironmentVariable('Path', 'Machine');" ^
    "    if ($sysPath -notlike \"*$targetPath*\") {" ^
    "        Write-Host '[*] Adding ADB to System Environment PATH...' -ForegroundColor Green;" ^
    "        [Environment]::SetEnvironmentVariable('Path', \"$sysPath;$targetPath\", 'Machine');" ^
    "    }" ^
    "    $env:Path += \";$targetPath\";" ^
    "}" ^
    "Write-Host '--------------------------------------------------' -ForegroundColor Cyan;" ^
    "$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User') + ';C:\adb\platform-tools';" ^
    "if (Get-Command adb -ErrorAction SilentlyContinue) {" ^
    "    Write-Host '[✓] Installation completed and verified successfully!' -ForegroundColor Green;" ^
    "    Write-Host '[i] Installed Version Details:' -ForegroundColor Yellow;" ^
    "    adb --version | Select-Object -First 2;" ^
    "    if (Get-Command fastboot -ErrorAction SilentlyContinue) {" ^
    "        Write-Host '[✓] Fastboot is also verified and ready!' -ForegroundColor Green;" ^
    "    }" ^
    "} else {" ^
    "    Write-Host '[X] Verification Failed: ADB could not be installed.' -ForegroundColor Red;" ^
    "    exit 1;" ^
    "}" ^
    "Write-Host '==================================================' -ForegroundColor Cyan;"

echo.
pause
