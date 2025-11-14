# Скрипт для генерации доверенных SSL-сертификатов для localhost (PowerShell)

Write-Host "Checking mkcert installation..." -ForegroundColor Cyan

if (-not (Get-Command mkcert -ErrorAction SilentlyContinue)) {
    Write-Host "mkcert not found. Please install it:" -ForegroundColor Yellow
    Write-Host "  Option 1: Download from https://github.com/FiloSottile/mkcert/releases" -ForegroundColor Green
    Write-Host "  Option 2: choco install mkcert (if Chocolatey is installed)" -ForegroundColor Green
    Write-Host "  Option 3: scoop install mkcert (if Scoop is installed)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Manual installation:" -ForegroundColor Yellow
    Write-Host "  1. Download mkcert-v1.4.4-windows-amd64.exe from GitHub releases" -ForegroundColor Cyan
    Write-Host "  2. Rename to mkcert.exe" -ForegroundColor Cyan
    Write-Host "  3. Add to PATH or place in this directory" -ForegroundColor Cyan
    exit 1
}

Write-Host "Creating local CA (if not exists)..." -ForegroundColor Cyan
mkcert -install

Write-Host "Generating certificates for localhost and 178.72.139.15..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path ./ssl | Out-Null
mkcert -key-file ./ssl/localhost-key.pem -cert-file ./ssl/localhost.pem localhost 127.0.0.1 ::1 178.72.139.15

Write-Host "Certificates created in ./miniapp/caddy/ssl/" -ForegroundColor Green
Write-Host "Now restart: docker compose restart caddy" -ForegroundColor Green

