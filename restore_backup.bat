@echo off
chcp 65001 >nul
title استعادة النسخة الاحتياطية - نظام إدارة المبيعات

echo.
echo ========================================================================
echo 🔄 استعادة النسخة الاحتياطية
echo 🏪 التميز للهاتف النقال وقطع الغيار
echo ========================================================================
echo.

:: التحقق من وجود مجلد النسخ الاحتياطية
if not exist "backups" (
    echo ❌ خطأ: مجلد النسخ الاحتياطية غير موجود
    echo 📁 يرجى إنشاء نسخة احتياطية أولاً
    echo.
    pause
    exit /b 1
)

:: عرض النسخ الاحتياطية المتاحة
echo 📋 النسخ الاحتياطية المتاحة:
echo.
dir /b backups\*.zip 2>nul | findstr /r "backup_.*\.zip" > temp_backups.txt

if not exist "temp_backups.txt" (
    echo ❌ لا توجد نسخ احتياطية متاحة
    echo.
    pause
    exit /b 1
)

:: عرض قائمة النسخ الاحتياطية
set "counter=1"
for /f "delims=" %%i in (temp_backups.txt) do (
    echo %counter%. %%i
    set "backup_%counter%=%%i"
    set /a counter+=1
)

echo.
set /p choice="اختر رقم النسخة الاحتياطية (أو اضغط Enter للخروج): "

if "%choice%"=="" (
    echo.
    echo 👋 تم إلغاء العملية
    goto cleanup
)

:: التحقق من صحة الاختيار
set /a choice_num=%choice% 2>nul
if %choice_num% leq 0 (
    echo ❌ اختيار غير صحيح
    goto cleanup
)

set "selected_backup=!backup_%choice%!"
if not defined selected_backup (
    echo ❌ اختيار غير صحيح
    goto cleanup
)

echo.
echo ⚠️ تحذير: سيتم استبدال الملفات الحالية
echo 📁 النسخة المختارة: %selected_backup%
echo.
set /p confirm="هل أنت متأكد؟ (y/N): "

if /i not "%confirm%"=="y" (
    echo.
    echo 👋 تم إلغاء العملية
    goto cleanup
)

:: إنشاء نسخة احتياطية من الملفات الحالية قبل الاستعادة
echo.
echo 🔄 إنشاء نسخة احتياطية من الملفات الحالية...

for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "datestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

if exist "excellence_mobile_system_v6.py" (
    copy "excellence_mobile_system_v6.py" "excellence_mobile_system_v6.py.backup.%datestamp%"
    echo ✅ تم حفظ نسخة من الملف الرئيسي
)

if exist "excellence_mobile_database_v6.json" (
    copy "excellence_mobile_database_v6.json" "excellence_mobile_database_v6.json.backup.%datestamp%"
    echo ✅ تم حفظ نسخة من قاعدة البيانات
)

:: استعادة النسخة الاحتياطية
echo.
echo 🔄 جاري استعادة النسخة الاحتياطية...

powershell -command "Expand-Archive -Path 'backups\%selected_backup%' -DestinationPath '.' -Force"

if errorlevel 1 (
    echo ❌ خطأ في استعادة النسخة الاحتياطية
    goto cleanup
)

echo ✅ تم استعادة النسخة الاحتياطية بنجاح
echo.
echo 🎯 تم استعادة الملفات التالية:
echo   📄 excellence_mobile_system_v6.py
echo   📊 excellence_mobile_database_v6.json
echo   📝 ملفات التوثيق (*.md)
echo.

:cleanup
if exist "temp_backups.txt" del "temp_backups.txt"

pause 