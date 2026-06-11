$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot
$NoAlias = $args -contains "--no-alias"
$BinDir = Join-Path $env:LOCALAPPDATA "CoreUtils\bin"
$VenvDir = Join-Path $env:LOCALAPPDATA "pushguard\venv"
$Launcher = Join-Path $BinDir "pushguard.cmd"
$AliasLauncher = Join-Path $BinDir "pushg.cmd"

if (-not (Test-Path (Join-Path $Root ".git"))) {
    throw "Please run init.ps1 from the repository root of pushguard."
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git is required." }
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python 3 is required." }

New-Item -ItemType Directory -Force -Path (Split-Path $VenvDir -Parent) | Out-Null
python -m venv $VenvDir
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
& $VenvPython -m pip install -U pip
& $VenvPython -m pip install -U $Root
$PushguardExe = Join-Path $VenvDir "Scripts\pushguard.exe"

New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
@"
@echo off
"$PushguardExe" %*
"@ | Set-Content -Path $Launcher -Encoding ASCII

if (-not $NoAlias) {
@"
@echo off
"$PushguardExe" %*
"@ | Set-Content -Path $AliasLauncher -Encoding ASCII
}

New-Item -ItemType Directory -Force -Path (Join-Path $Root ".pushguard\reports") | Out-Null
Write-Host "Done. Add $BinDir to PATH if needed."
