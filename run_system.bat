@echo off
chcp 65001 >nul
title نظام إدارة المبيعات المتقدم - التميز للهاتف النقال

echo.
echo ========================================================================
echo 🚀 نظام إدارة المبيعات المتقدم - الإصدار السادس
echo 🏪 التميز للهاتف النقال وقطع الغيار
echo ========================================================================
echo.

:: التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ خطأ: Python غير مثبت أو غير موجود في PATH
    echo.
    echo 📥 يرجى تثبيت Python من الموقع الرسمي:
    echo 🌐 https://www.python.org/downloads/
    echo.
    echo ⚠️ تأكد من تفعيل خيار "Add Python to PATH" عند التثبيت
    echo.
    pause
    exit /b 1
)

:: التحقق من وجود الملف الرئيسي
if not exist "excellence_mobile_system_v6.py" (
    echo ❌ خطأ: الملف الرئيسي للنظام غير موجود
    echo 📁 يرجى التأكد من وجود الملف: excellence_mobile_system_v6.py
    echo.
    pause
    exit /b 1
)

:: التحقق من وجود قاعدة البيانات
if not exist "excellence_mobile_database_v6.json" (
    echo ⚠️ تحذير: قاعدة البيانات غير موجودة
    echo 📝 سيتم إنشاء قاعدة بيانات جديدة عند التشغيل
    echo.
)

echo ✅ Python متوفر
echo ✅ الملف الرئيسي موجود
echo.
echo 🔄 بدء تشغيل النظام...
echo.

:: تشغيل النظام
python excellence_mobile_system_v6.py

:: في حالة إغلاق النظام
echo.
echo 👋 تم إغلاق النظام
echo.
pause 