# Build check for the latam-valuation-engine CANVAS wizard frontend (Windows).
# Usage:   .\build_check.ps1
# Exits 0 on success.

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "[build_check] node:  $(node --version)"
Write-Host "[build_check] npm:   $(npm --version)"
Write-Host "[build_check] cwd:   $ScriptDir"

Write-Host "[build_check] Step 1/3 - npm install"
npm install --no-audit --no-fund
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[build_check] Step 2/3 - typecheck"
npm run typecheck
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[build_check] Step 3/3 - build"
npm run build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[build_check] OK - dist/ produced"
Get-ChildItem dist | Format-Table -AutoSize
