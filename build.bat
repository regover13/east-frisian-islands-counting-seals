@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM Frisian Islands Seals – MSFS Package Build Script
REM MSFS 2020: requires BGL compilation via fspackagetool
REM MSFS 2024: works without compilation (PackageSources read directly)
REM ─────────────────────────────────────────────────────────────────────────────

setlocal

set SDK_TOOL="D:\MSFS SDK\Tools\bin\fspackagetool.exe"
set PKG_SRC=E:\Addons\Community\counting-seals-frisian-islands\PackageSources\seals-frisian

echo.
echo [*] Frisian Islands Seals – Package Build
echo.

REM Step 1: Regenerate placement XML with fresh random positions
echo [1/3] Regenerating seal positions...
cd /d "%~dp0"
python generate_seals.py
if errorlevel 1 (
    echo [ERROR] Python script failed. Is Python 3.9+ installed?
    pause & exit /b 1
)

REM Step 2: Compile with fspackagetool (produces BGL for MSFS 2020 compatibility)
echo.
echo [2/3] Compiling BGL (MSFS 2020 compatibility)...
%SDK_TOOL% "%PKG_SRC%"
if errorlevel 1 (
    echo [WARNING] fspackagetool returned an error – check output above.
    echo           MSFS 2024 will still work via PackageSources XML directly.
) else (
    echo [OK] BGL compiled successfully.
)

echo.
echo [3/3] Done.
echo       Package: E:\Addons\Community\counting-seals-frisian-islands\
echo       Airports: EDWB EDWJ EDWY EDWI EDWL EDWS EDWW
echo.
pause
