@echo off
rem Build Driver Studio as a standalone Windows .exe.
rem
rem Prereqs:
rem   pip install -r gui\requirements.txt
rem
rem Output:
rem   packaging\dist\driver_studio.exe
rem   (also: packaging\build\ with intermediate PyInstaller artifacts)
rem
rem Run from the repo root OR from inside packaging\. The spec file resolves
rem the repo path from SPECPATH, so cwd does not matter -- but the dist/
rem and build/ folders are created relative to cwd. We cd into packaging/
rem so the artifacts land alongside the spec, keeping the top-level clean.

setlocal
pushd "%~dp0"

echo === Driver Studio EXE build ===
echo Spec:    %~dp0driver_studio.spec
echo Output:  %~dp0dist\driver_studio.exe

where pyinstaller >nul 2>&1
if errorlevel 1 (
  echo ERROR: pyinstaller is not on PATH.
  echo        Install it with:  pip install -r gui\requirements.txt
  echo        Then re-run this script.
  popd
  exit /b 1
)

pyinstaller --clean --noconfirm driver_studio.spec
set BUILD_RC=%ERRORLEVEL%

if %BUILD_RC% neq 0 (
  echo === Build failed with rc=%BUILD_RC% ===
  popd
  exit /b %BUILD_RC%
)

echo === Build succeeded ===
echo EXE at: %~dp0dist\driver_studio.exe

popd
endlocal
exit /b 0
