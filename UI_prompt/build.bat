@echo off
echo Building OnePage.py...
nuitka --onefile --enable-plugin=pyside6 --windows-console-mode=disable --experimental=use_pefile --experimental=use_pefile_recurse --experimental=use_pefile_fullrecurse OnePage.py

echo Building TwoPage.py...
nuitka --onefile --enable-plugin=pyside6 --windows-console-mode=disable --experimental=use_pefile --experimental=use_pefile_recurse --experimental=use_pefile_fullrecurse TwoPage.py

echo Build process completed.
pause
