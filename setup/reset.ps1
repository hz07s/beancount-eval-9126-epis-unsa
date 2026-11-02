# Borra lo generado por setup. Uso: .\reset.ps1 [-Full]
#   sin -Full: venvs, worktrees, examples y logs (conserva clon y Python portable)
#   con -Full: ademas beancount-src y .tools (el siguiente setup vuelve a descargar)
# Solo actua sobre estas rutas fijas junto al script. No toca locks ni scripts.
param([switch]$Full)

$targets = @('.venv-323', '.venv-236', 'beancount-src\v3.2.3', 'beancount-src\v2.3.6', 'examples', 'logs')
if ($Full) { $targets += @('beancount-src', '.tools') }

foreach ($name in $targets) {
    $path = Join-Path $PSScriptRoot $name
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Recurse -Force
        Write-Host "Borrado: $name"
    }
}

$repo = Join-Path $PSScriptRoot 'beancount-src'
if ((Test-Path (Join-Path $repo '.git')) -and (Get-Command git -ErrorAction SilentlyContinue)) {
    & git -C $repo worktree prune
}
Write-Host 'Reset terminado.' -ForegroundColor Green
