# Monta el entorno completo. Uso: .\setup.ps1 [argumentos de bootstrap.py]
# Compatible con PowerShell 5.1 y 7+. Solo ASCII: 5.1 lee los .ps1 sin BOM como ANSI.

function Find-HostPython {
    $check = 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'
    foreach ($candidate in @(@('py', '-3.12'), @('py', '-3.11'), @('py', '-3'), @('python'), @('python3'))) {
        if (-not (Get-Command $candidate[0] -ErrorAction SilentlyContinue)) { continue }
        $extra = @($candidate | Select-Object -Skip 1)
        & $candidate[0] @extra -c $check 2>$null
        if ($LASTEXITCODE -eq 0) { return , $candidate }
    }
    return $null
}

Write-Host '== Entorno Beancount 3.2.3 + 2.3.6 ==' -ForegroundColor Cyan

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host 'Falta Git. Instalalo y abre una terminal nueva:' -ForegroundColor Red
    Write-Host '  winget install -e --id Git.Git --scope user' -ForegroundColor Yellow
    exit 1
}

$python = Find-HostPython
if (-not $python) {
    Write-Host 'Falta Python >= 3.11. Instalalo y abre una terminal nueva:' -ForegroundColor Red
    Write-Host '  winget install -e --id Python.Python.3.12 --scope user' -ForegroundColor Yellow
    exit 1
}

$hostArgs = @($python | Select-Object -Skip 1)
& $python[0] @hostArgs (Join-Path $PSScriptRoot 'bootstrap.py') @args
$code = $LASTEXITCODE

if ($code -eq 0) {
    Write-Host "`nEntorno listo. Ejemplo:" -ForegroundColor Green
    Write-Host '  .\run.ps1 -Version 3.2.3 -Command "bean-check --version"' -ForegroundColor Green
} else {
    Write-Host "`nLa instalacion fallo (codigo $code). Revisa los mensajes y la carpeta logs\." -ForegroundColor Red
}
exit $code
