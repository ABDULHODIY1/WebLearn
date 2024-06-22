@REM @echo off
@REM setlocal

@REM rem Python versiyasi va yuklab olish havolasi
@REM set "PYTHON_VERSION=3.10.0"
@REM set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe"

@REM rem Vaqtinchalik yuklab olish va o'rnatish katalogini yaratish
@REM set "TEMP_DIR=%~dp0temp_python"
@REM mkdir "%TEMP_DIR%"
@REM cd /d "%TEMP_DIR%"

@REM rem Pythonni yuklab olish
@REM echo Yuklab olinmoqda...
@REM powershell -command "Invoke-WebRequest -Uri %PYTHON_URL% -OutFile python_installer.exe"

@REM rem Pythonni o'rnatish
@REM echo O'rnatilmoqda...
@REM python_installer.exe /quiet InstallAllUsers=1 PrependPath=1

@REM rem PATH muammosini hal qilish uchun kiritamiz
@REM setx PATH "%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python%PYTHON_VERSION%"

@REM rem Temp katalogni tozalash
@REM cd /d %~dp0
@REM rmdir /s /q "%TEMP_DIR%"

@REM rem Kutubhonalarni yuklab olish
@REM echo Kutubhonalarni yuklab olinmoqda...
@REM python -m pip install numpy opencv-python datetime requests pyserial pyinstaller

@REM rem Python faylini .exe ga aylantirish
@REM echo Detector faylini .exe ga aylantirilmoqda...
@REM pyinstaller --onefile --noconsole detector.py

@REM rem O'rnatilgan Pythonni tekshirish
@REM echo O'rnatish tugadi.
@REM python --version

@REM endlocal
@REM pause
@echo off
setlocal

rem Python versiyasi va yuklab olish havolasi
set "PYTHON_VERSION=3.10.0"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe"

rem Python o'rnatilganligini tekshirish
python --version 2>nul
if %errorlevel% neq 0 (
    rem Pythonni o'rnatish jarayoni
    echo Python o'rnatilmagan, yuklab olinmoqda va o'rnatilmoqda...

    rem Vaqtinchalik yuklab olish va o'rnatish katalogini yaratish
    set "TEMP_DIR=%~dp0temp_python"
    mkdir "%TEMP_DIR%"
    cd /d "%TEMP_DIR%"

    rem Pythonni yuklab olish
    powershell -command "Invoke-WebRequest -Uri %PYTHON_URL% -OutFile python_installer.exe"

    rem Pythonni o'rnatish
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1

    rem PATH muammosini hal qilish uchun kiritamiz
    setx PATH "%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python%PYTHON_VERSION%"

    rem Temp katalogni tozalash
    cd /d %~dp0
    rmdir /s /q "%TEMP_DIR%"

    rem O'rnatilgan Pythonni tekshirish
    python --version
) else (
    echo Python allaqachon o'rnatilgan.
)

rem Kutubhonalar o'rnatilganligini tekshirish
pip show numpy 2>nul || set NEED_INSTALL=true
pip show opencv-python 2>nul || set NEED_INSTALL=true
pip show datetime 2>nul || set NEED_INSTALL=true
pip show requests 2>nul || set NEED_INSTALL=true
pip show pyserial 2>nul || set NEED_INSTALL=true
pip show pyinstaller 2>nul || set NEED_INSTALL=true

if defined NEED_INSTALL (
    echo Kutubhonalarni yuklab olinmoqda...
    python -m pip install numpy opencv-python datetime requests pyserial pyinstaller
) else (
    echo Kutubhonalar allaqachon o'rnatilgan.
)

rem Python faylini .exe ga aylantirish
if exist detector.py (
    echo Detector faylini .exe ga aylantirilmoqda...
    pyinstaller --onefile --noconsole detector.py
) else (
    echo detector.py fayli topilmadi.
)

endlocal
pause
