@echo off
setlocal
set "SCRIPT_DIR=%~dp0"

echo Starting Geckowo comics pipeline...

echo Downloading comics...
py "%SCRIPT_DIR%download_geckowo_comics.py"

echo Extracting metadata...
py "%SCRIPT_DIR%extract_comic_metadata.py"

echo Renaming files with reverse-chron numbers...
py "%SCRIPT_DIR%rename_comics.py"

echo Pipeline complete!
endlocal
