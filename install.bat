@echo off
chcp 65001 >nul
echo Проверка установки необходимых библиотек...
echo.
python -m pip install --upgrade pip
python -m pip install customtkinter Pillow
echo.
echo Установка завершена!
pause