#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار الـ APIs الجديدة - نظام التميز للهاتف النقال
"""

import requests
import json

def test_api(url, description):
    """اختبار API محدد"""
    print(f"\n🧪 اختبار: {description}")
    print(f"📡 URL: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ نجح الاختبار")
            if 'success' in data:
                print(f"📊 النتيجة: {'نجح' if data['success'] else 'فشل'}")
                if not data['success'] and 'message' in data:
                    print(f"⚠️  الرسالة: {data['message']}")
            return True
        else:
            print(f"❌ فشل الاختبار - كود الحالة: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ لا يمكن الاتصال بالخادم - تأكد من تشغيل النظام")
        return False
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def main():
    """تشغيل الاختبارات"""
    base_url = "http://localhost:5000"
    
    print("="*60)
    print("🧪 اختبار الـ APIs الجديدة")
    print("🏪 نظام التميز للهاتف النقال")
    print("="*60)
    
    # اختبار الصفحة الرئيسية
    if not test_api(f"{base_url}/", "الصفحة الرئيسية"):
        print("\n❌ النظام غير مُشغل. يرجى تشغيل excellence_mobile_system_v6.py أولاً")
        return
    
    # اختبار APIs الجديدة (ستحتاج تسجيل دخول)
    apis_to_test = [
        ("/api/excel/download-template", "تنزيل قالب Excel"),
        ("/api/reports/inventory-movement", "تقرير حركة المخزون"),
        ("/api/customers/statement/customer1", "كشف حساب عميل (مثال)"),
    ]
    
    print(f"\n📝 ملاحظة: بعض الـ APIs تحتاج تسجيل دخول")
    print(f"🔑 للاختبار الكامل، استخدم المتصفح وسجل الدخول أولاً")
    
    for api_path, description in apis_to_test:
        test_api(f"{base_url}{api_path}", description)
    
    print("\n" + "="*60)
    print("✅ انتهى الاختبار")
    print("🌐 للوصول للنظام: http://localhost:5000")
    print("👤 المدير الافتراضي: admin / admin123")

if __name__ == "__main__":
    main()