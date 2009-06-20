rd gmbox /S /Q
python win_packer.py py2exe
xcopy c:\\GTK\etc gmbox\etc /E /I /R
xcopy c:\\GTK\lib gmbox\lib /E /I /R
rd build /S /Q
