for /f "delims=" %%a in ('GetOutFiles all') do set FILES=%%a

cd /D "%~dp0"
cd ../../../

pipenv run python processAfterEncode.py
