@echo off
setlocal

echo Starting Geckowo comics pipeline...

echo Downloading comics...
py download_geckowo_comics.py

echo Extracting metadata...
py extract_comic_metadata.py

echo Renaming files with reverse-chron numbers...
py rename_comics.py

echo Pipeline complete!
endlocal
