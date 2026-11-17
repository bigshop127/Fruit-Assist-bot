# 把輔助器打包成「免裝 Python」的單一 .exe，給朋友用。
#
#   powershell -ExecutionPolicy Bypass -File tools\build_exe.ps1 [-Python <venv 裡的 python.exe>]
#
# 不給 -Python 就在 %TEMP%\fruit2048-buildenv 建一個乾淨的 venv（只裝 numpy/pillow/mss/pyinstaller，
# 打出來的 exe 比較小，也不會把你全域環境裡的雜套件包進去）。
# 產出：fruit2048\dist\水果2048輔助器.exe
param([string]$Python = '')
$ErrorActionPreference = 'Stop'
$AppDir = Split-Path -Parent $PSScriptRoot

if (-not $Python) {
    $venv = Join-Path $env:TEMP 'fruit2048-buildenv'
    if (-not (Test-Path "$venv\Scripts\python.exe")) {
        python -m venv $venv
        & "$venv\Scripts\python.exe" -m pip install -q -r "$AppDir\requirements.txt" pyinstaller
    }
    $Python = "$venv\Scripts\python.exe"
}

Push-Location $AppDir
try {
    & $Python -m PyInstaller --noconfirm --clean --onefile --windowed `
        --name '水果2048輔助器' --icon (Join-Path $AppDir 'icon.ico') `
        --workpath "$env:TEMP\fruit2048-pyi-build" --specpath "$env:TEMP\fruit2048-pyi-build" `
        --distpath dist app.py
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller 失敗（$LASTEXITCODE）" }
} finally { Pop-Location }
