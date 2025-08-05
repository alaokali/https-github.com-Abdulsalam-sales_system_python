@echo off
chcp 65001 >nul
title نسخة احتياطية - نظام إدارة المبيعات

echo.
echo ========================================================================
echo 📦 إنشاء نسخة احتياطية للنظام
echo 🏪 التميز للهاتف النقال وقطع الغيار
echo ========================================================================
echo.

:: إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً
if not exist "backups" (
    mkdir backups
    echo ✅ تم إنشاء مجلد النسخ الاحتياطية
)

:: الحصول على التاريخ والوقت
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "datestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

:: اسم ملف النسخة الاحتياطية
set "backup_name=backup_%datestamp%.zip"

echo 📅 التاريخ: %YYYY%-%MM%-%DD%
echo 🕒 الوقت: %HH%:%Min%:%Sec%
echo 📁 اسم النسخة: %backup_name%
echo.

:: إنشاء النسخة الاحتياطية
echo 🔄 جاري إنشاء النسخة الاحتياطية...

:: استخدام PowerShell لإنشاء ملف ZIP
powershell -command "Compress-Archive -Path 'excellence_mobile_system_v6.py', 'excellence_mobile_database_v6.json', '*.md' -DestinationPath 'backups\%backup_name%' -Force"

if errorlevel 1 (
    echo ❌ خطأ في إنشاء النسخة الاحتياطية
    echo.
    pause
    exit /b 1
)

echo ✅ تم إنشاء النسخة الاحتياطية بنجاح
echo 📁 الموقع: backups\%backup_name%
echo.

:: عرض حجم الملف
for %%A in ("backups\%backup_name%") do (
    echo 📊 حجم الملف: %%~zA بايت
)

echo.
echo 🎯 تم حفظ الملفات التالية في النسخة الاحتياطية:
echo   📄 excellence_mobile_system_v6.py
echo   📊 excellence_mobile_database_v6.json
echo   📝 ملفات التوثيق (*.md)
echo.

pause 