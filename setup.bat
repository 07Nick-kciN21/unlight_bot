@echo off
echo 正在建置 Unlight 自動化環境...

REM 檢查Python是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 請先安裝 Python 3.8+
    pause
    exit /b 1
)

REM 創建虛擬環境
echo 創建虛擬環境...
python -m venv venv
call venv\Scripts\activate.bat

REM 升級pip
echo 升級pip...
python -m pip install --upgrade pip

REM 安裝套件
echo 安裝所需套件...
pip install -r requirements.txt

REM 創建資料夾
echo 創建專案資料夾...
if not exist templates mkdir templates
if not exist logs mkdir logs
if not exist config mkdir config

echo.
echo ✅ 安裝完成！
echo.
echo 下一步:
echo 1. 將遊戲符號圖片放入 templates/ 資料夾
echo 2. 執行: python unlight_bot.py
echo.
pause
EOF