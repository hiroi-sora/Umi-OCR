@echo off
REM º§ªÓ–Èƒ‚ª∑æ≥
call E:/Code/MyGit/Umi-OCR//venv//Scripts//activate.bat
nuitka E:/Code/MyGit/Umi-OCR/main.py --standalone --windows-disable-console --include-data-dir=PaddleOCR-json=PaddleOCR-json --include-data-files=PaddleOCR-json/*dll=PaddleOCR-json/ --plugin-enable=tk-inter --onefile
pause