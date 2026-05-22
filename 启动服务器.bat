@echo off
chcp 65001 >nul
title AI学习助手

echo ================================================
echo   AI学习助手 - 正在启动...
echo ================================================
echo.
echo 第一步：检查Python...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 没有找到Python！请先安装Python 3.10以上版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Python已就绪！

echo.
echo 第二步：检查依赖库...
py -m pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [警告] 依赖安装失败，尝试继续...
)

echo.
echo 第三步：启动服务器...
echo.
echo ================================================
echo   启动成功后，请在浏览器打开：
echo   http://127.0.0.1:5000
echo ================================================
echo.
start "" http://127.0.0.1:5000
py app.py
pause
