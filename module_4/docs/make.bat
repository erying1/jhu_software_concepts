@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
    set SPHINXBUILD=sphinx-build
)
set BUILDDIR=_build
set ALLSPHINXOPTS=-d %BUILDDIR%/doctrees %SPHINXOPTS% .
set I18NSPHINXOPTS=%SPHINXOPTS% .

if "%1" == "" goto help

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
    echo.
    echo.The 'sphinx-build' command was not found. Make sure you have Sphinx installed.
    goto end
)

if "%1" == "html" (
    %SPHINXBUILD% -b html %ALLSPHINXOPTS% %BUILDDIR%/html
    goto end
)

:help
echo.Please use `make.bat target` where target is one of
echo.  html
echo.  latex
echo.  clean
echo.  linkcheck

:end
popd
