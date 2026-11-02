# Ejecuta un comando dentro del venv de una version, sin alterar la sesion.
# Ejemplo: .\run.ps1 -Version 3.2.3 -Command "bean-check archivo.beancount"
# El comando se ejecuta en la carpeta actual. Solo ASCII: ver nota en setup.ps1.
param(
    [Parameter(Mandatory = $true)][ValidateSet('3.2.3', '2.3.6')][string]$Version,
    [Parameter(Mandatory = $true)][string]$Command
)

$venv = Join-Path $PSScriptRoot ('.venv-' + $Version.Replace('.', ''))
$scripts = Join-Path $venv 'Scripts'
if (-not (Test-Path (Join-Path $scripts 'python.exe'))) {
    Write-Host "No existe $venv. Ejecuta primero .\setup.ps1" -ForegroundColor Red
    exit 1
}

# Se ajusta PATH en lugar de usar Activate.ps1, que la politica de ejecucion podria bloquear.
$saved = @{ Path = $env:Path; VIRTUAL_ENV = $env:VIRTUAL_ENV; PYTHONUTF8 = $env:PYTHONUTF8 }
$env:Path = "$scripts;$env:Path"
$env:VIRTUAL_ENV = $venv
$env:PYTHONUTF8 = '1'
$ok = $true
try {
    $global:LASTEXITCODE = 0
    # Stop: sin esto, un comando inexistente terminaria con codigo de salida 0.
    Invoke-Expression $Command -ErrorAction Stop
    $code = $global:LASTEXITCODE
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    $ok = $false
    $code = 0
} finally {
    $env:Path = $saved.Path
    $env:VIRTUAL_ENV = $saved.VIRTUAL_ENV
    $env:PYTHONUTF8 = $saved.PYTHONUTF8
}
if ($code -ne 0) { exit $code }
if (-not $ok) { exit 1 }
exit 0
