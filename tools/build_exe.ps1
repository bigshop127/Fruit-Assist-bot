# 把輔助器打包成「免裝 Python」的單一 .exe，中文版跟英文版各一支，給朋友用。
#
#   powershell -ExecutionPolicy Bypass -File tools\build_exe.ps1 [-Python <venv 裡的 python.exe>] [-Lang zh|en|all]
#
# 不給 -Python 就在 %TEMP%\fruit2048-buildenv 建一個乾淨的 venv（只裝 numpy/pillow/mss/pyinstaller，
# 打出來的 exe 比較小，也不會把你全域環境裡的雜套件包進去）。
# 產出：fruit2048\dist\水果2048輔助器.exe（中文）、fruit2048\dist\Fruit2048Assistant.exe（English）
#
# 語言是打包時寫進 exe 的預設值（暫時產生 _build_lang.py，打包完就刪掉）；
# 使用者之後還是可以在 config.json 加 "language": "zh" / "en" 自己換。
param([string]$Python = '', [ValidateSet('zh', 'en', 'all')][string]$Lang = 'all')
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

$targets = @(
    @{ Lang = 'zh'; Name = '水果2048輔助器' },
    @{ Lang = 'en'; Name = 'Fruit2048Assistant' }
) | Where-Object { $Lang -eq 'all' -or $_.Lang -eq $Lang }

$langFile = Join-Path $AppDir '_build_lang.py'
Push-Location $AppDir
try {
    foreach ($t in $targets) {
        Set-Content -Path $langFile -Value "LANG = `"$($t.Lang)`"" -Encoding ascii
        & $Python -m PyInstaller --noconfirm --clean --onefile --windowed `
            --name $t.Name --icon (Join-Path $AppDir 'icon.ico') `
            --hidden-import _build_lang `
            --workpath "$env:TEMP\fruit2048-pyi-build" --specpath "$env:TEMP\fruit2048-pyi-build" `
            --distpath dist app.py
        if ($LASTEXITCODE -ne 0) { throw "PyInstaller 失敗（$($t.Name)，$LASTEXITCODE）" }
    }
} finally {
    Remove-Item $langFile -ErrorAction SilentlyContinue
    Pop-Location
}
