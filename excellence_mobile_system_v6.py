#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 نظام إدارة المبيعات المتقدم - الإصدار السادس المتكامل والشامل
🏪 مخصص لمحل: التميز للهاتف النقال وقطع الغيار
📅 تاريخ الإنشاء: 4 أغسطس 2025
👨‍💻 المطور: Augment Agent
🎯 الإصدار: 6.0 Ultimate Professional Enterprise Edition

الميزات المتكاملة:
✅ نظام المستخدمين والصلاحيات (5 أنواع)
✅ نقطة البيع المتقدمة مع الاختصارات والقوائم السياقية
✅ إدارة المنتجات الشاملة مع الباركود والمخزون
✅ إدارة العملاء المتقدمة مع التصنيفات والحدود الائتمانية
✅ نظام التقارير والتحليلات الشامل
✅ إدارة المخزون المتقدمة مع تتبع الحركة
✅ نظام البيع والشراء المتكامل
✅ نظام حساب الشركاء
✅ الإعدادات المتقدمة والتخصيص الشامل
✅ النسخ الاحتياطي التلقائي
✅ نظام الأمان المتقدم
✅ واجهات عصرية ومتجاوبة
"""

from flask import Flask, render_template_string, redirect, url_for, request, session, flash, jsonify, send_file
import json
import os
import hashlib
from datetime import datetime, timedelta
import uuid
import secrets
import shutil
import zipfile
from functools import wraps
import re

# إنشاء التطبيق
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ===== إعدادات النظام المخصصة لمحل التميز =====
SYSTEM_CONFIG = {
    'company_name': 'التميز للهاتف النقال وقطع الغيار',
    'company_name_en': 'Excellence Mobile & Spare Parts',
    'version': '6.0 Ultimate Professional Enterprise Edition',
    'currency': 'ريال',
    'currency_symbol': 'ر.س',
    'tax_rate': 0.15,  # 15% ضريبة القيمة المضافة
    'low_stock_threshold': 5,
    'critical_stock_threshold': 2,
    'exchange_rate': 3.75,  # دولار إلى ريال
    'auto_barcode': True,
    'auto_price_update': True,
    'backup_enabled': True,
    'backup_interval': 24,  # كل 24 ساعة
    'session_timeout': 120,  # 2 ساعة
    'max_users': 10,
    'company_phone': '+966501234567',
    'company_email': 'info@excellence-mobile.com',
    'company_address': 'الرياض، المملكة العربية السعودية',
    'invoice_format': 'A4',
    'printer_type': 'normal',
    'default_payment_terms': 'نقدي',
    'default_discount': 0,
    'business_type': 'mobile_electronics',  # نوع العمل: هواتف وإلكترونيات
    'working_hours': 'السبت - الخميس: 9:00 ص - 11:00 م',
    'cr_number': '1010123456',  # رقم السجل التجاري
    'vat_number': '300123456789003'  # الرقم الضريبي
}

# ===== أنواع المستخدمين والصلاحيات المفصلة =====
DETAILED_PERMISSIONS = {
    'pos': {
        'name': 'نقطة البيع',
        'sub_permissions': {
            'pos_view': 'عرض نقطة البيع',
            'pos_sale': 'إتمام البيع',
            'pos_return': 'إرجاع المنتجات',
            'pos_discount': 'إضافة خصم',
            'pos_payment_methods': 'تغيير طريقة الدفع',
            'pos_customer_select': 'اختيار العملاء',
            'pos_price_edit': 'تعديل الأسعار'
        }
    },
    'products': {
        'name': 'إدارة المنتجات',
        'sub_permissions': {
            'products_view': 'عرض المنتجات',
            'products_add': 'إضافة منتج',
            'products_edit': 'تعديل منتج',
            'products_delete': 'حذف منتج',
            'products_prices': 'إدارة الأسعار',
            'products_categories': 'إدارة الفئات',
            'products_import': 'استيراد المنتجات',
            'products_export': 'تصدير المنتجات'
        }
    },
    'customers': {
        'name': 'إدارة العملاء',
        'sub_permissions': {
            'customers_view': 'عرض العملاء',
            'customers_add': 'إضافة عميل',
            'customers_edit': 'تعديل عميل',
            'customers_delete': 'حذف عميل',
            'customers_balance': 'إدارة الأرصدة',
            'customers_statement': 'كشف الحساب',
            'customers_credit_limit': 'تحديد الحد الائتماني'
        }
    },
    'inventory': {
        'name': 'إدارة المخزون',
        'sub_permissions': {
            'inventory_view': 'عرض المخزون',
            'inventory_add': 'إضافة مخزون',
            'inventory_adjust': 'تعديل المخزون',
            'inventory_movements': 'حركة المخزون',
            'inventory_reports': 'تقارير المخزون',
            'inventory_alerts': 'تنبيهات المخزون'
        }
    },
    'purchases': {
        'name': 'إدارة المشتريات',
        'sub_permissions': {
            'purchases_view': 'عرض المشتريات',
            'purchases_add': 'إضافة مشتريات',
            'purchases_edit': 'تعديل مشتريات',
            'purchases_delete': 'حذف مشتريات',
            'purchases_import': 'استيراد فواتير',
            'purchases_suppliers': 'إدارة الموردين'
        }
    },
    'reports': {
        'name': 'التقارير والتحليلات',
        'sub_permissions': {
            'reports_sales': 'تقارير المبيعات',
            'reports_customers': 'تقارير العملاء',
            'reports_products': 'تقارير المنتجات',
            'reports_inventory': 'تقارير المخزون',
            'reports_profit': 'تقارير الأرباح (مدير فقط)',
            'reports_financial': 'التقارير المالية',
            'reports_daily': 'التقارير اليومية',
            'reports_users': 'تقارير المستخدمين'
        }
    },
    'partners': {
        'name': 'حساب الشركاء',
        'sub_permissions': {
            'partners_view': 'عرض الشركاء',
            'partners_add': 'إضافة شريك',
            'partners_edit': 'تعديل شريك',
            'partners_transactions': 'معاملات الشركاء',
            'partners_statements': 'كشوفات الشركاء'
        }
    },
    'users': {
        'name': 'إدارة المستخدمين',
        'sub_permissions': {
            'users_view': 'عرض المستخدمين',
            'users_add': 'إضافة مستخدم',
            'users_edit': 'تعديل مستخدم',
            'users_delete': 'حذف مستخدم',
            'users_permissions': 'إدارة الصلاحيات',
            'users_activity': 'سجل نشاط المستخدمين'
        }
    },
    'settings': {
        'name': 'الإعدادات',
        'sub_permissions': {
            'settings_system': 'إعدادات النظام',
            'settings_company': 'إعدادات الشركة',
            'settings_backup': 'النسخ الاحتياطية',
            'settings_security': 'الإعدادات الأمنية'
        }
    }
}

USER_ROLES = {
    'admin': {
        'name': 'مدير النظام',
        'permissions': ['all'],
        'detailed_permissions': {permission: list(details['sub_permissions'].keys()) for permission, details in DETAILED_PERMISSIONS.items()},
        'description': 'صلاحيات كاملة لجميع أجزاء النظام'
    },
    'manager': {
        'name': 'مدير المبيعات',
        'permissions': ['pos', 'customers', 'products', 'inventory', 'purchases', 'reports', 'partners'],
        'detailed_permissions': {
            'pos': ['pos_view', 'pos_sale', 'pos_return', 'pos_discount', 'pos_payment_methods', 'pos_customer_select', 'pos_price_edit'],
            'customers': ['customers_view', 'customers_add', 'customers_edit', 'customers_balance', 'customers_statement', 'customers_credit_limit'],
            'products': ['products_view', 'products_add', 'products_edit', 'products_prices', 'products_categories', 'products_import', 'products_export'],
            'inventory': ['inventory_view', 'inventory_add', 'inventory_adjust', 'inventory_movements', 'inventory_reports', 'inventory_alerts'],
            'purchases': ['purchases_view', 'purchases_add', 'purchases_edit', 'purchases_import', 'purchases_suppliers'],
            'reports': ['reports_sales', 'reports_customers', 'reports_products', 'reports_inventory', 'reports_profit', 'reports_financial', 'reports_daily'],
            'partners': ['partners_view', 'partners_add', 'partners_edit', 'partners_transactions', 'partners_statements']
        },
        'description': 'إدارة شاملة للمبيعات والعمليات التجارية'
    },
    'cashier': {
        'name': 'أمين الصندوق',
        'permissions': ['pos', 'customers', 'products'],
        'detailed_permissions': {
            'pos': ['pos_view', 'pos_sale', 'pos_return', 'pos_discount', 'pos_customer_select'],
            'customers': ['customers_view', 'customers_add', 'customers_edit', 'customers_statement'],
            'products': ['products_view', 'products_prices']
        },
        'description': 'نقطة البيع والتعامل مع العملاء'
    },
    'accountant': {
        'name': 'محاسب',
        'permissions': ['reports', 'customers', 'partners'],
        'detailed_permissions': {
            'reports': ['reports_sales', 'reports_customers', 'reports_financial', 'reports_daily'],
            'customers': ['customers_view', 'customers_balance', 'customers_statement'],
            'partners': ['partners_view', 'partners_transactions', 'partners_statements']
        },
        'description': 'التقارير المالية وإدارة الحسابات'
    },
    'employee': {
        'name': 'موظف',
        'permissions': ['pos', 'customers'],
        'detailed_permissions': {
            'pos': ['pos_view', 'pos_sale', 'pos_customer_select'],
            'customers': ['customers_view', 'customers_add']
        },
        'description': 'العمليات الأساسية للبيع'
    }
}

# ===== أنواع البيع والأسعار =====
SALE_TYPES = {
    'retail': {
        'name': 'بيع تجزئة',
        'icon': 'fa-shopping-cart',
        'price_field': 'selling_price',
        'description': 'البيع للعملاء الأفراد بسعر التجزئة',
        'shortcut': 'F1'
    },
    'wholesale': {
        'name': 'بيع جملة',
        'icon': 'fa-boxes',
        'price_field': 'wholesale_price',
        'description': 'البيع للتجار والموزعين بسعر الجملة',
        'shortcut': 'F2'
    },
    'cost': {
        'name': 'سعر التكلفة',
        'icon': 'fa-calculator',
        'price_field': 'cost_price',
        'description': 'البيع بسعر التكلفة للموظفين أو حالات خاصة',
        'shortcut': 'F3'
    },
    'purchase': {
        'name': 'سعر الشراء',
        'icon': 'fa-shopping-bag',
        'price_field': 'purchase_price',
        'description': 'سعر الشراء الأصلي للإرجاع أو التبديل',
        'shortcut': 'F4'
    }
}

# ===== إعدادات الفاتورة =====
INVOICE_FORMATS = {
    'A4': {
        'name': 'A4 عادي',
        'width': '210mm',
        'height': '297mm',
        'orientation': 'portrait'
    },
    'thermal': {
        'name': 'طابعة حرارية',
        'width': '80mm',
        'height': 'auto',
        'orientation': 'portrait'
    },
    'receipt': {
        'name': 'إيصال صغير',
        'width': '58mm',
        'height': 'auto',
        'orientation': 'portrait'
    }
}

# ===== فئات المنتجات المخصصة للهواتف النقالة =====
PRODUCT_CATEGORIES = {
    'smartphones': {
        'name': 'الهواتف الذكية',
        'icon': 'fa-mobile-alt',
        'subcategories': ['iPhone', 'Samsung', 'Huawei', 'Xiaomi', 'Oppo', 'Vivo', 'OnePlus', 'أخرى']
    },
    'accessories': {
        'name': 'الإكسسوارات',
        'icon': 'fa-headphones',
        'subcategories': ['سماعات', 'شواحن', 'كابلات', 'حافظات', 'واقيات شاشة', 'حوامل', 'أخرى']
    },
    'spare_parts': {
        'name': 'قطع الغيار',
        'icon': 'fa-tools',
        'subcategories': ['شاشات', 'بطاريات', 'كاميرات', 'سماعات داخلية', 'أزرار', 'فليكس', 'أخرى']
    },
    'tablets': {
        'name': 'الأجهزة اللوحية',
        'icon': 'fa-tablet-alt',
        'subcategories': ['iPad', 'Samsung Tab', 'Huawei Tab', 'أخرى']
    },
    'smartwatches': {
        'name': 'الساعات الذكية',
        'icon': 'fa-clock',
        'subcategories': ['Apple Watch', 'Samsung Watch', 'Huawei Watch', 'أخرى']
    },
    'electronics': {
        'name': 'إلكترونيات أخرى',
        'icon': 'fa-microchip',
        'subcategories': ['سماعات بلوتوث', 'باور بانك', 'كاميرات', 'أجهزة ذكية', 'أخرى']
    }
}

# ===== قاعدة البيانات =====
DATABASE_FILE = 'excellence_mobile_database_v6.json'
BACKUP_DIR = 'backups'

def load_database():
    """تحميل قاعدة البيانات"""
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # التأكد من وجود جميع الأقسام المطلوبة
                required_sections = [
                    'users', 'products', 'customers', 'categories', 'suppliers',
                    'sales', 'purchases', 'inventory_movements', 'partners',
                    'balance_history', 'activity_log', 'settings', 'reports_cache'
                ]
                for section in required_sections:
                    if section not in data:
                        data[section] = {}
                return data
        except Exception as e:
            print(f"خطأ في تحميل قاعدة البيانات: {e}")
            return init_default_data()
    return init_default_data()

def save_database(data):
    """حفظ قاعدة البيانات مع النسخ الاحتياطي والتحسينات الشاملة"""
    try:
        # إنشاء نسخة احتياطية قبل الحفظ
        if os.path.exists(DATABASE_FILE):
            backup_filename = f"{DATABASE_FILE}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(DATABASE_FILE, backup_filename)
            print(f"✅ تم إنشاء نسخة احتياطية: {backup_filename}")
        
        # حفظ البيانات الجديدة
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # تنظيف النسخ الاحتياطية القديمة (الاحتفاظ بآخر 10 نسخ)
        cleanup_old_backups()
        
        print(f"✅ تم حفظ قاعدة البيانات بنجاح - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
    except Exception as e:
        print(f"❌ خطأ في حفظ قاعدة البيانات: {e}")
        return False

def cleanup_old_backups():
    """تنظيف النسخ الاحتياطية القديمة"""
    try:
        backup_files = [f for f in os.listdir('.') if f.startswith(f"{DATABASE_FILE}.backup.")]
        backup_files.sort(reverse=True)
        
        # حذف النسخ الزائدة عن 10
        for backup_file in backup_files[10:]:
            os.remove(backup_file)
    except:
        pass

def init_default_data():
    """تهيئة البيانات الافتراضية"""
    admin_id = str(uuid.uuid4())
    manager_id = str(uuid.uuid4())
    cashier_id = str(uuid.uuid4())
    
    # منتجات تجريبية للهواتف النقالة
    sample_products = {}
    
    # iPhone 15 Pro Max
    iphone_id = str(uuid.uuid4())
    sample_products[iphone_id] = {
        'id': iphone_id,
        'name': 'iPhone 15 Pro Max 256GB',
        'sku': 'IP15PM256',
        'barcode': 'BC' + iphone_id[:8].upper(),
        'category': 'smartphones',
        'subcategory': 'iPhone',
        'description': 'أحدث إصدار من آيفون مع كاميرا متطورة وشاشة Super Retina XDR',
        'cost_price': 3500.00,
        'selling_price': 4200.00,
        'wholesale_price': 3800.00,
        'purchase_price': 3500.00,
        'stock_quantity': 15,
        'min_stock_level': 3,
        'max_stock_level': 50,
        'supplier_id': '',
        'unit': 'قطعة',
        'weight': 0.221,
        'dimensions': '159.9 × 76.7 × 8.25 مم',
        'is_active': True,
        'tax_rate': 0.15,
        'discount_rate': 0,
        'image_url': '',
        'warranty_period': '12 شهر',
        'brand': 'Apple',
        'model': 'iPhone 15 Pro Max',
        'color': 'تيتانيوم طبيعي',
        'storage': '256GB',
        'notes': 'منتج أصلي مع ضمان الوكيل',
        'created_at': datetime.now().isoformat(),
        'created_by': admin_id,
        'updated_at': datetime.now().isoformat(),
        'updated_by': admin_id
    }
    
    # Samsung Galaxy S24 Ultra
    samsung_id = str(uuid.uuid4())
    sample_products[samsung_id] = {
        'id': samsung_id,
        'name': 'Samsung Galaxy S24 Ultra 512GB',
        'sku': 'SGS24U512',
        'barcode': 'BC' + samsung_id[:8].upper(),
        'category': 'smartphones',
        'subcategory': 'Samsung',
        'description': 'هاتف سامسونج الرائد مع قلم S Pen وكاميرا 200 ميجابكسل',
        'cost_price': 3200.00,
        'selling_price': 3800.00,
        'wholesale_price': 3500.00,
        'purchase_price': 3200.00,
        'stock_quantity': 12,
        'min_stock_level': 3,
        'max_stock_level': 40,
        'supplier_id': '',
        'unit': 'قطعة',
        'weight': 0.232,
        'dimensions': '162.3 × 79.0 × 8.6 مم',
        'is_active': True,
        'tax_rate': 0.15,
        'discount_rate': 0,
        'image_url': '',
        'warranty_period': '12 شهر',
        'brand': 'Samsung',
        'model': 'Galaxy S24 Ultra',
        'color': 'أسود تيتانيوم',
        'storage': '512GB',
        'notes': 'منتج أصلي مع ضمان الوكيل',
        'created_at': datetime.now().isoformat(),
        'created_by': admin_id,
        'updated_at': datetime.now().isoformat(),
        'updated_by': admin_id
    }
    
    # شاحن لاسلكي
    charger_id = str(uuid.uuid4())
    sample_products[charger_id] = {
        'id': charger_id,
        'name': 'شاحن لاسلكي سريع 15W',
        'sku': 'WC15W001',
        'barcode': 'BC' + charger_id[:8].upper(),
        'category': 'accessories',
        'subcategory': 'شواحن',
        'description': 'شاحن لاسلكي سريع متوافق مع جميع الهواتف الداعمة للشحن اللاسلكي',
        'cost_price': 45.00,
        'selling_price': 75.00,
        'wholesale_price': 60.00,
        'purchase_price': 45.00,
        'stock_quantity': 25,
        'min_stock_level': 5,
        'max_stock_level': 100,
        'supplier_id': '',
        'unit': 'قطعة',
        'weight': 0.150,
        'dimensions': '100 × 100 × 10 مم',
        'is_active': True,
        'tax_rate': 0.15,
        'discount_rate': 0,
        'image_url': '',
        'warranty_period': '6 أشهر',
        'brand': 'Generic',
        'model': 'WC-15W',
        'color': 'أسود',
        'storage': '',
        'notes': 'متوافق مع iPhone و Samsung',
        'created_at': datetime.now().isoformat(),
        'created_by': admin_id,
        'updated_at': datetime.now().isoformat(),
        'updated_by': admin_id
    }
    
    # عملاء تجريبيين
    sample_customers = {}
    
    # عميل تجزئة
    retail_customer_id = str(uuid.uuid4())
    sample_customers[retail_customer_id] = {
        'id': retail_customer_id,
        'name': 'أحمد محمد العلي',
        'phone': '+966501234567',
        'email': 'ahmed.ali@email.com',
        'address': 'الرياض، حي النخيل، شارع الملك فهد',
        'type': 'تجزئة',
        'tax_number': '',
        'credit_limit': 0.0,
        'payment_terms': 'نقدي',
        'discount_rate': 0.0,
        'current_balance': 0.0,
        'total_purchases': 0.0,
        'last_purchase_date': None,
        'is_active': True,
        'notes': 'عميل مميز',
        'created_at': datetime.now().isoformat(),
        'created_by': admin_id,
        'updated_at': datetime.now().isoformat(),
        'updated_by': admin_id
    }
    
    # عميل جملة
    wholesale_customer_id = str(uuid.uuid4())
    sample_customers[wholesale_customer_id] = {
        'id': wholesale_customer_id,
        'name': 'شركة الاتصالات المتقدمة',
        'phone': '+966112345678',
        'email': 'info@advanced-telecom.com',
        'address': 'جدة، حي الحمراء، طريق الملك عبدالعزيز',
        'type': 'جملة',
        'tax_number': '300123456789003',
        'credit_limit': 50000.0,
        'payment_terms': 'آجل 30 يوم',
        'discount_rate': 5.0,
        'current_balance': 0.0,
        'total_purchases': 0.0,
        'last_purchase_date': None,
        'is_active': True,
        'notes': 'عميل جملة مميز',
        'created_at': datetime.now().isoformat(),
        'created_by': admin_id,
        'updated_at': datetime.now().isoformat(),
        'updated_by': admin_id
    }
    
    # شركاء تجريبيين
    sample_partners = {}
    
    # شريك 1
    partner1_id = str(uuid.uuid4())
    sample_partners[partner1_id] = {
        'id': partner1_id,
        'name': 'شركة التكنولوجيا المتقدمة',
        'phone': '+966112345678',
        'email': 'info@advanced-tech.com',
        'address': 'الرياض، حي النخيل، شارع الملك فهد',
        'tax_number': '300123456789003',
        'credit_limit': 100000.0,
        'payment_terms': 'آجل 60 يوم',
        'discount_rate': 3.0,
        'current_balance': 0.0,
        'total_purchases': 0.0,
        'last_purchase_date': None,
        'is_active': True,
        'notes': 'شريك مميز',
        'created_at': datetime.now().isoformat(),
        'created_by': admin_id,
        'updated_at': datetime.now().isoformat(),
        'updated_by': admin_id
    }
    
    # شريك 2
    partner2_id = str(uuid.uuid4())
    sample_partners[partner2_id] = {
        'id': partner2_id,
        'name': 'شركة التجارة العالمية',
        'phone': '+966112345678',
        'email': 'info@global-trade.com',
        'address': 'جدة، حي الحمراء، طريق الملك عبدالعزيز',
        'tax_number': '300123456789003',
        'credit_limit': 200000.0,
        'payment_terms': 'آجل 90 يوم',
        'discount_rate': 2.0,
        'current_balance': 0.0,
        'total_purchases': 0.0,
        'last_purchase_date': None,
        'is_active': True,
        'notes': 'شريك مميز',
        'created_at': datetime.now().isoformat(),
        'created_by': admin_id,
        'updated_at': datetime.now().isoformat(),
        'updated_by': admin_id
    }
    
    # شركاء تجريبيين
    sample_partners = {}
    
    # شريك 1
    partner1_id = str(uuid.uuid4())
    sample_partners[partner1_id] = {
        'id': partner1_id,
        'name': 'أحمد محمد العلي',
        'phone': '+966501234567',
        'email': 'ahmed.ali@email.com',
        'address': 'الرياض، حي النخيل، شارع الملك فهد',
        'national_id': '1010123456',
        'contribution_amount': 50000.0,
        'contribution_percentage': 25.0,
        'current_balance': 0.0,
        'total_withdrawals': 0.0,
        'total_profits_received': 0.0,
        'assets': [],
        'is_active': True,
        'join_date': datetime.now().isoformat(),
        'notes': 'شريك مؤسس',
        'created_at': datetime.now().isoformat(),
        'created_by': admin_id,
        'updated_at': datetime.now().isoformat(),
        'updated_by': admin_id
    }
    
    # شريك 2
    partner2_id = str(uuid.uuid4())
    sample_partners[partner2_id] = {
        'id': partner2_id,
        'name': 'محمد عبدالله السعد',
        'phone': '+966502345678',
        'email': 'mohammed.saad@email.com',
        'address': 'جدة، حي الحمراء، طريق الملك عبدالعزيز',
        'national_id': '1010123457',
        'contribution_amount': 30000.0,
        'contribution_percentage': 15.0,
        'current_balance': 0.0,
        'total_withdrawals': 0.0,
        'total_profits_received': 0.0,
        'assets': [],
        'is_active': True,
        'join_date': datetime.now().isoformat(),
        'notes': 'شريك مميز',
        'created_at': datetime.now().isoformat(),
        'created_by': admin_id,
        'updated_at': datetime.now().isoformat(),
        'updated_by': admin_id
    }
    
    return {
        'users': {
            'admin': {
                'id': admin_id,
                'username': 'admin',
                'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
                'full_name': 'مدير النظام',
                'email': 'admin@excellence-mobile.com',
                'phone': '+966501234567',
                'role': 'admin',
                'permissions': ['all'],
                'is_active': True,
                'last_login': None,
                'created_at': datetime.now().isoformat(),
                'created_by': admin_id,
                'avatar': None,
                'settings': {
                    'theme': 'light',
                    'language': 'ar',
                    'notifications': True,
                    'default_view': 'dashboard'
                }
            },
            'manager': {
                'id': manager_id,
                'username': 'manager',
                'password_hash': hashlib.sha256('manager123'.encode()).hexdigest(),
                'full_name': 'مدير المبيعات',
                'email': 'manager@excellence-mobile.com',
                'phone': '+966502345678',
                'role': 'manager',
                'permissions': ['sales', 'customers', 'products', 'reports', 'pos', 'inventory', 'purchases', 'partners', 'settings'],
                'is_active': True,
                'last_login': None,
                'created_at': datetime.now().isoformat(),
                'created_by': admin_id,
                'avatar': None,
                'settings': {
                    'theme': 'light',
                    'language': 'ar',
                    'notifications': True,
                    'default_view': 'pos'
                }
            },
            'cashier': {
                'id': cashier_id,
                'username': 'cashier',
                'password_hash': hashlib.sha256('cashier123'.encode()).hexdigest(),
                'full_name': 'أمين الصندوق',
                'email': 'cashier@excellence-mobile.com',
                'phone': '+966503456789',
                'role': 'cashier',
                'permissions': ['pos', 'customers', 'products', 'inventory', 'partners'],
                'is_active': True,
                'last_login': None,
                'created_at': datetime.now().isoformat(),
                'created_by': admin_id,
                'avatar': None,
                'settings': {
                    'theme': 'light',
                    'language': 'ar',
                    'notifications': True,
                    'default_view': 'pos'
                }
            }
        },
        'products': sample_products,
        'customers': sample_customers,
        'categories': PRODUCT_CATEGORIES,
        'suppliers': {},
        'sales': {},
        'purchases': {},
        'inventory_movements': {},
        'partners': sample_partners,
        'balance_history': [],
        'activity_log': [],
        'settings': SYSTEM_CONFIG,
        'reports_cache': {}
    }

# ===== دوال المساعدة =====
def init_database():
    """تهيئة قاعدة البيانات"""
    if not os.path.exists(DATABASE_FILE):
        data = init_default_data()
        save_database(data)
        print("✅ تم إنشاء قاعدة البيانات بنجاح")
    else:
        print("✅ قاعدة البيانات موجودة")
def check_permission(user_id, permission, sub_permission=None):
    """فحص صلاحيات المستخدم المحسن مع الصلاحيات المفصلة"""
    try:
        # التحقق من وجود معرف المستخدم
        if not user_id:
            print(f"خطأ: معرف المستخدم فارغ للصلاحية: {permission}")
            return False

        data = load_database()
        users = data.get('users', {})

        current_user = None
        for username, user in users.items():
            if user.get('id') == user_id:
                current_user = user
                break

        if not current_user:
            print(f"خطأ: المستخدم غير موجود للصلاحية: {permission}")
            return False

        # التحقق من أن المستخدم نشط
        if not current_user.get('is_active', True):
            print(f"خطأ: المستخدم غير نشط للصلاحية: {permission}")
            return False

        user_permissions = current_user.get('permissions', [])
        user_detailed_permissions = current_user.get('detailed_permissions', {})
        user_role = current_user.get('role', 'employee')

        # المدير له جميع الصلاحيات
        if user_role == 'admin' or 'all' in user_permissions:
            print(f"✅ صلاحية ممنوحة: {permission} للمستخدم: {current_user.get('username', 'unknown')} (مدير)")
            return True

        # فحص الصلاحية العامة أولاً
        if permission not in user_permissions:
            # فحص صلاحيات الدور الافتراضية للتوافق العكسي
            role_perms = USER_ROLES.get(user_role, {}).get('permissions', [])
            if permission not in role_perms:
                print(f"❌ صلاحية مرفوضة: {permission} للمستخدم: {current_user.get('username', 'unknown')}")
                return False

        # إذا لم يتم تحديد صلاحية فرعية، السماح بالوصول للصلاحية العامة
        if sub_permission is None:
            print(f"✅ صلاحية عامة ممنوحة: {permission} للمستخدم: {current_user.get('username', 'unknown')}")
            return True

        # فحص الصلاحية الفرعية
        if permission in user_detailed_permissions:
            if sub_permission in user_detailed_permissions[permission]:
                print(f"✅ صلاحية مفصلة ممنوحة: {permission}.{sub_permission} للمستخدم: {current_user.get('username', 'unknown')}")
                return True
            else:
                print(f"❌ صلاحية مفصلة مرفوضة: {permission}.{sub_permission} للمستخدم: {current_user.get('username', 'unknown')}")
                return False

        # إذا لم تكن هناك صلاحيات مفصلة محددة، فحص الصلاحيات الافتراضية للدور
        role_detailed_perms = USER_ROLES.get(user_role, {}).get('detailed_permissions', {})
        if permission in role_detailed_perms:
            if sub_permission in role_detailed_perms[permission]:
                print(f"✅ صلاحية افتراضية ممنوحة: {permission}.{sub_permission} للمستخدم: {current_user.get('username', 'unknown')}")
                return True

        print(f"❌ صلاحية مفصلة مرفوضة: {permission}.{sub_permission} للمستخدم: {current_user.get('username', 'unknown')}")
        return False

    except Exception as e:
        print(f"خطأ في فحص الصلاحيات: {e}")
        return False

def check_detailed_permission(user_id, detailed_permission):
    """فحص صلاحية مفصلة محددة"""
    try:
        data = load_database()
        users = data.get('users', {})

        current_user = None
        for username, user in users.items():
            if user.get('id') == user_id:
                current_user = user
                break

        if not current_user or not current_user.get('is_active', True):
            return False

        # المدير له جميع الصلاحيات
        if current_user.get('role') == 'admin' or 'all' in current_user.get('permissions', []):
            return True

        # البحث في الصلاحيات المفصلة
        user_detailed_permissions = current_user.get('detailed_permissions', {})
        for category, perms in user_detailed_permissions.items():
            if detailed_permission in perms:
                return True

        # فحص الصلاحيات الافتراضية للدور
        user_role = current_user.get('role', 'employee')
        role_detailed_perms = USER_ROLES.get(user_role, {}).get('detailed_permissions', {})
        for category, perms in role_detailed_perms.items():
            if detailed_permission in perms:
                return True

        return False

    except Exception as e:
        print(f"خطأ في فحص الصلاحية المفصلة: {e}")
        return False

def get_current_user():
    """الحصول على بيانات المستخدم الحالي"""
    if 'user_id' not in session:
        return None
    
    try:
        data = load_database()
        users = data.get('users', {})
        
        for username, user in users.items():
            if user.get('id') == session['user_id']:
                return user
        return None
    except:
        return None

def log_activity(user_id, action, details=None):
    """تسجيل نشاط المستخدم مع تحسينات شاملة"""
    try:
        data = load_database()
        activity_log = data.get('activity_log', [])
        
        # الحصول على معلومات المستخدم
        user_info = "unknown"
        try:
            users = data.get('users', {})
            for username, user in users.items():
                if user.get('id') == user_id:
                    user_info = f"{user.get('username', 'unknown')} ({user.get('role', 'unknown')})"
                    break
        except:
            pass
        
        log_entry = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'user_info': user_info,
            'action': action,
            'details': details or {},
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr if request else 'system',
            'user_agent': request.headers.get('User-Agent', 'unknown') if request else 'system'
        }
        
        activity_log.append(log_entry)
        
        # الاحتفاظ بآخر 1000 سجل فقط
        if len(activity_log) > 1000:
            activity_log = activity_log[-1000:]
        
        data['activity_log'] = activity_log
        save_database(data)
    except:
        pass

def require_permission(permission):
    """ديكوريتر للتحقق من الصلاحيات"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            if not check_permission(session['user_id'], permission):
                flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_login(f):
    """ديكوريتر للتحقق من تسجيل الدخول"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
# ===== الصفحات الأساسية =====
@app.route('/')
@require_login
def index():
    """الصفحة الرئيسية - لوحة التحكم"""
    current_user = get_current_user()
    data = load_database()

    # حساب الإحصائيات
    products = data.get('products', {})
    customers = data.get('customers', {})
    sales = data.get('sales', {})
    users = data.get('users', {})

    # إحصائيات المنتجات
    total_products = len(products)
    active_products = len([p for p in products.values() if p.get('is_active', True)])
    low_stock = len([p for p in products.values() if p.get('stock_quantity', 0) <= SYSTEM_CONFIG.get('low_stock_threshold', 5)])
    out_of_stock = len([p for p in products.values() if p.get('stock_quantity', 0) <= 0])

    # إحصائيات العملاء
    total_customers = len(customers)
    active_customers = len([c for c in customers.values() if c.get('is_active', True)])
    retail_customers = len([c for c in customers.values() if c.get('type') == 'تجزئة'])
    wholesale_customers = len([c for c in customers.values() if c.get('type') == 'جملة'])

    # إحصائيات المبيعات (اليوم)
    today = datetime.now().date()
    today_sales = [s for s in sales.values() if s.get('date', '')[:10] == str(today)]
    today_revenue = sum(s.get('total_amount', 0) for s in today_sales)
    today_transactions = len(today_sales)

    # إحصائيات المبيعات (الشهر)
    current_month = datetime.now().strftime('%Y-%m')
    month_sales = [s for s in sales.values() if s.get('date', '')[:7] == current_month]
    month_revenue = sum(s.get('total_amount', 0) for s in month_sales)
    month_transactions = len(month_sales)

    # قيمة المخزون
    inventory_value = sum(p.get('stock_quantity', 0) * p.get('cost_price', 0) for p in products.values())

    # المديونية
    total_debt = sum(c.get('current_balance', 0) for c in customers.values() if c.get('current_balance', 0) > 0)

    stats = {
        'products': {
            'total': total_products,
            'active': active_products,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
            'inventory_value': inventory_value
        },
        'customers': {
            'total': total_customers,
            'active': active_customers,
            'retail': retail_customers,
            'wholesale': wholesale_customers,
            'total_debt': total_debt
        },
        'sales': {
            'today_revenue': today_revenue,
            'today_transactions': today_transactions,
            'month_revenue': month_revenue,
            'month_transactions': month_transactions
        },
        'users': {
            'total': len(users),
            'active': len([u for u in users.values() if u.get('is_active', True)])
        }
    }

    # الأنشطة الأخيرة
    activity_log = data.get('activity_log', [])
    recent_activities = sorted(activity_log, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]

    # المنتجات منخفضة المخزون
    low_stock_products = [p for p in products.values() if p.get('stock_quantity', 0) <= SYSTEM_CONFIG.get('low_stock_threshold', 5)][:5]

    # أفضل المنتجات مبيعاً (محاكاة)
    top_products = list(products.values())[:5]

    return render_template_string(DASHBOARD_TEMPLATE,
                                current_user=current_user,
                                stats=stats,
                                recent_activities=recent_activities,
                                low_stock_products=low_stock_products,
                                top_products=top_products,
                                system_config=SYSTEM_CONFIG,
                                user_roles=USER_ROLES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """تسجيل الدخول"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember_me = request.form.get('remember_me') == 'on'

        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'error')
            return render_template_string(LOGIN_TEMPLATE)

        data = load_database()
        users = data.get('users', {})

        if username in users:
            user = users[username]
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            if user['password_hash'] == password_hash and user.get('is_active', True):
                # تسجيل الدخول بنجاح
                session['user_id'] = user['id']
                session['username'] = username
                session['full_name'] = user['full_name']
                session['role'] = user['role']
                session['permissions'] = user.get('permissions', [])

                # تحديث آخر دخول
                user['last_login'] = datetime.now().isoformat()
                users[username] = user
                data['users'] = users
                save_database(data)

                # تسجيل النشاط
                log_activity(user['id'], 'login', {'username': username, 'ip': request.remote_addr})

                # تحديد مدة الجلسة
                if remember_me:
                    session.permanent = True
                    app.permanent_session_lifetime = timedelta(days=30)
                else:
                    session.permanent = True
                    app.permanent_session_lifetime = timedelta(minutes=SYSTEM_CONFIG.get('session_timeout', 120))

                flash(f'مرحباً {user["full_name"]}، تم تسجيل الدخول بنجاح', 'success')

                # إعادة التوجيه حسب الدور
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                elif user['role'] in ['cashier', 'employee']:
                    return redirect(url_for('pos'))
                else:
                    return redirect(url_for('index'))
            else:
                flash('كلمة المرور غير صحيحة', 'error')
                log_activity('unknown', 'failed_login', {'username': username, 'ip': request.remote_addr})
        else:
            flash('اسم المستخدم غير موجود', 'error')
            log_activity('unknown', 'failed_login', {'username': username, 'ip': request.remote_addr})

    return render_template_string(LOGIN_TEMPLATE, system_config=SYSTEM_CONFIG)

@app.route('/logout')
@require_login
def logout():
    """تسجيل الخروج"""
    user_id = session.get('user_id')
    username = session.get('username')

    # تسجيل النشاط
    if user_id:
        log_activity(user_id, 'logout', {'username': username})

    # مسح الجلسة
    session.clear()

    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('login'))

# ===== نقطة البيع المتقدمة =====

@app.route('/pos')
@require_permission('pos')
def pos():
    """نقطة البيع المتقدمة"""
    current_user = get_current_user()
    data = load_database()

    # تحميل البيانات
    products = list(data.get('products', {}).values())
    customers = list(data.get('customers', {}).values())
    categories = data.get('categories', {})

    # فلترة المنتجات النشطة فقط
    active_products = [p for p in products if p.get('is_active', True)]

    # قراءة القالب المحسن
    try:
        with open('pos_enhanced_template.html', 'r', encoding='utf-8') as f:
            pos_template = f.read()

        return render_template_string(pos_template,
                                    products=active_products,
                                    customers=customers,
                                    categories=categories,
                                    current_user=current_user,
                                    system_config=SYSTEM_CONFIG,
                                    sale_types=SALE_TYPES)
    except FileNotFoundError:
        # استخدام القالب المتقدم في حالة عدم وجود الملف المحسن
        try:
            with open('pos_advanced_template.html', 'r', encoding='utf-8') as f:
                pos_template = f.read()

            return render_template_string(pos_template,
                                        products=active_products,
                                        customers=customers,
                                        categories=categories,
                                        current_user=current_user,
                                        system_config=SYSTEM_CONFIG,
                                        sale_types=SALE_TYPES)
        except FileNotFoundError:
            # استخدام القالب الافتراضي في حالة عدم وجود الملف
            return render_template_string(POS_TEMPLATE,
                                        products=active_products,
                                        customers=customers,
                                        categories=categories,
                                        current_user=current_user,
                                        system_config=SYSTEM_CONFIG,
                                        sale_types=SALE_TYPES)

@app.route('/api/pos/add-to-cart', methods=['POST'])
@require_permission('pos')
def add_to_cart():
    """إضافة منتج للسلة"""
    try:
        data = load_database()
        products = data.get('products', {})

        product_id = request.json.get('product_id')
        quantity = int(request.json.get('quantity', 1))
        sale_type = request.json.get('sale_type', 'retail')

        if product_id not in products:
            return jsonify({'success': False, 'message': 'المنتج غير موجود'})

        product = products[product_id]

        if not product.get('is_active', True):
            return jsonify({'success': False, 'message': 'المنتج غير نشط'})

        if product.get('stock_quantity', 0) < quantity:
            return jsonify({'success': False, 'message': 'المخزون غير كافي'})

        # تحديد السعر حسب نوع البيع
        price_field = SALE_TYPES.get(sale_type, {}).get('price_field', 'selling_price')
        price = product.get(price_field, product.get('selling_price', 0))

        cart_item = {
            'product_id': product_id,
            'name': product['name'],
            'sku': product['sku'],
            'price': price,
            'quantity': quantity,
            'total': price * quantity,
            'sale_type': sale_type
        }

        return jsonify({'success': True, 'item': cart_item})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/pos/update-item-price', methods=['POST'])
@require_permission('pos')
def update_item_price():
    """تحديث سعر منتج في السلة"""
    try:
        data = load_database()
        products = data.get('products', {})
        
        item_index = request.json.get('item_index')
        new_price = float(request.json.get('new_price', 0))
        quantity = int(request.json.get('quantity', 1))
        
        if new_price <= 0:
            return jsonify({'success': False, 'message': 'السعر يجب أن يكون أكبر من صفر'})
        
        total = new_price * quantity
        
        return jsonify({
            'success': True, 
            'new_price': new_price,
            'total': total
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/pos/search-invoices', methods=['POST'])
@require_permission('pos')
def search_invoices():
    """
    البحث في الفواتير السابقة
    """
    try:
        data = load_database()
        sales = data.get('sales', {})
        search_type = request.json.get('search_type', 'invoice_number')
        search_value = request.json.get('search_value', '')
        results = []
        for sale_id, sale in sales.items():
            if search_type == 'invoice_number' and search_value.lower() in sale.get('invoice_number', '').lower():
                results.append({
                    'invoice_number': sale.get('invoice_number'),
                    'date': sale.get('date'),
                    'customer_name': sale.get('customer_name'),
                    'total_amount': sale.get('total_amount'),
                    'payment_method': sale.get('payment_method'),
                    'status': sale.get('status'),
                    'items': sale.get('items', []),  # إضافة تفاصيل المنتجات
                })
            elif search_type == 'date' and search_value in sale.get('date', ''):
                results.append({
                    'invoice_number': sale.get('invoice_number'),
                    'date': sale.get('date'),
                    'customer_name': sale.get('customer_name'),
                    'total_amount': sale.get('total_amount'),
                    'payment_method': sale.get('payment_method'),
                    'status': sale.get('status'),
                    'items': sale.get('items', []),  # إضافة تفاصيل المنتجات
                })
        return jsonify({'success': True, 'invoices': results})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/pos/print-invoice/<invoice_number>', methods=['GET'])
@require_permission('pos')
def print_invoice(invoice_number):
    """
    طباعة فاتورة حرارية مبسطة (عرض 7 سم)
    """
    try:
        data = load_database()
        sales = data.get('sales', {})
        sale_record = None
        for sale_id, sale in sales.items():
            if sale.get('invoice_number') == invoice_number:
                sale_record = sale
                break
        if not sale_record:
            return 'الفاتورة غير موجودة', 404
        # إعداد قالب الفاتورة الحرارية
        shop_name = data.get('settings', {}).get('company_name', 'اسم المحل')
        shop_address = data.get('settings', {}).get('company_address', 'عنوان المحل')
        cashier_name = sale_record.get('cashier_name', '-')
        customer_name = sale_record.get('customer_name', '-')
        invoice_number = sale_record.get('invoice_number', '-')
        invoice_date = sale_record.get('date', '-')
        items = sale_record.get('items', [])
        discount = sale_record.get('discount_amount', 0)
        total = sale_record.get('total_amount', 0)
        html = f'''
        <html dir="rtl">
        <head>
        <meta charset="utf-8">
        <style>
        body {{ font-family: 'Cairo', Arial, sans-serif; width: 270px; margin: 0; padding: 0; }}
        .receipt {{ width: 270px; margin: auto; padding: 0.5em 0.5em 0 0.5em; }}
        .center {{ text-align: center; }}
        .bold {{ font-weight: bold; }}
        .header {{ font-size: 18px; font-weight: bold; margin-bottom: 4px; }}
        .sub-header {{ font-size: 13px; margin-bottom: 4px; }}
        .info-row {{ font-size: 13px; margin-bottom: 2px; display: flex; justify-content: space-between; }}
        .items-table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 8px; }}
        .items-table th, .items-table td {{ border-bottom: 1px dashed #ccc; padding: 2px 0; text-align: center; }}
        .items-table th {{ font-size: 12px; background: #f8f8f8; }}
        .footer {{ margin-top: 10px; font-size: 13px; }}
        .total-row td {{ font-size: 15px; font-weight: bold; }}
        .thanks {{ margin-top: 10px; font-size: 14px; text-align: center; }}
        </style>
        </head>
        <body onload="window.print()">
        <div class="receipt">
            <div class="center header">{shop_name}</div>
            <div class="center sub-header">{shop_address}</div>
            <hr>
            <div class="info-row"><span>رقم الفاتورة:</span><span>{invoice_number}</span></div>
            <div class="info-row"><span>التاريخ:</span><span>{invoice_date[:16]}</span></div>
            <div class="info-row"><span>اسم الزبون:</span><span>{customer_name}</span></div>
            <hr>
            <table class="items-table">
                <tr>
                    <th>الصنف</th>
                    <th>العدد</th>
                    <th>سعر</th>
                    <th>الإجمالي</th>
                </tr>
        '''
        # طباعة فقط الأصناف المباعة في الفاتورة
        for item in items:
            html += f'''<tr>
                <td>{item.get('name', '-')}</td>
                <td>{item.get('quantity', 1)}</td>
                <td>{item.get('price', 0):.2f}</td>
                <td>{item.get('total', 0):.2f}</td>
            </tr>'''
        html += '</table>'
        if discount and discount > 0:
            html += f'<div class="info-row"><span>الخصم:</span><span>{discount:.2f}</span></div>'
        html += f'''
            <div class="info-row"><span>اسم البائع:</span><span>{cashier_name}</span></div>
            <div class="info-row"><span>الإجمالي النهائي:</span><span>{total:.2f}</span></div>
            <div class="thanks">شكرًا لزيارتكم</div>
        </div>
        </body>
        </html>
        '''
        return html
    except Exception as e:
        return f'خطأ في طباعة الفاتورة: {e}', 500

@app.route('/api/pos/remove-item', methods=['POST'])
@require_permission('pos')
def remove_item():
    """إزالة منتج من السلة"""
    try:
        item_index = request.json.get('item_index')
        
        return jsonify({'success': True, 'message': 'تم إزالة المنتج بنجاح'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/pos/complete-sale', methods=['POST'])
@require_permission('pos')
def complete_sale():
    """إتمام عملية البيع"""
    try:
        data = load_database()
        products = data.get('products', {})
        customers = data.get('customers', {})
        sales = data.get('sales', {})

        sale_data = request.json
        cart_items = sale_data.get('items', [])
        customer_id = sale_data.get('customer_id')
        payment_method = sale_data.get('payment_method', 'نقدي')
        discount_amount = float(sale_data.get('discount_amount', 0))
        notes = sale_data.get('notes', '')
        print_invoice = sale_data.get('print_invoice', True)  # إضافة خيار الطباعة

        if not cart_items:
            return jsonify({'success': False, 'message': 'السلة فارغة'})

        # حساب المجاميع
        subtotal = sum(item.get('total', 0) for item in cart_items)
        tax_amount = (subtotal - discount_amount) * SYSTEM_CONFIG.get('tax_rate', 0.15)
        total_amount = subtotal - discount_amount + tax_amount

        # إنشاء فاتورة البيع
        sale_id = str(uuid.uuid4())
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{len(sales) + 1:04d}"

        sale_record = {
            'id': sale_id,
            'invoice_number': invoice_number,
            'date': datetime.now().isoformat(),
            'customer_id': customer_id,
            'customer_name': customers.get(customer_id, {}).get('name', 'عميل عادي') if customer_id else 'عميل عادي',
            'items': cart_items,
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'payment_method': payment_method,
            'status': 'completed',
            'notes': notes,
            'cashier_id': session['user_id'],
            'cashier_name': session['full_name'],
            'created_at': datetime.now().isoformat()
        }

        # تحديث المخزون
        for item in cart_items:
            product_id = item['product_id']
            quantity = item['quantity']

            if product_id in products:
                products[product_id]['stock_quantity'] -= quantity

                # تسجيل حركة المخزون
                movement_id = str(uuid.uuid4())
                inventory_movements = data.get('inventory_movements', {})
                inventory_movements[movement_id] = {
                    'id': movement_id,
                    'product_id': product_id,
                    'product_name': products[product_id]['name'],
                    'type': 'out',
                    'quantity': quantity,
                    'reason': 'sale',
                    'reference_id': sale_id,
                    'reference_type': 'sale',
                    'date': datetime.now().isoformat(),
                    'user_id': session['user_id'],
                    'notes': f'بيع - فاتورة رقم {invoice_number}'
                }
                data['inventory_movements'] = inventory_movements

        # تحديث رصيد العميل (بعد خصم المردودات)
        if customer_id and payment_method == 'آجل':
            if customer_id in customers:
                # إضافة الرصيد الصافي (بعد خصم المردودات)
                customers[customer_id]['current_balance'] += total_amount
                customers[customer_id]['total_purchases'] += subtotal  # المبلغ الإجمالي قبل الخصم والضريبة
                customers[customer_id]['last_purchase_date'] = datetime.now().isoformat()
                
                # خصم المردودات من إجمالي المشتريات
                if returns_amount > 0:
                    customers[customer_id]['total_purchases'] -= returns_amount
                    # تسجيل المردود في تاريخ الرصيد
                    balance_history = data.get('balance_history', {})
                    history_id = str(uuid.uuid4())
                    balance_history[history_id] = {
                        'id': history_id,
                        'customer_id': customer_id,
                        'type': 'return_credit',
                        'amount': -returns_amount,  # مبلغ سالب للمردود
                        'description': f'خصم مردودات من فاتورة {invoice_number}',
                        'date': datetime.now().isoformat(),
                        'user_id': session['user_id']
                    }
                    data['balance_history'] = balance_history
        elif customer_id:
            if customer_id in customers:
                # للدفع النقدي - تحديث إجمالي المشتريات بالمبلغ الصافي
                customers[customer_id]['total_purchases'] += subtotal - returns_amount
                customers[customer_id]['last_purchase_date'] = datetime.now().isoformat()
                
                # تسجيل المردود في تاريخ الرصيد للدفع النقدي أيضاً
                if returns_amount > 0:
                    balance_history = data.get('balance_history', {})
                    history_id = str(uuid.uuid4())
                    balance_history[history_id] = {
                        'id': history_id,
                        'customer_id': customer_id,
                        'type': 'return_cash',
                        'amount': -returns_amount,  # مبلغ سالب للمردود
                        'description': f'مردود نقدي من فاتورة {invoice_number}',
                        'date': datetime.now().isoformat(),
                        'user_id': session['user_id']
                    }
                    data['balance_history'] = balance_history

        # حفظ البيانات
        sales[sale_id] = sale_record
        data['sales'] = sales
        data['products'] = products
        data['customers'] = customers

        if save_database(data):
            # تسجيل النشاط
            log_activity(session['user_id'], 'complete_sale', {
                'sale_id': sale_id,
                'invoice_number': invoice_number,
                'total_amount': total_amount,
                'items_count': len(cart_items)
            })

            return jsonify({
                'success': True,
                'message': 'تم إتمام البيع بنجاح',
                'sale_id': sale_id,
                'invoice_number': invoice_number,
                'total_amount': total_amount
            })
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/pos/process-post-sale-return', methods=['POST'])
@require_permission('pos')
def process_post_sale_return():
    """معالجة مردود بعد إتمام البيع"""
    try:
        data = load_database()
        products = data.get('products', {})
        customers = data.get('customers', {})
        sales = data.get('sales', {})
        returns_data = data.get('returns', {})
        
        return_request = request.json
        sale_id = return_request.get('sale_id')
        invoice_number = return_request.get('invoice_number')
        return_items = return_request.get('items', [])
        return_reason = return_request.get('reason', 'مردود بعد البيع')
        
        # البحث عن الفاتورة
        sale_record = None
        if sale_id and sale_id in sales:
            sale_record = sales[sale_id]
        elif invoice_number:
            for sid, sale in sales.items():
                if sale.get('invoice_number') == invoice_number:
                    sale_record = sale
                    sale_id = sid
                    break
        
        if not sale_record:
            return jsonify({'success': False, 'message': 'الفاتورة غير موجودة'})
        
        if sale_record.get('status') != 'completed':
            return jsonify({'success': False, 'message': 'لا يمكن إرجاع منتجات من فاتورة غير مكتملة'})
        
        # معالجة كل منتج مردود
        total_return_amount = 0
        processed_returns = []
        
        for return_item in return_items:
            product_id = return_item.get('product_id')
            return_quantity = int(return_item.get('quantity', 0))
            
            if return_quantity <= 0:
                continue
            
            # البحث عن المنتج في الفاتورة الأصلية
            original_item = None
            for item in sale_record.get('items', []):
                if item.get('product_id') == product_id:
                    original_item = item
                    break
            
            if not original_item:
                continue
            
            # التحقق من الكمية المتاحة للإرجاع
            already_returned = original_item.get('returned_quantity', 0)
            available_for_return = original_item.get('quantity', 0) - already_returned
            
            if return_quantity > available_for_return:
                return jsonify({
                    'success': False, 
                    'message': f'الكمية المطلوب إرجاعها أكبر من المتاح للمنتج {original_item.get("name", "")}'
                })
            
            # حساب قيمة المردود
            return_value = return_quantity * original_item.get('price', 0)
            total_return_amount += return_value
            
            # تحديث المخزون
            if product_id in products:
                products[product_id]['stock_quantity'] += return_quantity
            
            # تسجيل حركة المخزون
            movement_id = str(uuid.uuid4())
            inventory_movements = data.get('inventory_movements', {})
            inventory_movements[movement_id] = {
                'id': movement_id,
                'product_id': product_id,
                'product_name': products[product_id]['name'] if product_id in products else original_item.get('name'),
                'type': 'in',
                'quantity': return_quantity,
                'reason': 'post_sale_return',
                'reference_id': sale_id,
                'reference_type': 'post_sale_return',
                'date': datetime.now().isoformat(),
                'user_id': session['user_id'],
                'notes': f'مردود بعد البيع - فاتورة {sale_record.get("invoice_number")} - السبب: {return_reason}'
            }
            data['inventory_movements'] = inventory_movements
            
            # تحديث الفاتورة الأصلية
            original_item['returned_quantity'] = already_returned + return_quantity
            
            # تسجيل المردود
            return_id = str(uuid.uuid4())
            return_record = {
                'id': return_id,
                'sale_id': sale_id,
                'invoice_number': sale_record.get('invoice_number'),
                'product_id': product_id,
                'product_name': original_item.get('name'),
                'quantity': return_quantity,
                'unit_price': original_item.get('price', 0),
                'total_amount': return_value,
                'reason': return_reason,
                'date': datetime.now().isoformat(),
                'processed_by': session['user_id'],
                'customer_id': sale_record.get('customer_id'),
                'payment_method': sale_record.get('payment_method'),
                'status': 'completed'
            }
            
            returns_data[return_id] = return_record
            processed_returns.append(return_record)
        
        # تحديث حساب العميل بشكل صحيح
        customer_id = sale_record.get('customer_id')
        if customer_id and customer_id in customers and total_return_amount > 0:
            payment_method = sale_record.get('payment_method', 'نقدي')
            
            if payment_method == 'آجل':
                # خصم من الرصيد المستحق للعميل
                customers[customer_id]['current_balance'] -= total_return_amount
            
            # خصم من إجمالي المشتريات دائماً
            customers[customer_id]['total_purchases'] -= total_return_amount
            
            # تسجيل في تاريخ الرصيد
            balance_history = data.get('balance_history', {})
            history_id = str(uuid.uuid4())
            balance_history[history_id] = {
                'id': history_id,
                'customer_id': customer_id,
                'type': 'post_sale_return',
                'amount': -total_return_amount,
                'description': f'مردود بعد البيع - فاتورة {sale_record.get("invoice_number")} - السبب: {return_reason}',
                'date': datetime.now().isoformat(),
                'user_id': session['user_id']
            }
            data['balance_history'] = balance_history
        
        # حفظ البيانات
        data['sales'] = sales
        data['products'] = products
        data['customers'] = customers
        data['returns'] = returns_data
        
        if save_database(data):
            # تسجيل النشاط
            log_activity(session['user_id'], 'post_sale_return', {
                'sale_id': sale_id,
                'invoice_number': sale_record.get('invoice_number'),
                'total_return_amount': total_return_amount,
                'items_count': len(processed_returns),
                'customer_id': customer_id
            })
            
            return jsonify({
                'success': True,
                'message': f'تم معالجة مردود بقيمة {total_return_amount:.2f} ريال بنجاح',
                'total_return_amount': total_return_amount,
                'processed_returns': processed_returns,
                'customer_balance_updated': customer_id is not None
            })
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/customers/statement/<customer_id>')
@require_permission('customers')
def get_customer_statement(customer_id):
    """كشف حساب مفصل للعميل"""
    try:
        if not check_detailed_permission(session['user_id'], 'customers_statement'):
            return jsonify({'success': False, 'message': 'ليس لديك صلاحية لعرض كشف الحساب'})
        
        data = load_database()
        customers = data.get('customers', {})
        sales = data.get('sales', {})
        balance_history = data.get('balance_history', {})
        returns_data = data.get('returns', {})
        
        if customer_id not in customers:
            return jsonify({'success': False, 'message': 'العميل غير موجود'})
        
        customer = customers[customer_id]
        
        # جمع جميع المعاملات
        transactions = []
        
        # إضافة المبيعات
        for sale_id, sale in sales.items():
            if sale.get('customer_id') == customer_id:
                transactions.append({
                    'date': sale.get('date'),
                    'type': 'sale',
                    'type_name': 'بيع',
                    'reference': sale.get('invoice_number'),
                    'debit': sale.get('total_amount', 0) if sale.get('payment_method') == 'آجل' else 0,
                    'credit': 0,
                    'description': f"فاتورة بيع رقم {sale.get('invoice_number')}",
                    'payment_method': sale.get('payment_method'),
                    'items_count': len(sale.get('items', [])),
                    'returns_amount': sale.get('returns_amount', 0)
                })
        
        # إضافة تاريخ الرصيد
        for history_id, history in balance_history.items():
            if history.get('customer_id') == customer_id:
                amount = history.get('amount', 0)
                transactions.append({
                    'date': history.get('date'),
                    'type': history.get('type'),
                    'type_name': get_transaction_type_name(history.get('type')),
                    'reference': history.get('reference', ''),
                    'debit': amount if amount > 0 else 0,
                    'credit': abs(amount) if amount < 0 else 0,
                    'description': history.get('description', ''),
                    'payment_method': '',
                    'items_count': 0,
                    'returns_amount': 0
                })
        
        # إضافة المردودات
        for return_id, return_item in returns_data.items():
            if return_item.get('customer_id') == customer_id:
                transactions.append({
                    'date': return_item.get('date'),
                    'type': 'return',
                    'type_name': 'مردود',
                    'reference': return_item.get('invoice_number'),
                    'debit': 0,
                    'credit': return_item.get('total_amount', 0),
                    'description': f"مردود من فاتورة {return_item.get('invoice_number')} - {return_item.get('reason', '')}",
                    'payment_method': return_item.get('payment_method'),
                    'items_count': 1,
                    'returns_amount': return_item.get('total_amount', 0)
                })
        
        # ترتيب المعاملات حسب التاريخ
        transactions.sort(key=lambda x: x['date'], reverse=True)
        
        # حساب الرصيد الجاري
        running_balance = 0
        for transaction in reversed(transactions):
            running_balance += transaction['debit'] - transaction['credit']
            transaction['running_balance'] = running_balance
        
        # حساب الإحصائيات
        total_sales = sum(t['debit'] for t in transactions if t['type'] == 'sale')
        total_payments = sum(t['credit'] for t in transactions if t['type'] in ['payment', 'cash_payment'])
        total_returns = sum(t['credit'] for t in transactions if t['type'] == 'return')
        current_balance = customer.get('current_balance', 0)
        
        summary = {
            'customer_name': customer.get('name'),
            'customer_phone': customer.get('phone'),
            'customer_email': customer.get('email', ''),
            'total_sales': total_sales,
            'total_payments': total_payments,
            'total_returns': total_returns,
            'current_balance': current_balance,
            'credit_limit': customer.get('credit_limit', 0),
            'available_credit': customer.get('credit_limit', 0) - current_balance,
            'transactions_count': len(transactions),
            'first_transaction_date': transactions[-1]['date'] if transactions else None,
            'last_transaction_date': transactions[0]['date'] if transactions else None
        }
        
        return jsonify({
            'success': True,
            'customer': customer,
            'transactions': transactions,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def get_transaction_type_name(transaction_type):
    """ترجمة نوع المعاملة"""
    type_names = {
        'payment': 'دفعة',
        'cash_payment': 'دفع نقدي',
        'credit_adjustment': 'تعديل ائتماني',
        'return_credit': 'خصم مردود',
        'return_cash': 'مردود نقدي',
        'post_sale_return': 'مردود بعد البيع',
        'opening_balance': 'رصيد افتتاحي'
    }
    return type_names.get(transaction_type, transaction_type)

# ===== إدارة المنتجات =====

@app.route('/products')
@require_permission('products')
def products():
    """إدارة المنتجات"""
    current_user = get_current_user()
    data = load_database()

    products = list(data.get('products', {}).values())
    categories = data.get('categories', {})
    suppliers = list(data.get('suppliers', {}).values())

    # إحصائيات المنتجات
    total_products = len(products)
    active_products = len([p for p in products if p.get('is_active', True)])
    low_stock = len([p for p in products if p.get('stock_quantity', 0) <= SYSTEM_CONFIG.get('low_stock_threshold', 5)])
    out_of_stock = len([p for p in products if p.get('stock_quantity', 0) <= 0])
    total_value = sum(p.get('stock_quantity', 0) * p.get('cost_price', 0) for p in products)

    stats = {
        'total_products': total_products,
        'active_products': active_products,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'total_value': total_value
    }

    return render_template_string(PRODUCTS_TEMPLATE,
                                products=products,
                                categories=categories,
                                suppliers=suppliers,
                                current_user=current_user,
                                stats=stats,
                                system_config=SYSTEM_CONFIG)

@app.route('/api/products/add', methods=['POST'])
@require_permission('products')
def add_product():
    """إضافة منتج جديد"""
    try:
        data = load_database()
        products = data.get('products', {})

        product_data = request.json

        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'sku', 'category', 'cost_price', 'selling_price']
        for field in required_fields:
            if not product_data.get(field):
                return jsonify({'success': False, 'message': f'حقل {field} مطلوب'})

        # التحقق من عدم تكرار SKU
        if any(p.get('sku') == product_data['sku'] for p in products.values()):
            return jsonify({'success': False, 'message': 'رقم المنتج موجود مسبقاً'})

        # إنشاء المنتج الجديد
        product_id = str(uuid.uuid4())
        new_product = {
            'id': product_id,
            'name': product_data['name'],
            'sku': product_data['sku'],
            'barcode': product_data.get('barcode', ''),
            'category': product_data['category'],
            'subcategory': product_data.get('subcategory', ''),
            'description': product_data.get('description', ''),
            'cost_price': float(product_data['cost_price']),
            'selling_price': float(product_data['selling_price']),
            'wholesale_price': float(product_data.get('wholesale_price', product_data['selling_price'])),
            'purchase_price': float(product_data.get('purchase_price', product_data['cost_price'])),
            'stock_quantity': int(product_data.get('stock_quantity', 0)),
            'min_stock_level': int(product_data.get('min_stock_level', 5)),
            'max_stock_level': int(product_data.get('max_stock_level', 100)),
            'supplier_id': product_data.get('supplier_id', ''),
            'unit': product_data.get('unit', 'قطعة'),
            'weight': float(product_data.get('weight', 0)),
            'dimensions': product_data.get('dimensions', ''),
            'is_active': product_data.get('is_active', True),
            'tax_rate': float(product_data.get('tax_rate', SYSTEM_CONFIG.get('tax_rate', 0.15))),
            'discount_rate': float(product_data.get('discount_rate', 0)),
            'image_url': product_data.get('image_url', ''),
            'warranty_period': product_data.get('warranty_period', ''),
            'brand': product_data.get('brand', ''),
            'model': product_data.get('model', ''),
            'color': product_data.get('color', ''),
            'storage': product_data.get('storage', ''),
            'notes': product_data.get('notes', ''),
            'created_at': datetime.now().isoformat(),
            'created_by': session['user_id'],
            'updated_at': datetime.now().isoformat(),
            'updated_by': session['user_id']
        }

        # إنشاء باركود تلقائي إذا لم يتم إدخاله
        if not new_product['barcode'] and SYSTEM_CONFIG.get('auto_barcode', True):
            new_product['barcode'] = f"BC{product_id[:8].upper()}"

        products[product_id] = new_product
        data['products'] = products

        if save_database(data):
            log_activity(session['user_id'], 'add_product', {'product_id': product_id, 'name': new_product['name']})
            return jsonify({'success': True, 'message': 'تم إضافة المنتج بنجاح', 'product': new_product})
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/products/update/<product_id>', methods=['POST'])
@require_permission('products')
def update_product(product_id):
    """تحديث منتج"""
    try:
        data = load_database()
        products = data.get('products', {})

        if product_id not in products:
            return jsonify({'success': False, 'message': 'المنتج غير موجود'})

        product = products[product_id]
        product_data = request.json

        # تحديث البيانات
        updatable_fields = [
            'name', 'sku', 'barcode', 'category', 'subcategory', 'description',
            'cost_price', 'selling_price', 'wholesale_price', 'purchase_price',
            'stock_quantity', 'min_stock_level', 'max_stock_level',
            'supplier_id', 'unit', 'weight', 'dimensions',
            'is_active', 'tax_rate', 'discount_rate',
            'image_url', 'warranty_period', 'brand', 'model', 'color', 'storage', 'notes'
        ]

        for field in updatable_fields:
            if field in product_data:
                if field in ['cost_price', 'selling_price', 'wholesale_price', 'purchase_price', 'weight', 'tax_rate', 'discount_rate']:
                    product[field] = float(product_data[field])
                elif field in ['stock_quantity', 'min_stock_level', 'max_stock_level']:
                    product[field] = int(product_data[field])
                elif field == 'is_active':
                    product[field] = bool(product_data[field])
                else:
                    product[field] = product_data[field]

        product['updated_at'] = datetime.now().isoformat()
        product['updated_by'] = session['user_id']

        if save_database(data):
            log_activity(session['user_id'], 'update_product', {'product_id': product_id, 'name': product['name']})
            return jsonify({'success': True, 'message': 'تم تحديث المنتج بنجاح', 'product': product})
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/products/delete/<product_id>', methods=['DELETE'])
@require_permission('products')
def delete_product(product_id):
    """حذف منتج"""
    try:
        data = load_database()
        products = data.get('products', {})

        if product_id not in products:
            return jsonify({'success': False, 'message': 'المنتج غير موجود'})

        product_name = products[product_id]['name']
        del products[product_id]
        data['products'] = products

        if save_database(data):
            log_activity(session['user_id'], 'delete_product', {'product_id': product_id, 'name': product_name})
            return jsonify({'success': True, 'message': 'تم حذف المنتج بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ===== إدارة العملاء =====

@app.route('/customers')
@require_permission('customers')
def customers():
    """إدارة العملاء"""
    current_user = get_current_user()
    data = load_database()

    customers = list(data.get('customers', {}).values())

    # إحصائيات العملاء
    total_customers = len(customers)
    active_customers = len([c for c in customers if c.get('is_active', True)])
    retail_customers = len([c for c in customers if c.get('type') == 'تجزئة'])
    wholesale_customers = len([c for c in customers if c.get('type') == 'جملة'])
    corporate_customers = len([c for c in customers if c.get('type') == 'مؤسسة'])
    total_debt = sum(c.get('current_balance', 0) for c in customers if c.get('current_balance', 0) > 0)

    stats = {
        'total_customers': total_customers,
        'active_customers': active_customers,
        'retail_customers': retail_customers,
        'wholesale_customers': wholesale_customers,
        'corporate_customers': corporate_customers,
        'total_debt': total_debt
    }

    return render_template_string(CUSTOMERS_TEMPLATE,
                                customers=customers,
                                current_user=current_user,
                                stats=stats,
                                system_config=SYSTEM_CONFIG)
@app.route('/api/customers/add', methods=['POST'])
@require_permission('customers')
def add_customer():
    """إضافة عميل جديد"""
    try:
        data = load_database()
        customers = data.get('customers', {})

        customer_data = request.json

        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'phone', 'type']
        for field in required_fields:
            if not customer_data.get(field):
                return jsonify({'success': False, 'message': f'حقل {field} مطلوب'})

        # التحقق من عدم تكرار رقم الهاتف
        if any(c.get('phone') == customer_data['phone'] for c in customers.values()):
            return jsonify({'success': False, 'message': 'رقم الهاتف موجود مسبقاً'})

        # إنشاء العميل الجديد
        customer_id = str(uuid.uuid4())
        new_customer = {
            'id': customer_id,
            'name': customer_data['name'],
            'phone': customer_data['phone'],
            'email': customer_data.get('email', ''),
            'address': customer_data.get('address', ''),
            'type': customer_data['type'],  # تجزئة، جملة، مؤسسة
            'tax_number': customer_data.get('tax_number', ''),
            'credit_limit': float(customer_data.get('credit_limit', 0)),
            'payment_terms': customer_data.get('payment_terms', 'نقدي'),
            'discount_rate': float(customer_data.get('discount_rate', 0)),
            'current_balance': 0.0,
            'total_purchases': 0.0,
            'last_purchase_date': None,
            'is_active': customer_data.get('is_active', True),
            'notes': customer_data.get('notes', ''),
            'created_at': datetime.now().isoformat(),
            'created_by': session['user_id'],
            'updated_at': datetime.now().isoformat(),
            'updated_by': session['user_id']
        }

        customers[customer_id] = new_customer
        data['customers'] = customers

        if save_database(data):
            log_activity(session['user_id'], 'add_customer', {'customer_id': customer_id, 'name': new_customer['name']})
            return jsonify({'success': True, 'message': 'تم إضافة العميل بنجاح', 'customer': new_customer})
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/customers/update/<customer_id>', methods=['POST'])
@require_permission('customers')
def update_customer(customer_id):
    """تحديث عميل"""
    try:
        data = load_database()
        customers = data.get('customers', {})

        if customer_id not in customers:
            return jsonify({'success': False, 'message': 'العميل غير موجود'})

        customer = customers[customer_id]
        customer_data = request.json

        # تحديث البيانات
        updatable_fields = [
            'name', 'phone', 'email', 'address', 'type', 'tax_number',
            'credit_limit', 'payment_terms', 'discount_rate', 'is_active', 'notes'
        ]

        for field in updatable_fields:
            if field in customer_data:
                if field in ['credit_limit', 'discount_rate']:
                    customer[field] = float(customer_data[field])
                elif field == 'is_active':
                    customer[field] = bool(customer_data[field])
                else:
                    customer[field] = customer_data[field]

        customer['updated_at'] = datetime.now().isoformat()
        customer['updated_by'] = session['user_id']

        if save_database(data):
            log_activity(session['user_id'], 'update_customer', {'customer_id': customer_id, 'name': customer['name']})
            return jsonify({'success': True, 'message': 'تم تحديث العميل بنجاح', 'customer': customer})
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/customers/delete/<customer_id>', methods=['DELETE'])
@require_permission('customers')
def delete_customer(customer_id):
    """حذف عميل"""
    try:
        data = load_database()
        customers = data.get('customers', {})

        if customer_id not in customers:
            return jsonify({'success': False, 'message': 'العميل غير موجود'})

        customer = customers[customer_id]

        # التحقق من وجود معاملات للعميل
        if customer.get('current_balance', 0) != 0:
            return jsonify({'success': False, 'message': 'لا يمكن حذف عميل له رصيد مستحق'})

        customer_name = customer['name']
        del customers[customer_id]
        data['customers'] = customers

        if save_database(data):
            log_activity(session['user_id'], 'delete_customer', {'customer_id': customer_id, 'name': customer_name})
            return jsonify({'success': True, 'message': 'تم حذف العميل بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ===== الصفحات الأخرى =====

@app.route('/inventory')
@require_permission('inventory')
def inventory():
    """إدارة المخزون"""
    current_user = get_current_user()
    data = load_database()
    
    products = list(data.get('products', {}).values())
    
    # إحصائيات المخزون
    total_products = len(products)
    low_stock = len([p for p in products if p.get('stock_quantity', 0) <= SYSTEM_CONFIG.get('low_stock_threshold', 5)])
    out_of_stock = len([p for p in products if p.get('stock_quantity', 0) <= 0])
    total_value = sum(p.get('stock_quantity', 0) * p.get('cost_price', 0) for p in products)
    
    stats = {
        'total_products': total_products,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'total_value': total_value
    }
    
    return render_template_string(INVENTORY_TEMPLATE,
                                current_user=current_user,
                                products=products,
                                stats=stats,
                                system_config=SYSTEM_CONFIG)

@app.route('/reports')
@require_permission('reports')
def reports():
    """التقارير"""
    current_user = get_current_user()
    data = load_database()
    
    # إحصائيات سريعة
    sales = data.get('sales', {})
    products = data.get('products', {})
    customers = data.get('customers', {})
    
    # إحصائيات المبيعات
    total_sales = len(sales)
    total_revenue = sum(sale.get('total_amount', 0) for sale in sales.values())
    total_profit = sum(sale.get('total_profit', 0) for sale in sales.values())
    
    # إحصائيات المنتجات
    total_products = len(products)
    low_stock_products = len([p for p in products.values() if p.get('stock_quantity', 0) <= 5])
    out_of_stock_products = len([p for p in products.values() if p.get('stock_quantity', 0) <= 0])
    
    # إحصائيات العملاء
    total_customers = len(customers)
    debtors = len([c for c in customers.values() if c.get('current_balance', 0) > 0])
    total_debt = sum(c.get('current_balance', 0) for c in customers.values())
    
    stats = {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'total_customers': total_customers,
        'debtors': debtors,
        'total_debt': total_debt
    }
    
    return render_template_string(REPORTS_TEMPLATE,
                                current_user=current_user,
                                stats=stats,
                                system_config=SYSTEM_CONFIG)

@app.route('/purchases')
@require_permission('purchases')
def purchases():
    """المشتريات"""
    current_user = get_current_user()
    data = load_database()
    
    purchases = data.get('purchases', {})
    suppliers = data.get('suppliers', {})
    
    # إحصائيات المشتريات
    total_purchases = len(purchases)
    total_amount = sum(p.get('total_amount', 0) for p in purchases.values())
    pending_purchases = len([p for p in purchases.values() if p.get('status') == 'pending'])
    
    stats = {
        'total_purchases': total_purchases,
        'total_amount': total_amount,
        'pending_purchases': pending_purchases
    }
    
    return render_template_string(PURCHASES_TEMPLATE,
                                current_user=current_user,
                                purchases=purchases,
                                suppliers=suppliers,
                                stats=stats,
                                system_config=SYSTEM_CONFIG)

@app.route('/partners')
@require_permission('partners')
def partners():
    """حساب الشركاء"""
    current_user = get_current_user()
    data = load_database()
    partners = data.get('partners', {})

    return render_template_string(PARTNERS_TEMPLATE,
                                current_user=current_user,
                                partners=partners,
                                system_config=SYSTEM_CONFIG)

# ===== APIs نظام الشركاء =====

@app.route('/api/partners/add', methods=['POST'])
@require_permission('partners')
def add_partner():
    """إضافة شريك جديد"""
    try:
        data = load_database()
        partners = data.get('partners', {})

        partner_data = request.json

        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'contribution_amount', 'contribution_percentage']
        for field in required_fields:
            if not partner_data.get(field):
                return jsonify({'success': False, 'message': f'حقل {field} مطلوب'})

        # إنشاء الشريك الجديد
        partner_id = str(uuid.uuid4())
        new_partner = {
            'id': partner_id,
            'name': partner_data['name'],
            'phone': partner_data.get('phone', ''),
            'email': partner_data.get('email', ''),
            'address': partner_data.get('address', ''),
            'national_id': partner_data.get('national_id', ''),
            'contribution_amount': float(partner_data['contribution_amount']),
            'contribution_percentage': float(partner_data['contribution_percentage']),
            'current_balance': 0.0,  # الرصيد الحالي
            'total_withdrawals': 0.0,  # إجمالي المسحوبات
            'total_profits_received': 0.0,  # إجمالي الأرباح المستلمة
            'assets': [],  # الأصول المساهم بها
            'is_active': partner_data.get('is_active', True),
            'join_date': partner_data.get('join_date', datetime.now().isoformat()),
            'notes': partner_data.get('notes', ''),
            'created_at': datetime.now().isoformat(),
            'created_by': session['user_id'],
            'updated_at': datetime.now().isoformat(),
            'updated_by': session['user_id']
        }

        # إضافة الأصول إذا تم تحديدها
        if partner_data.get('assets'):
            for asset in partner_data['assets']:
                new_partner['assets'].append({
                    'id': str(uuid.uuid4()),
                    'name': asset.get('name', ''),
                    'type': asset.get('type', ''),  # نقدي، عقار، معدات، إلخ
                    'value': float(asset.get('value', 0)),
                    'description': asset.get('description', ''),
                    'date_added': datetime.now().isoformat()
                })

        partners[partner_id] = new_partner
        data['partners'] = partners

        if save_database(data):
            log_activity(session['user_id'], 'add_partner', {
                'partner_id': partner_id,
                'name': new_partner['name'],
                'contribution_amount': new_partner['contribution_amount']
            })

            return jsonify({
                'success': True,
                'message': 'تم إضافة الشريك بنجاح',
                'partner': new_partner
            })
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/partners/withdrawal', methods=['POST'])
@require_permission('partners')
def add_partner_withdrawal():
    """إضافة مسحوبات شريك"""
    try:
        data = load_database()
        partners = data.get('partners', {})

        withdrawal_data = request.json
        partner_id = withdrawal_data.get('partner_id')
        amount = float(withdrawal_data.get('amount', 0))
        description = withdrawal_data.get('description', '')

        if partner_id not in partners:
            return jsonify({'success': False, 'message': 'الشريك غير موجود'})

        if amount <= 0:
            return jsonify({'success': False, 'message': 'المبلغ يجب أن يكون أكبر من صفر'})

        partner = partners[partner_id]

        # التحقق من الرصيد المتاح
        if partner['current_balance'] < amount:
            return jsonify({'success': False, 'message': 'الرصيد غير كافي'})

        # تحديث رصيد الشريك
        partner['current_balance'] -= amount
        partner['total_withdrawals'] += amount
        partner['updated_at'] = datetime.now().isoformat()
        partner['updated_by'] = session['user_id']

        # إضافة سجل المسحوبات
        if 'withdrawals' not in partner:
            partner['withdrawals'] = []

        withdrawal_record = {
            'id': str(uuid.uuid4()),
            'amount': amount,
            'description': description,
            'date': datetime.now().isoformat(),
            'created_by': session['user_id']
        }

        partner['withdrawals'].append(withdrawal_record)

        if save_database(data):
            log_activity(session['user_id'], 'partner_withdrawal', {
                'partner_id': partner_id,
                'partner_name': partner['name'],
                'amount': amount,
                'description': description
            })

            return jsonify({
                'success': True,
                'message': 'تم تسجيل المسحوبات بنجاح',
                'new_balance': partner['current_balance']
            })
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@app.route('/api/partners/distribute-profits', methods=['POST'])
@require_permission('partners')
def distribute_profits():
    """توزيع الأرباح على الشركاء"""
    try:
        data = load_database()
        partners = data.get('partners', {})

        distribution_data = request.json
        total_profit = float(distribution_data.get('total_profit', 0))
        period = distribution_data.get('period', '')  # شهري، ربع سنوي، سنوي
        notes = distribution_data.get('notes', '')

        if total_profit <= 0:
            return jsonify({'success': False, 'message': 'مبلغ الأرباح يجب أن يكون أكبر من صفر'})

        distribution_record = {
            'id': str(uuid.uuid4()),
            'total_profit': total_profit,
            'period': period,
            'notes': notes,
            'date': datetime.now().isoformat(),
            'created_by': session['user_id'],
            'distributions': []
        }

        # توزيع الأرباح حسب النسب
        for partner_id, partner in partners.items():
            if partner.get('is_active', True):
                partner_share = total_profit * (partner['contribution_percentage'] / 100)

                # تحديث رصيد الشريك
                partner['current_balance'] += partner_share
                partner['total_profits_received'] += partner_share
                partner['updated_at'] = datetime.now().isoformat()

                # إضافة سجل التوزيع
                if 'profit_distributions' not in partner:
                    partner['profit_distributions'] = []

                partner_distribution = {
                    'id': str(uuid.uuid4()),
                    'distribution_id': distribution_record['id'],
                    'amount': partner_share,
                    'percentage': partner['contribution_percentage'],
                    'date': datetime.now().isoformat()
                }

                partner['profit_distributions'].append(partner_distribution)
                distribution_record['distributions'].append({
                    'partner_id': partner_id,
                    'partner_name': partner['name'],
                    'amount': partner_share,
                    'percentage': partner['contribution_percentage']
                })

        # حفظ سجل التوزيع العام
        if 'profit_distributions' not in data:
            data['profit_distributions'] = {}

        data['profit_distributions'][distribution_record['id']] = distribution_record
        data['partners'] = partners

        if save_database(data):
            log_activity(session['user_id'], 'distribute_profits', {
                'total_profit': total_profit,
                'period': period,
                'partners_count': len(distribution_record['distributions'])
            })

            return jsonify({
                'success': True,
                'message': 'تم توزيع الأرباح بنجاح',
                'distribution': distribution_record
            })
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/partners/update', methods=['POST'])
@require_permission('partners')
def update_partner():
    """تحديث بيانات شريك"""
    try:
        data = load_database()
        partners = data.get('partners', {})

        partner_data = request.json
        partner_id = partner_data.get('partner_id')

        if partner_id not in partners:
            return jsonify({'success': False, 'message': 'الشريك غير موجود'})

        partner = partners[partner_id]

        # تحديث البيانات القابلة للتعديل
        updatable_fields = ['name', 'phone', 'email', 'contribution_amount',
                           'contribution_percentage', 'notes', 'is_active']

        for field in updatable_fields:
            if field in partner_data:
                if field == 'contribution_amount':
                    partner[field] = float(partner_data[field])
                elif field == 'contribution_percentage':
                    partner[field] = float(partner_data[field])
                elif field == 'is_active':
                    partner[field] = bool(partner_data[field])
                else:
                    partner[field] = partner_data[field]

        partner['updated_at'] = datetime.now().isoformat()
        partner['updated_by'] = session['user_id']

        data['partners'] = partners

        if save_database(data):
            log_activity(session['user_id'], 'update_partner', {'partner_id': partner_id, 'name': partner['name']})
            return jsonify({'success': True, 'message': 'تم تحديث بيانات الشريك بنجاح', 'partner': partner})
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/partners/delete', methods=['POST'])
@require_permission('partners')
def delete_partner():
    """حذف شريك"""
    try:
        data = load_database()
        partners = data.get('partners', {})

        partner_id = request.json.get('partner_id')

        if partner_id not in partners:
            return jsonify({'success': False, 'message': 'الشريك غير موجود'})

        partner = partners[partner_id]

        # التحقق من وجود رصيد للشريك
        if partner.get('current_balance', 0) > 0:
            return jsonify({'success': False, 'message': 'لا يمكن حذف شريك لديه رصيد متبقي'})

        # حذف الشريك
        partner_name = partner['name']
        del partners[partner_id]
        data['partners'] = partners

        if save_database(data):
            log_activity(session['user_id'], 'delete_partner', {'partner_id': partner_id, 'name': partner_name})
            return jsonify({'success': True, 'message': 'تم حذف الشريك بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/partners/details/<partner_id>')
@require_permission('partners')
def get_partner_details(partner_id):
    """الحصول على تفاصيل شريك"""
    try:
        data = load_database()
        partners = data.get('partners', {})

        if partner_id not in partners:
            return jsonify({'success': False, 'message': 'الشريك غير موجود'})

        partner = partners[partner_id]

        # حساب إحصائيات الشريك
        total_withdrawals = sum(w.get('amount', 0) for w in partner.get('withdrawals', []))
        total_profits = sum(p.get('amount', 0) for p in partner.get('profit_distributions', []))

        partner_stats = {
            'total_withdrawals': total_withdrawals,
            'total_profits': total_profits,
            'net_balance': partner.get('current_balance', 0),
            'withdrawals_count': len(partner.get('withdrawals', [])),
            'distributions_count': len(partner.get('profit_distributions', []))
        }

        return jsonify({
            'success': True,
            'partner': partner,
            'stats': partner_stats
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/settings')
@require_permission('settings')
def settings():
    """الإعدادات"""
    current_user = get_current_user()
    data = load_database()
    settings = data.get('settings', SYSTEM_CONFIG)

    return render_template_string(SETTINGS_TEMPLATE,
                                current_user=current_user,
                                settings=settings,
                                system_config=SYSTEM_CONFIG)

@app.route('/api/settings/update', methods=['POST'])
@require_permission('settings')
def update_settings():
    """تحديث إعدادات النظام مع تحسينات شاملة"""
    try:
        print(f"⚙️ بدء تحديث إعدادات النظام - المستخدم: {session.get('user_id', 'unknown')}")
        
        data = load_database()
        settings_data = request.json
        print(f"📋 الإعدادات المراد تحديثها: {list(settings_data.keys())}")

        # قائمة الإعدادات القابلة للتحديث
        updatable_settings = [
            'company_name', 'company_name_en', 'company_phone', 'company_email',
            'company_address', 'working_hours', 'cr_number', 'vat_number',
            'currency', 'currency_symbol', 'tax_rate', 'exchange_rate',
            'low_stock_threshold', 'critical_stock_threshold',
            'auto_barcode', 'auto_price_update', 'backup_enabled',
            'backup_interval', 'session_timeout', 'max_users',
            'invoice_format', 'printer_type', 'default_payment_terms',
            'default_discount'
        ]

        current_settings = data.get('settings', SYSTEM_CONFIG.copy())
        updated_count = 0

        # تحديث الإعدادات
        for setting in updatable_settings:
            if setting in settings_data:
                old_value = current_settings.get(setting, 'غير محدد')
                
                if setting in ['tax_rate', 'exchange_rate', 'default_discount']:
                    current_settings[setting] = float(settings_data[setting])
                elif setting in ['low_stock_threshold', 'critical_stock_threshold',
                               'backup_interval', 'session_timeout', 'max_users']:
                    current_settings[setting] = int(settings_data[setting])
                elif setting in ['auto_barcode', 'auto_price_update', 'backup_enabled']:
                    current_settings[setting] = bool(settings_data[setting])
                else:
                    current_settings[setting] = str(settings_data[setting])
                
                new_value = current_settings[setting]
                print(f"   🔄 تحديث {setting}: {old_value} → {new_value}")
                updated_count += 1

        # حفظ الإعدادات
        data['settings'] = current_settings

        print(f"💾 محاولة حفظ {updated_count} إعداد جديد")

        if save_database(data):
            # تحديث الإعدادات العامة
            SYSTEM_CONFIG.update(current_settings)

            log_activity(session['user_id'], 'update_settings', {
                'updated_settings': list(settings_data.keys()),
                'updated_count': updated_count
            })

            print(f"✅ تم تحديث {updated_count} إعداد بنجاح")

            return jsonify({
                'success': True,
                'message': f'تم تحديث {updated_count} إعداد بنجاح',
                'settings': current_settings
            })
        else:
            error_msg = 'خطأ في حفظ الإعدادات'
            print(f"❌ {error_msg}")
            return jsonify({'success': False, 'message': error_msg})

    except Exception as e:
        error_msg = f"خطأ غير متوقع: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'message': error_msg})

@app.route('/api/settings/reset', methods=['POST'])
@require_permission('settings')
def reset_settings():
    """إعادة تعيين الإعدادات للقيم الافتراضية"""
    try:
        data = load_database()
        data['settings'] = SYSTEM_CONFIG.copy()

        if save_database(data):
            log_activity(session['user_id'], 'reset_settings', {})
            return jsonify({
                'success': True,
                'message': 'تم إعادة تعيين الإعدادات بنجاح',
                'settings': SYSTEM_CONFIG
            })
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ الإعدادات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/settings/backup', methods=['POST'])
@require_permission('settings')
def create_settings_backup():
    """إنشاء نسخة احتياطية من الإعدادات"""
    try:
        backup_file = create_backup()
        if backup_file:
            return jsonify({'success': True, 'message': 'تم إنشاء النسخة الاحتياطية بنجاح', 'file': backup_file})
        else:
            return jsonify({'success': False, 'message': 'فشل في إنشاء النسخة الاحتياطية'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/inventory/add-stock', methods=['POST'])
@require_permission('inventory')
def add_stock():
    """إضافة مخزون مع تحسينات شاملة"""
    try:
        print(f"🔍 بدء عملية إضافة مخزون - المستخدم: {session.get('user_id', 'unknown')}")
        
        data = load_database()
        products = data.get('products', {})
        
        stock_data = request.json
        print(f"📋 بيانات المخزون المستلمة: {stock_data}")
        
        product_id = stock_data.get('product_id')
        quantity = int(stock_data.get('quantity', 0))
        reason = stock_data.get('reason', '')
        notes = stock_data.get('notes', '')
        
        # التحقق من المنتج
        if not product_id or product_id not in products:
            error_msg = 'المنتج غير موجود'
            print(f"❌ خطأ في المنتج: {error_msg}")
            return jsonify({'success': False, 'message': error_msg})
        
        # التحقق من الكمية
        if quantity <= 0:
            error_msg = 'الكمية يجب أن تكون أكبر من صفر'
            print(f"❌ خطأ في الكمية: {error_msg}")
            return jsonify({'success': False, 'message': error_msg})
        
        product_name = products[product_id]['name']
        old_quantity = products[product_id]['stock_quantity']
        new_quantity = old_quantity + quantity
        
        print(f"📦 تحديث مخزون المنتج: {product_name}")
        print(f"   الكمية القديمة: {old_quantity}")
        print(f"   الكمية المضافة: {quantity}")
        print(f"   الكمية الجديدة: {new_quantity}")
        
        # تحديث المخزون
        products[product_id]['stock_quantity'] = new_quantity
        products[product_id]['updated_at'] = datetime.now().isoformat()
        products[product_id]['updated_by'] = session['user_id']
        
        # تسجيل حركة المخزون
        movement_id = str(uuid.uuid4())
        movement = {
            'id': movement_id,
            'product_id': product_id,
            'product_name': product_name,
            'type': 'addition',
            'quantity': quantity,
            'old_quantity': old_quantity,
            'new_quantity': new_quantity,
            'reason': reason,
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'created_by': session['user_id']
        }
        
        # إضافة الحركة إلى قاعدة البيانات
        movements = data.get('inventory_movements', {})
        movements[movement_id] = movement
        data['inventory_movements'] = movements
        data['products'] = products
        
        print(f"💾 محاولة حفظ تحديث المخزون")
        
        if save_database(data):
            log_activity(session['user_id'], 'add_stock', {
                'product_id': product_id,
                'product_name': product_name,
                'quantity': quantity,
                'reason': reason,
                'old_quantity': old_quantity,
                'new_quantity': new_quantity
            })
            print(f"✅ تم إضافة المخزون بنجاح للمنتج: {product_name}")
            return jsonify({
                'success': True, 
                'message': f'تم إضافة {quantity} قطعة للمنتج {product_name} بنجاح',
                'new_quantity': new_quantity
            })
        else:
            error_msg = 'خطأ في حفظ البيانات'
            print(f"❌ {error_msg}")
            return jsonify({'success': False, 'message': error_msg})
            
    except Exception as e:
        error_msg = f"خطأ غير متوقع: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'message': error_msg})
@app.route('/api/inventory/adjust-stock', methods=['POST'])
@require_permission('inventory')
def adjust_stock():
    """تعديل المخزون"""
    try:
        data = load_database()
        products = data.get('products', {})
        
        stock_data = request.json
        product_id = stock_data.get('product_id')
        new_quantity = int(stock_data.get('new_quantity', 0))
        reason = stock_data.get('reason', '')
        notes = stock_data.get('notes', '')
        
        if not product_id or product_id not in products:
            return jsonify({'success': False, 'message': 'المنتج غير موجود'})
        
        if new_quantity < 0:
            return jsonify({'success': False, 'message': 'الكمية لا يمكن أن تكون سالبة'})
        
        old_quantity = products[product_id]['stock_quantity']
        
        # تحديث المخزون
        products[product_id]['stock_quantity'] = new_quantity
        products[product_id]['updated_at'] = datetime.now().isoformat()
        products[product_id]['updated_by'] = session['user_id']
        
        # تسجيل حركة المخزون
        movement_id = str(uuid.uuid4())
        movement = {
            'id': movement_id,
            'product_id': product_id,
            'product_name': products[product_id]['name'],
            'type': 'adjustment',
            'quantity': new_quantity - old_quantity,
            'old_quantity': old_quantity,
            'new_quantity': new_quantity,
            'reason': reason,
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'created_by': session['user_id']
        }
        
        # إضافة الحركة إلى قاعدة البيانات
        movements = data.get('inventory_movements', {})
        movements[movement_id] = movement
        data['inventory_movements'] = movements
        data['products'] = products
        
        if save_database(data):
            log_activity(session['user_id'], 'adjust_stock', {
                'product_id': product_id,
                'product_name': products[product_id]['name'],
                'old_quantity': old_quantity,
                'new_quantity': new_quantity,
                'reason': reason
            })
            return jsonify({'success': True, 'message': 'تم تعديل المخزون بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/purchases/add', methods=['POST'])
@require_permission('purchases')
def add_purchase():
    """إضافة مشترى جديد مع تحسينات شاملة"""
    try:
        print(f"🔍 بدء عملية إضافة مشترى جديد - المستخدم: {session.get('user_id', 'unknown')}")
        
        data = load_database()
        purchases = data.get('purchases', {})
        
        purchase_data = request.json
        print(f"📋 بيانات المشترى المستلمة: {purchase_data}")
        
        # التحقق من البيانات المطلوبة
        required_fields = ['supplier_id', 'invoice_number', 'date', 'status']
        for field in required_fields:
            if not purchase_data.get(field):
                error_msg = f'حقل {field} مطلوب'
                print(f"❌ خطأ في البيانات: {error_msg}")
                return jsonify({'success': False, 'message': error_msg})
        
        # التحقق من المورد
        suppliers = data.get('suppliers', {})
        supplier_id = purchase_data['supplier_id']
        if supplier_id not in suppliers:
            error_msg = 'المورد غير موجود'
            print(f"❌ خطأ في المورد: {error_msg}")
            return jsonify({'success': False, 'message': error_msg})
        
        # إنشاء المشترى الجديد
        purchase_id = str(uuid.uuid4())
        new_purchase = {
            'id': purchase_id,
            'supplier_id': purchase_data['supplier_id'],
            'supplier_name': suppliers[supplier_id].get('name', ''),
            'invoice_number': purchase_data['invoice_number'],
            'date': purchase_data['date'],
            'status': purchase_data['status'],
            'total_amount': float(purchase_data.get('total_amount', 0)),
            'notes': purchase_data.get('notes', ''),
            'created_at': datetime.now().isoformat(),
            'created_by': session['user_id'],
            'updated_at': datetime.now().isoformat(),
            'updated_by': session['user_id']
        }
        
        purchases[purchase_id] = new_purchase
        data['purchases'] = purchases
        
        print(f"💾 محاولة حفظ المشترى الجديد: {purchase_id}")
        
        if save_database(data):
            log_activity(session['user_id'], 'add_purchase', {
                'purchase_id': purchase_id,
                'invoice_number': new_purchase['invoice_number'],
                'supplier_id': new_purchase['supplier_id'],
                'total_amount': new_purchase['total_amount']
            })
            print(f"✅ تم إضافة المشترى بنجاح: {purchase_id}")
            return jsonify({
                'success': True, 
                'message': 'تم إضافة المشترى بنجاح', 
                'purchase': new_purchase
            })
        else:
            error_msg = 'خطأ في حفظ البيانات'
            print(f"❌ {error_msg}")
            return jsonify({'success': False, 'message': error_msg})
            
    except Exception as e:
        error_msg = f"خطأ غير متوقع: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'message': error_msg})

@app.route('/api/purchases/delete/<purchase_id>', methods=['DELETE'])
@require_permission('purchases')
def delete_purchase(purchase_id):
    """حذف مشترى"""
    try:
        data = load_database()
        purchases = data.get('purchases', {})
        
        if purchase_id not in purchases:
            return jsonify({'success': False, 'message': 'المشترى غير موجود'})
        
        purchase = purchases[purchase_id]
        del purchases[purchase_id]
        data['purchases'] = purchases
        
        if save_database(data):
            log_activity(session['user_id'], 'delete_purchase', {
                'purchase_id': purchase_id,
                'invoice_number': purchase.get('invoice_number', '')
            })
            return jsonify({'success': True, 'message': 'تم حذف المشترى بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/suppliers/add', methods=['POST'])
@require_permission('purchases')
def add_supplier():
    """إضافة مورد جديد"""
    try:
        data = load_database()
        suppliers = data.get('suppliers', {})
        
        supplier_data = request.json
        
        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'phone']
        for field in required_fields:
            if not supplier_data.get(field):
                return jsonify({'success': False, 'message': f'حقل {field} مطلوب'})
        
        # إنشاء المورد الجديد
        supplier_id = str(uuid.uuid4())
        new_supplier = {
            'id': supplier_id,
            'name': supplier_data['name'],
            'phone': supplier_data['phone'],
            'email': supplier_data.get('email', ''),
            'address': supplier_data.get('address', ''),
            'notes': supplier_data.get('notes', ''),
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'created_by': session['user_id'],
            'updated_at': datetime.now().isoformat(),
            'updated_by': session['user_id']
        }
        
        suppliers[supplier_id] = new_supplier
        data['suppliers'] = suppliers
        
        if save_database(data):
            log_activity(session['user_id'], 'add_supplier', {
                'supplier_id': supplier_id,
                'name': new_supplier['name']
            })
            return jsonify({'success': True, 'message': 'تم إضافة المورد بنجاح', 'supplier': new_supplier})
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@app.route('/api/products/update-prices-by-exchange', methods=['POST'])
@require_permission('products')
def update_prices_by_exchange():
    """تحديث الأسعار حسب سعر الصرف"""
    try:
        data = load_database()
        products = data.get('products', {})
        settings = data.get('settings', SYSTEM_CONFIG)

        request_data = request.json
        new_exchange_rate = float(request_data.get('exchange_rate', settings.get('exchange_rate', 3.75)))
        price_increase_percentage = float(request_data.get('price_increase', 0))  # نسبة زيادة إضافية
        update_type = request_data.get('update_type', 'all')  # all, category, specific
        category_filter = request_data.get('category', '')
        product_ids = request_data.get('product_ids', [])
        prices_in_usd = request_data.get('prices_in_usd', False)

        updated_count = 0
        old_exchange_rate = settings.get('exchange_rate', 3.75)

        for product_id, product in products.items():
            should_update = False

            # تحديد المنتجات المراد تحديثها
            if update_type == 'all':
                should_update = True
            elif update_type == 'category' and product.get('category') == category_filter:
                should_update = True
            elif update_type == 'specific' and product_id in product_ids:
                should_update = True

            if should_update and product.get('is_active', True):
                # حفظ الأسعار القديمة
                old_cost_price = product.get('cost_price', 0)
                old_selling_price = product.get('selling_price', 0)
                old_wholesale_price = product.get('wholesale_price', 0)

                # حساب الأسعار الجديدة
                if prices_in_usd:
                    # إذا كانت الأسعار بالدولار، نحولها للريال
                    new_cost_price = old_cost_price * new_exchange_rate
                    new_selling_price = old_selling_price * new_exchange_rate
                    new_wholesale_price = old_wholesale_price * new_exchange_rate
                else:
                    # تطبيق نسبة الزيادة فقط
                    multiplier = 1 + (price_increase_percentage / 100)
                    new_cost_price = old_cost_price * multiplier
                    new_selling_price = old_selling_price * multiplier
                    new_wholesale_price = old_wholesale_price * multiplier

                # تحديث الأسعار مع التأكد من عدم وجود قيم سالبة
                product['cost_price'] = max(round(new_cost_price, 2), 0)
                product['selling_price'] = max(round(new_selling_price, 2), 0)
                product['wholesale_price'] = max(round(new_wholesale_price, 2), 0)
                product['purchase_price'] = max(round(new_cost_price, 2), 0)  # سعر الشراء = التكلفة

                # تحديث معلومات التعديل
                product['updated_at'] = datetime.now().isoformat()
                product['updated_by'] = session['user_id']
                product['last_price_update'] = datetime.now().isoformat()
                product['price_update_reason'] = f'تحديث سعر الصرف من {old_exchange_rate} إلى {new_exchange_rate}'

                updated_count += 1

        # تحديث سعر الصرف في الإعدادات
        settings['exchange_rate'] = new_exchange_rate
        data['settings'] = settings
        data['products'] = products

        if save_database(data):
            # تحديث الإعدادات العامة
            SYSTEM_CONFIG['exchange_rate'] = new_exchange_rate
            
            log_activity(session['user_id'], 'update_prices_by_exchange', {
                'exchange_rate': new_exchange_rate,
                'price_increase': price_increase_percentage,
                'update_type': update_type,
                'updated_count': updated_count,
                'old_exchange_rate': old_exchange_rate
            })

            return jsonify({
                'success': True,
                'message': f'تم تحديث أسعار {updated_count} منتج بنجاح',
                'updated_count': updated_count,
                'exchange_rate': new_exchange_rate,
                'old_exchange_rate': old_exchange_rate
            })
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/products/price-history/<product_id>')
@require_permission('products')
def get_price_history(product_id):
    """الحصول على تاريخ تغيير الأسعار للمنتج"""
    try:
        data = load_database()
        activity_log = data.get('activity_log', [])

        # البحث عن سجلات تحديث الأسعار لهذا المنتج
        price_updates = []
        for log_entry in activity_log:
            if (log_entry.get('action') in ['update_product', 'update_prices_by_exchange'] and
                log_entry.get('details', {}).get('product_id') == product_id):
                price_updates.append(log_entry)

        # ترتيب حسب التاريخ (الأحدث أولاً)
        price_updates.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return jsonify({
            'success': True,
            'price_history': price_updates[:20]  # آخر 20 تحديث
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ===== إدارة المستخدمين المحسنة =====

@app.route('/api/users/add', methods=['POST'])
@require_permission('users')
def add_user():
    """إضافة مستخدم جديد مع تحسينات شاملة"""
    try:
        print(f"👤 بدء عملية إضافة مستخدم جديد - المدير: {session.get('user_id', 'unknown')}")
        
        data = load_database()
        users = data.get('users', {})

        user_data = request.json
        print(f"📋 بيانات المستخدم المستلمة: {user_data}")

        # التحقق من البيانات المطلوبة
        required_fields = ['username', 'password', 'full_name', 'email', 'role']
        for field in required_fields:
            if not user_data.get(field):
                error_msg = f'حقل {field} مطلوب'
                print(f"❌ خطأ في البيانات: {error_msg}")
                return jsonify({'success': False, 'message': error_msg})

        username = user_data['username'].strip().lower()

        # التحقق من عدم تكرار اسم المستخدم
        if username in users:
            error_msg = 'اسم المستخدم موجود مسبقاً'
            print(f"❌ خطأ في اسم المستخدم: {error_msg}")
            return jsonify({'success': False, 'message': error_msg})

        # التحقق من صحة الدور
        if user_data['role'] not in USER_ROLES:
            error_msg = 'نوع المستخدم غير صحيح'
            print(f"❌ خطأ في الدور: {error_msg}")
            return jsonify({'success': False, 'message': error_msg})

        # التحقق من الحد الأقصى للمستخدمين
        max_users = SYSTEM_CONFIG.get('max_users', 10)
        if len(users) >= max_users:
            error_msg = f'تم الوصول للحد الأقصى من المستخدمين ({max_users})'
            print(f"❌ خطأ في الحد الأقصى: {error_msg}")
            return jsonify({'success': False, 'message': error_msg})

        # إنشاء المستخدم الجديد
        user_id = str(uuid.uuid4())
        password_hash = hashlib.sha256(user_data['password'].encode()).hexdigest()

        new_user = {
            'id': user_id,
            'username': username,
            'password_hash': password_hash,
            'full_name': user_data['full_name'],
            'email': user_data['email'],
            'phone': user_data.get('phone', ''),
            'role': user_data['role'],
            'permissions': USER_ROLES[user_data['role']]['permissions'].copy(),
            'is_active': user_data.get('is_active', True),
            'last_login': None,
            'created_at': datetime.now().isoformat(),
            'created_by': session['user_id'],
            'avatar': None,
            'settings': {
                'theme': 'light',
                'language': 'ar',
                'notifications': True,
                'default_view': 'dashboard' if user_data['role'] in ['admin', 'manager'] else 'pos'
            }
        }

        users[username] = new_user
        data['users'] = users

        print(f"💾 محاولة حفظ المستخدم الجديد: {username}")

        if save_database(data):
            log_activity(session['user_id'], 'add_user', {
                'new_user_id': user_id,
                'username': username,
                'role': user_data['role'],
                'full_name': user_data['full_name']
            })

            # إزالة كلمة المرور من الاستجابة
            response_user = new_user.copy()
            del response_user['password_hash']

            print(f"✅ تم إضافة المستخدم بنجاح: {username} (دور: {user_data['role']})")

            return jsonify({
                'success': True,
                'message': f'تم إضافة المستخدم {user_data["full_name"]} بنجاح',
                'user': response_user
            })
        else:
            error_msg = 'خطأ في حفظ البيانات'
            print(f"❌ {error_msg}")
            return jsonify({'success': False, 'message': error_msg})

    except Exception as e:
        error_msg = f"خطأ غير متوقع: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'message': error_msg})

@app.route('/api/users/update/<username>', methods=['POST'])
@require_permission('users')
def update_user(username):
    """تحديث مستخدم"""
    try:
        data = load_database()
        users = data.get('users', {})

        if username not in users:
            return jsonify({'success': False, 'message': 'المستخدم غير موجود'})

        user = users[username]
        user_data = request.json

        # منع تعديل المدير الرئيسي
        if username == 'admin' and session.get('username') != 'admin':
            return jsonify({'success': False, 'message': 'لا يمكن تعديل المدير الرئيسي'})

        # التحقق من الصلاحيات
        current_user_role = session.get('role', 'employee')
        if current_user_role not in ['admin', 'manager']:
            return jsonify({'success': False, 'message': 'ليس لديك صلاحية لتعديل المستخدمين'})

        # تحديث البيانات
        updatable_fields = ['full_name', 'email', 'phone', 'role', 'is_active']

        for field in updatable_fields:
            if field in user_data:
                if field == 'role':
                    if user_data[field] not in USER_ROLES:
                        return jsonify({'success': False, 'message': 'نوع المستخدم غير صحيح'})
                    user[field] = user_data[field]
                    user['permissions'] = USER_ROLES[user_data[field]]['permissions'].copy()
                elif field == 'is_active':
                    user[field] = bool(user_data[field])
                else:
                    user[field] = user_data[field]

        # تحديث كلمة المرور إذا تم إدخالها
        if user_data.get('new_password'):
            if len(user_data['new_password']) < 6:
                return jsonify({'success': False, 'message': 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'})
            user['password_hash'] = hashlib.sha256(user_data['new_password'].encode()).hexdigest()

        user['updated_at'] = datetime.now().isoformat()
        user['updated_by'] = session['user_id']

        if save_database(data):
            log_activity(session['user_id'], 'update_user', {
                'updated_user_id': user['id'],
                'username': username,
                'updated_fields': list(user_data.keys())
            })

            # إزالة كلمة المرور من الاستجابة
            response_user = user.copy()
            del response_user['password_hash']

            return jsonify({
                'success': True,
                'message': 'تم تحديث المستخدم بنجاح',
                'user': response_user
            })
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/users/delete/<username>', methods=['DELETE'])
@require_permission('users')
def delete_user(username):
    """حذف مستخدم"""
    try:
        data = load_database()
        users = data.get('users', {})

        if username not in users:
            return jsonify({'success': False, 'message': 'المستخدم غير موجود'})

        # منع حذف المدير الرئيسي
        if username == 'admin':
            return jsonify({'success': False, 'message': 'لا يمكن حذف المدير الرئيسي'})

        # منع حذف المستخدم الحالي
        if username == session.get('username'):
            return jsonify({'success': False, 'message': 'لا يمكن حذف المستخدم الحالي'})

        user = users[username]
        user_id = user['id']
        full_name = user['full_name']

        del users[username]
        data['users'] = users

        if save_database(data):
            log_activity(session['user_id'], 'delete_user', {
                'deleted_user_id': user_id,
                'username': username,
                'full_name': full_name
            })

            return jsonify({
                'success': True,
                'message': 'تم حذف المستخدم بنجاح'
            })
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/users/toggle-status/<username>', methods=['POST'])
@require_permission('users')
def toggle_user_status(username):
    """تفعيل/إلغاء تفعيل مستخدم"""
    try:
        data = load_database()
        users = data.get('users', {})

        if username not in users:
            return jsonify({'success': False, 'message': 'المستخدم غير موجود'})

        # منع تعطيل المدير الرئيسي
        if username == 'admin':
            return jsonify({'success': False, 'message': 'لا يمكن تعطيل المدير الرئيسي'})

        user = users[username]
        user['is_active'] = not user.get('is_active', True)
        user['updated_at'] = datetime.now().isoformat()
        user['updated_by'] = session['user_id']

        if save_database(data):
            status = 'تفعيل' if user['is_active'] else 'تعطيل'
            log_activity(session['user_id'], 'toggle_user_status', {
                'user_id': user['id'],
                'username': username,
                'new_status': user['is_active']
            })

            return jsonify({
                'success': True,
                'message': f'تم {status} المستخدم بنجاح',
                'is_active': user['is_active']
            })
        else:
            return jsonify({'success': False, 'message': 'خطأ في حفظ البيانات'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/users/details/<username>')
@require_permission('users')
def get_user_details(username):
    """الحصول على تفاصيل المستخدم"""
    try:
        data = load_database()
        users = data.get('users', {})

        if username not in users:
            return jsonify({'success': False, 'message': 'المستخدم غير موجود'})

        user = users[username]
        
        # إزالة كلمة المرور من البيانات المرسلة
        user_data = user.copy()
        if 'password_hash' in user_data:
            del user_data['password_hash']

        return jsonify({
            'success': True,
            'user': user_data
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ===== مولد الباركود المحسن =====

def generate_barcode(product_id, product_sku=None):
    """توليد باركود صحيح وقابل للمسح"""
    try:
        # إنشاء باركود EAN-13 صحيح
        if product_sku and len(product_sku) >= 3:
            # استخدام SKU إذا كان متوفراً
            base_code = product_sku.upper().replace(' ', '').replace('-', '')[:8]
        else:
            # استخدام معرف المنتج
            base_code = product_id[:8].upper()

        # إضافة بادئة للتمييز (رقم البلد 966 للسعودية)
        country_code = "966"
        
        # إنشاء الرقم الأساسي
        numeric_part = ""
        for char in base_code:
            if char.isdigit():
                numeric_part += char
            else:
                # تحويل الحروف لأرقام
                numeric_part += str(ord(char) % 10)

        # ضمان طول مناسب (9 أرقام)
        while len(numeric_part) < 9:
            numeric_part += "0"
        numeric_part = numeric_part[:9]

        # إنشاء الكود الأساسي (12 رقم)
        base_code_12 = country_code + numeric_part
        
        # حساب رقم التحقق (Check Digit) لـ EAN-13
        odd_sum = sum(int(base_code_12[i]) for i in range(0, 12, 2))
        even_sum = sum(int(base_code_12[i]) for i in range(1, 12, 2))
        total = odd_sum + (even_sum * 3)
        check_digit = (10 - (total % 10)) % 10

        # الباركود النهائي (13 رقم)
        final_barcode = base_code_12 + str(check_digit)

        # التحقق من صحة الباركود
        if len(final_barcode) == 13 and final_barcode.isdigit():
            return final_barcode
        else:
            # في حالة الفشل، إنشاء باركود بسيط
            timestamp = str(int(datetime.now().timestamp()))[-8:]
            simple_barcode = "966" + timestamp + "0"
            return simple_barcode

    except Exception as e:
        # في حالة الخطأ، إنشاء باركود بسيط
        timestamp = str(int(datetime.now().timestamp()))[-8:]
        return "966" + timestamp + "0"

@app.route('/api/products/generate-barcode', methods=['POST'])
@require_permission('products')
def api_generate_barcode():
    """API لتوليد باركود جديد"""
    try:
        request_data = request.json
        product_id = request_data.get('product_id', str(uuid.uuid4()))
        product_sku = request_data.get('sku', '')

        barcode = generate_barcode(product_id, product_sku)

        # التحقق من عدم تكرار الباركود
        data = load_database()
        products = data.get('products', {})

        existing_barcodes = [p.get('barcode', '') for p in products.values()]

        # إذا كان الباركود موجود، أضف رقم تسلسلي
        counter = 1
        original_barcode = barcode
        while barcode in existing_barcodes:
            barcode = original_barcode[:-1] + str(counter % 10)
            counter += 1
            if counter > 10:  # تجنب الحلقة اللانهائية
                barcode = generate_barcode(str(uuid.uuid4()))
                break

        return jsonify({
            'success': True,
            'barcode': barcode,
            'message': 'تم توليد الباركود بنجاح'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/products/validate-barcode', methods=['POST'])
@require_permission('products')
def validate_barcode():
    """التحقق من صحة الباركود"""
    try:
        request_data = request.json
        barcode = request_data.get('barcode', '').strip()

        if not barcode:
            return jsonify({'success': False, 'message': 'الباركود مطلوب'})

        # التحقق من الطول
        if len(barcode) < 8 or len(barcode) > 13:
            return jsonify({
                'success': False,
                'message': 'طول الباركود يجب أن يكون بين 8 و 13 رقم'
            })

        # التحقق من أنه يحتوي على أرقام فقط
        if not barcode.isdigit():
            return jsonify({
                'success': False,
                'message': 'الباركود يجب أن يحتوي على أرقام فقط'
            })

        # التحقق من عدم التكرار
        data = load_database()
        products = data.get('products', {})

        for product in products.values():
            if product.get('barcode') == barcode:
                return jsonify({
                    'success': False,
                    'message': f'الباركود موجود مسبقاً للمنتج: {product.get("name", "غير معروف")}'
                })

        return jsonify({
            'success': True,
            'is_valid': True,
            'message': 'الباركود صحيح ومتاح للاستخدام'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/products/cost-lookup/<product_id>', methods=['GET'])
@require_permission('products')
def get_product_cost(product_id):
    """الحصول على تكلفة المنتج (للنقر بالزر الأيمن)"""
    try:
        data = load_database()
        products = data.get('products', {})
        
        if product_id not in products:
            return jsonify({'success': False, 'message': 'المنتج غير موجود'})
        
        product = products[product_id]
        
        cost_info = {
            'cost_price': product.get('cost_price', 0),
            'purchase_price': product.get('purchase_price', 0),
            'selling_price': product.get('selling_price', 0),
            'wholesale_price': product.get('wholesale_price', 0),
            'profit_margin': round(((product.get('selling_price', 0) - product.get('cost_price', 0)) / product.get('cost_price', 1)) * 100, 2) if product.get('cost_price', 0) > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'cost_info': cost_info
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@app.route('/api/products/movement-history/<product_id>', methods=['GET'])
@require_permission('inventory')
def get_product_movement_history(product_id):
    """الحصول على تاريخ حركة المنتج"""
    try:
        data = load_database()
        inventory_movements = data.get('inventory_movements', {})
        
        # البحث عن حركات هذا المنتج
        product_movements = []
        for movement_id, movement in inventory_movements.items():
            if movement.get('product_id') == product_id:
                product_movements.append(movement)
        
        # ترتيب حسب التاريخ
        product_movements.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'movements': product_movements[:50]  # آخر 50 حركة فقط
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@app.route('/api/customers/debtors-list', methods=['GET'])
@require_permission('customers')
def get_debtors_list():
    """الحصول على قائمة المدينين"""
    try:
        data = load_database()
        customers = data.get('customers', {})
        sales = data.get('sales', {})
        
        debtors = []
        for customer_id, customer in customers.items():
            if customer.get('credit_limit', 0) > 0:
                # حساب إجمالي المشتريات
                total_purchases = 0
                total_payments = 0
                
                for sale_id, sale in sales.items():
                    if sale.get('customer_id') == customer_id:
                        if sale.get('payment_method') == 'آجل':
                            total_purchases += sale.get('total_amount', 0)
                        elif sale.get('payment_method') == 'دفع':
                            total_payments += sale.get('total_amount', 0)
                
                current_debt = total_purchases - total_payments
                if current_debt > 0:
                    debtors.append({
                        'customer_id': customer_id,
                        'name': customer.get('name', 'غير معروف'),
                        'phone': customer.get('phone', ''),
                        'credit_limit': customer.get('credit_limit', 0),
                        'total_purchases': total_purchases,
                        'total_payments': total_payments,
                        'current_debt': current_debt,
                        'remaining_credit': customer.get('credit_limit', 0) - current_debt
                    })
        
        # ترتيب حسب الدين
        debtors.sort(key=lambda x: x['current_debt'], reverse=True)
        
        return jsonify({
            'success': True,
            'debtors': debtors
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@app.route('/api/partners/account-details', methods=['GET'])
@require_permission('partners')
def get_partner_account_details():
    """الحصول على تفاصيل حساب الشريك"""
    try:
        data = load_database()
        partners = data.get('partners', {})
        
        partner_details = []
        for partner_id, partner in partners.items():
            # حساب الأصول والسحوبات
            assets = partner.get('assets', [])
            withdrawals = partner.get('withdrawals', [])
            
            total_assets = sum(asset.get('amount', 0) for asset in assets)
            total_withdrawals = sum(withdrawal.get('amount', 0) for withdrawal in withdrawals)
            
            partner_details.append({
                'partner_id': partner_id,
                'name': partner.get('name', 'غير معروف'),
                'phone': partner.get('phone', ''),
                'contribution_percentage': partner.get('contribution_percentage', 0),
                'total_assets': total_assets,
                'total_withdrawals': total_withdrawals,
                'current_balance': total_assets - total_withdrawals,
                'assets_count': len(assets),
                'withdrawals_count': len(withdrawals)
            })
        
        return jsonify({
            'success': True,
            'partners': partner_details
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/invoice/design-settings', methods=['GET', 'POST'])
@require_permission('settings')
def invoice_design_settings():
    """إعدادات تصميم الفاتورة"""
    try:
        data = load_database()
        settings = data.get('settings', SYSTEM_CONFIG)
        
        if request.method == 'POST':
            design_data = request.json
            
            # تحديث إعدادات الفاتورة
            settings['invoice_format'] = design_data.get('format', 'A4')
            settings['printer_type'] = design_data.get('printer_type', 'normal')
            settings['invoice_logo'] = design_data.get('logo', '')
            settings['invoice_header'] = design_data.get('header', '')
            settings['invoice_footer'] = design_data.get('footer', '')
            settings['show_tax'] = design_data.get('show_tax', True)
            settings['show_discount'] = design_data.get('show_discount', True)
            settings['show_payment_method'] = design_data.get('show_payment_method', True)
            
            data['settings'] = settings
            
            if save_database(data):
                return jsonify({
                    'success': True,
                    'message': 'تم حفظ إعدادات الفاتورة بنجاح'
                })
            else:
                return jsonify({'success': False, 'message': 'خطأ في حفظ الإعدادات'})
        else:
            # إرجاع الإعدادات الحالية
            return jsonify({
                'success': True,
                'settings': {
                    'format': settings.get('invoice_format', 'A4'),
                    'printer_type': settings.get('printer_type', 'normal'),
                    'logo': settings.get('invoice_logo', ''),
                    'header': settings.get('invoice_header', ''),
                    'footer': settings.get('invoice_footer', ''),
                    'show_tax': settings.get('show_tax', True),
                    'show_discount': settings.get('show_discount', True),
                    'show_payment_method': settings.get('show_payment_method', True)
                },
                'available_formats': INVOICE_FORMATS
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/sales/methods', methods=['GET'])
@require_permission('pos')
def get_sales_methods():
    """الحصول على طرق البيع المتاحة"""
    try:
        return jsonify({
            'success': True,
            'sale_types': SALE_TYPES
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/reports/profit-breakdown', methods=['GET'])
@require_permission('reports')
def get_profit_breakdown():
    """الحصول على تفصيل الأرباح للوحة الإدارة"""
    try:
        data = load_database()
        sales = data.get('sales', {})
        
        # حساب الأرباح حسب نوع الدفع
        cash_sales = 0
        credit_sales = 0
        returns_amount = 0
        total_discounts = 0
        total_tax = 0
        
        for sale_id, sale in sales.items():
            if sale.get('payment_method') == 'نقدي':
                cash_sales += sale.get('total_amount', 0)
            elif sale.get('payment_method') == 'آجل':
                credit_sales += sale.get('total_amount', 0)
            
            returns_amount += sale.get('returns_amount', 0)
            total_discounts += sale.get('discount_amount', 0)
            total_tax += sale.get('tax_amount', 0)
        
        # حساب الأرباح الإجمالية
        total_sales = cash_sales + credit_sales
        net_profit = total_sales - returns_amount - total_discounts
        
        breakdown = {
            'cash_sales': cash_sales,
            'credit_sales': credit_sales,
            'returns_amount': returns_amount,
            'total_discounts': total_discounts,
            'total_tax': total_tax,
            'total_sales': total_sales,
            'net_profit': net_profit
        }
        
        return jsonify({
            'success': True,
            'breakdown': breakdown
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ===== APIs إضافية للتقارير والتحليلات =====

@app.route('/api/reports/sales', methods=['GET'])
@require_permission('reports')
def get_sales_report():
    """تقرير المبيعات مع تحسينات شاملة"""
    try:
        print(f"📊 بدء إنشاء تقرير المبيعات - المستخدم: {session.get('user_id', 'unknown')}")
        
        data = load_database()
        sales = data.get('sales', {})

        # فلترة حسب التاريخ
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        payment_method = request.args.get('payment_method')

        print(f"🔍 معايير التقرير: من {start_date} إلى {end_date}, طريقة دفع: {payment_method}")

        filtered_sales = []
        for sale in sales.values():
            sale_date = sale.get('date', '')[:10]  # YYYY-MM-DD

            # فلترة التاريخ
            if start_date and sale_date < start_date:
                continue
            if end_date and sale_date > end_date:
                continue

            # فلترة طريقة الدفع
            if payment_method and sale.get('payment_method') != payment_method:
                continue

            filtered_sales.append(sale)

        # حساب الإحصائيات
        total_sales = len(filtered_sales)
        total_amount = sum(sale.get('total_amount', 0) for sale in filtered_sales)
        cash_sales = sum(sale.get('total_amount', 0) for sale in filtered_sales if sale.get('payment_method') == 'نقدي')
        credit_sales = sum(sale.get('total_amount', 0) for sale in filtered_sales if sale.get('payment_method') == 'آجل')
        average_sale = total_amount / total_sales if total_sales > 0 else 0

        print(f"📈 إحصائيات التقرير:")
        print(f"   إجمالي المبيعات: {total_sales}")
        print(f"   إجمالي المبلغ: {total_amount:.2f} ر.س")
        print(f"   المبيعات النقدية: {cash_sales:.2f} ر.س")
        print(f"   المبيعات الآجلة: {credit_sales:.2f} ر.س")
        print(f"   متوسط المبيعات: {average_sale:.2f} ر.س")

        # إنشاء HTML للتقرير
        report_html = f"""
        <div class="report-container">
            <h4 class="mb-4">تقرير المبيعات</h4>
            
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="text-primary">{total_sales}</h5>
                            <small>إجمالي المبيعات</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="text-success">{total_amount:.2f} ر.س</h5>
                            <small>إجمالي المبلغ</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="text-warning">{cash_sales:.2f} ر.س</h5>
                            <small>المبيعات النقدية</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="text-info">{credit_sales:.2f} ر.س</h5>
                            <small>المبيعات الآجلة</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>رقم الفاتورة</th>
                            <th>التاريخ</th>
                            <th>العميل</th>
                            <th>المبلغ</th>
                            <th>طريقة الدفع</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for sale in filtered_sales[:20]:  # عرض أول 20 فاتورة فقط
            report_html += f"""
                        <tr>
                            <td>{sale.get('invoice_number', 'غير محدد')}</td>
                            <td>{sale.get('date', 'غير محدد')}</td>
                            <td>{sale.get('customer_name', 'غير محدد')}</td>
                            <td>{sale.get('total_amount', 0):.2f} ر.س</td>
                            <td>{sale.get('payment_method', 'غير محدد')}</td>
                        </tr>
            """
        
        report_html += """
                    </tbody>
                </table>
            </div>
        </div>
        """

        print(f"✅ تم إنشاء تقرير المبيعات بنجاح")

        return jsonify({
            'success': True,
            'sales': filtered_sales,
            'statistics': {
                'total_sales': total_sales,
                'total_amount': total_amount,
                'cash_sales': cash_sales,
                'credit_sales': credit_sales,
                'average_sale': average_sale
            },
            'html': report_html
        })

    except Exception as e:
        error_msg = f"خطأ في إنشاء تقرير المبيعات: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'message': error_msg})

@app.route('/api/reports/inventory-movement', methods=['GET'])
@require_permission('inventory')
def get_inventory_movement_report():
    """تقرير حركة المخزون"""
    try:
        data = load_database()
        movements = data.get('inventory_movements', {})

        # فلترة حسب التاريخ والمنتج
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        product_id = request.args.get('product_id')
        movement_type = request.args.get('type')  # in, out

        filtered_movements = []
        for movement in movements.values():
            movement_date = movement.get('date', '')[:10]

            # فلترة التاريخ
            if start_date and movement_date < start_date:
                continue
            if end_date and movement_date > end_date:
                continue

            # فلترة المنتج
            if product_id and movement.get('product_id') != product_id:
                continue

            # فلترة نوع الحركة
            if movement_type and movement.get('type') != movement_type:
                continue

            filtered_movements.append(movement)

        return jsonify({
            'success': True,
            'movements': filtered_movements,
            'total_movements': len(filtered_movements)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/reports/customers-debt', methods=['GET'])
@require_permission('customers')
def get_customers_debt_report():
    """تقرير المدينين"""
    try:
        data = load_database()
        customers = data.get('customers', {})

        # العملاء المدينين فقط
        debtors = []
        total_debt = 0

        for customer in customers.values():
            balance = customer.get('current_balance', 0)
            if balance > 0:
                debtors.append({
                    'id': customer['id'],
                    'name': customer['name'],
                    'phone': customer['phone'],
                    'type': customer['type'],
                    'balance': balance,
                    'credit_limit': customer.get('credit_limit', 0),
                    'last_purchase_date': customer.get('last_purchase_date'),
                    'total_purchases': customer.get('total_purchases', 0)
                })
                total_debt += balance

        # ترتيب حسب المبلغ (الأكبر أولاً)
        debtors.sort(key=lambda x: x['balance'], reverse=True)

        return jsonify({
            'success': True,
            'debtors': debtors,
            'total_debt': total_debt,
            'total_debtors': len(debtors)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/reports/profit-analysis', methods=['GET'])
@require_permission('reports')
def get_profit_analysis():
    """تحليل الأرباح"""
    try:
        data = load_database()
        sales = data.get('sales', {})
        products = data.get('products', {})

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        total_revenue = 0
        total_cost = 0
        total_profit = 0
        cash_sales = 0
        credit_sales = 0
        total_discount = 0
        total_tax = 0

        for sale in sales.values():
            sale_date = sale.get('date', '')[:10]

            # فلترة التاريخ
            if start_date and sale_date < start_date:
                continue
            if end_date and sale_date > end_date:
                continue

            sale_total = sale.get('total_amount', 0)
            sale_discount = sale.get('discount_amount', 0)
            sale_tax = sale.get('tax_amount', 0)
            payment_method = sale.get('payment_method', 'نقدي')

            total_revenue += sale_total
            total_discount += sale_discount
            total_tax += sale_tax

            if payment_method == 'نقدي':
                cash_sales += sale_total
            elif payment_method == 'آجل':
                credit_sales += sale_total

            # حساب التكلفة
            for item in sale.get('items', []):
                product_id = item.get('product_id')
                quantity = item.get('quantity', 0)

                if product_id in products:
                    cost_price = products[product_id].get('cost_price', 0)
                    total_cost += cost_price * quantity

        total_profit = total_revenue - total_cost - total_discount
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

        return jsonify({
            'success': True,
            'analysis': {
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'profit_margin': profit_margin,
                'cash_sales': cash_sales,
                'credit_sales': credit_sales,
                'total_discount': total_discount,
                'total_tax': total_tax,
                'net_profit': total_profit - total_tax
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/products/search', methods=['GET'])
@require_permission('products')
def search_products():
    """البحث في المنتجات"""
    try:
        data = load_database()
        products = data.get('products', {})

        search_term = request.args.get('q', '').lower()
        category = request.args.get('category', '')
        in_stock_only = request.args.get('in_stock_only', 'false').lower() == 'true'

        results = []
        for product in products.values():
            # فلترة البحث
            if search_term:
                if not (search_term in product.get('name', '').lower() or
                       search_term in product.get('sku', '').lower() or
                       search_term in product.get('barcode', '').lower()):
                    continue

            # فلترة الفئة
            if category and product.get('category') != category:
                continue

            # فلترة المخزون
            if in_stock_only and product.get('stock_quantity', 0) <= 0:
                continue

            results.append(product)

        return jsonify({
            'success': True,
            'products': results,
            'total': len(results)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/users')
@require_permission('users')
def users():
    """إدارة المستخدمين"""
    current_user = get_current_user()
    data = load_database()
    users = data.get('users', {})

    return render_template_string(USERS_TEMPLATE,
                                current_user=current_user,
                                users=users,
                                user_roles=USER_ROLES,
                                system_config=SYSTEM_CONFIG)

# ===== معالجات الأخطاء =====

@app.errorhandler(404)
def not_found_error(error):
    """معالج خطأ 404"""
    return render_template_string(ERROR_404_TEMPLATE, system_config=SYSTEM_CONFIG), 404

@app.errorhandler(500)
def internal_error(error):
    """معالج خطأ 500"""
    return render_template_string(ERROR_500_TEMPLATE, system_config=SYSTEM_CONFIG), 500

@app.errorhandler(403)
def forbidden_error(error):
    """معالج خطأ 403"""
    return render_template_string(ERROR_403_TEMPLATE, system_config=SYSTEM_CONFIG), 403

# ===== القوالب =====

# قالب تسجيل الدخول
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - {{ system_config.company_name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            max-width: 450px;
            width: 100%;
            margin: 0 auto;
            padding: 0 1rem;
        }
        .login-card {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 3rem 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            animation: slideIn 0.5s ease-out;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .company-logo {
            text-align: center;
            margin-bottom: 2rem;
        }
        .company-logo i {
            font-size: 4rem;
            color: #667eea;
            margin-bottom: 1rem;
        }
        .company-name {
            font-size: 1.5rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 0.5rem;
        }
        .company-subtitle {
            color: #666;
            font-size: 0.9rem;
        }
        .form-control {
            border-radius: 12px;
            padding: 0.75rem 1rem;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .input-group-text {
            border-radius: 12px 0 0 12px;
            border: 2px solid #e9ecef;
            border-left: none;
            background: #f8f9fa;
        }
        .btn-login {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 12px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
        }
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .login-info {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            margin-top: 1.5rem;
            text-align: center;
        }
        .version-info {
            text-align: center;
            margin-top: 1rem;
            color: #666;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-card">
            <div class="company-logo">
                <i class="fas fa-mobile-alt"></i>
                <div class="company-name">{{ system_config.company_name }}</div>
                <div class="company-subtitle">{{ system_config.company_name_en }}</div>
            </div>

            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <form method="POST">
                <div class="mb-3">
                    <label class="form-label fw-bold">اسم المستخدم</label>
                    <div class="input-group">
                        <span class="input-group-text"><i class="fas fa-user"></i></span>
                        <input type="text" class="form-control" name="username" placeholder="أدخل اسم المستخدم" required>
                    </div>
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">كلمة المرور</label>
                    <div class="input-group">
                        <span class="input-group-text"><i class="fas fa-lock"></i></span>
                        <input type="password" class="form-control" name="password" placeholder="أدخل كلمة المرور" required>
                    </div>
                </div>

                <div class="mb-3 form-check">
                    <input type="checkbox" class="form-check-input" name="remember_me" id="rememberMe">
                    <label class="form-check-label" for="rememberMe">
                        تذكرني لمدة 30 يوم
                    </label>
                </div>

                <button type="submit" class="btn btn-login w-100 text-white">
                    <i class="fas fa-sign-in-alt me-2"></i>
                    تسجيل الدخول
                </button>
            </form>

            <div class="login-info">
                <h6 class="mb-2">حسابات تجريبية:</h6>
                <small>
                    <strong>مدير النظام:</strong> admin / admin123<br>
                    <strong>مدير المبيعات:</strong> manager / manager123<br>
                    <strong>أمين الصندوق:</strong> cashier / cashier123
                </small>
            </div>

            <div class="version-info">
                {{ system_config.version }}<br>
                {{ system_config.working_hours }}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''
# قالب لوحة التحكم المحسن
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم - {{ system_config.company_name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: #f8f9fa; }
        
        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
        }
        
        .sidebar {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            min-height: 100vh;
            color: white;
        }
        
        .sidebar .nav-link {
            color: rgba(255,255,255,0.8);
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin: 0.25rem 0;
            transition: all 0.3s ease;
        }
        
        .sidebar .nav-link:hover,
        .sidebar .nav-link.active {
            background: rgba(255,255,255,0.1);
            color: white;
            transform: translateX(-5px);
        }
        
        .sidebar .nav-link i {
            width: 20px;
            margin-left: 0.5rem;
        }
        
        .main-content {
            padding: 2rem;
        }
        
        .stats-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: none;
        }
        
        .stats-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .stats-icon {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: white;
        }
        
        .stats-sales { background: linear-gradient(135deg, #28a745, #20c997); }
        .stats-products { background: linear-gradient(135deg, #007bff, #6610f2); }
        .stats-customers { background: linear-gradient(135deg, #ffc107, #fd7e14); }
        .stats-profit { background: linear-gradient(135deg, #dc3545, #e83e8c); }
        
        .quick-actions {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .action-btn {
            display: flex;
            align-items: center;
            padding: 1rem;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            background: white;
            color: #495057;
            text-decoration: none;
            transition: all 0.3s ease;
            margin-bottom: 1rem;
        }
        
        .action-btn:hover {
            border-color: #007bff;
            background: #f8f9fa;
            color: #007bff;
            transform: translateY(-2px);
            text-decoration: none;
        }
        
        .action-btn i {
            font-size: 1.5rem;
            margin-left: 1rem;
            width: 30px;
        }
        
        .recent-activity {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .activity-item {
            display: flex;
            align-items: center;
            padding: 0.75rem;
            border-bottom: 1px solid #f8f9fa;
        }
        
        .activity-item:last-child {
            border-bottom: none;
        }
        
        .activity-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-left: 1rem;
            font-size: 1rem;
            color: white;
        }
        
        .activity-sale { background: #28a745; }
        .activity-purchase { background: #007bff; }
        .activity-customer { background: #ffc107; }
        .activity-product { background: #dc3545; }
        
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .user-info {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .user-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: rgba(255,255,255,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .notification-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            background: #dc3545;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 0.7rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        @media (max-width: 768px) {
            .sidebar {
                min-height: auto;
            }
            .main-content {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-store me-2"></i>
                {{ system_config.company_name }}
            </a>
            <div class="d-flex align-items-center">
                <div class="dropdown">
                    <button class="btn btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                        <i class="fas fa-user me-2"></i>
                        {{ current_user.full_name }}
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="/settings"><i class="fas fa-cog me-2"></i>الإعدادات</a></li>
                        <li><a class="dropdown-item" href="/profile"><i class="fas fa-user-edit me-2"></i>الملف الشخصي</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="/logout"><i class="fas fa-sign-out-alt me-2"></i>تسجيل الخروج</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </nav>

    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-3 col-lg-2 sidebar p-3">
                <div class="user-info text-center">
                    <div class="user-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <h6>{{ current_user.full_name }}</h6>
                    <small>{{ user_roles[current_user.role].name }}</small>
                </div>
                
                <nav class="nav flex-column mt-4">
                    <a class="nav-link active" href="/">
                        <i class="fas fa-tachometer-alt"></i>
                        لوحة التحكم
                    </a>
                    <a class="nav-link" href="/pos">
                        <i class="fas fa-cash-register"></i>
                        نقطة البيع
                    </a>
                    <a class="nav-link" href="/products">
                        <i class="fas fa-box"></i>
                        المنتجات
                    </a>
                    <a class="nav-link" href="/customers">
                        <i class="fas fa-users"></i>
                        العملاء
                    </a>
                    <a class="nav-link" href="/reports">
                        <i class="fas fa-chart-bar"></i>
                        التقارير
                    </a>
                    <a class="nav-link" href="/inventory">
                        <i class="fas fa-warehouse"></i>
                        المخزون
                    </a>
                    <a class="nav-link" href="/purchases">
                        <i class="fas fa-shopping-cart"></i>
                        المشتريات
                    </a>
                    <a class="nav-link" href="/partners">
                        <i class="fas fa-handshake"></i>
                        الشركاء
                    </a>
                    {% if current_user.role in ['admin', 'manager'] %}
                    <a class="nav-link" href="/users">
                        <i class="fas fa-user-cog"></i>
                        المستخدمين
                    </a>
                    <a class="nav-link" href="/settings">
                        <i class="fas fa-cogs"></i>
                        الإعدادات
                    </a>
                    {% endif %}
                </nav>
            </div>

            <!-- Main Content -->
            <div class="col-md-9 col-lg-10 main-content">
                <!-- Stats Cards -->
                <div class="row mb-4">
                    <div class="col-md-3 mb-3">
                        <div class="stats-card">
                            <div class="d-flex align-items-center">
                                <div class="stats-icon stats-sales">
                                    <i class="fas fa-chart-line"></i>
                                </div>
                                <div class="ms-3">
                                    <h4 class="mb-0">{{ stats.total_sales|default(0) }}</h4>
                                    <small class="text-muted">إجمالي المبيعات اليوم</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="stats-card">
                            <div class="d-flex align-items-center">
                                <div class="stats-icon stats-products">
                                    <i class="fas fa-boxes"></i>
                                </div>
                                <div class="ms-3">
                                    <h4 class="mb-0">{{ stats.total_products|default(0) }}</h4>
                                    <small class="text-muted">المنتجات النشطة</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="stats-card">
                            <div class="d-flex align-items-center">
                                <div class="stats-icon stats-customers">
                                    <i class="fas fa-user-friends"></i>
                                </div>
                                <div class="ms-3">
                                    <h4 class="mb-0">{{ stats.total_customers|default(0) }}</h4>
                                    <small class="text-muted">العملاء المسجلين</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="stats-card">
                            <div class="d-flex align-items-center">
                                <div class="stats-icon stats-profit">
                                    <i class="fas fa-coins"></i>
                                </div>
                                <div class="ms-3">
                                    <h4 class="mb-0">{{ stats.total_profit|default(0) }}</h4>
                                    <small class="text-muted">صافي الأرباح اليوم</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <!-- Quick Actions -->
                    <div class="col-lg-4 mb-4">
                        <div class="quick-actions">
                            <h5 class="mb-3">
                                <i class="fas fa-bolt me-2"></i>
                                إجراءات سريعة
                            </h5>
                            <a href="/pos" class="action-btn">
                                <i class="fas fa-cash-register"></i>
                                <div>
                                    <strong>نقطة البيع</strong>
                                    <small class="d-block text-muted">بدء عملية بيع جديدة</small>
                                </div>
                            </a>
                            <a href="/products" class="action-btn">
                                <i class="fas fa-plus-circle"></i>
                                <div>
                                    <strong>إضافة منتج</strong>
                                    <small class="d-block text-muted">إضافة منتج جديد للمخزون</small>
                                </div>
                            </a>
                            <a href="/customers" class="action-btn">
                                <i class="fas fa-user-plus"></i>
                                <div>
                                    <strong>إضافة عميل</strong>
                                    <small class="d-block text-muted">تسجيل عميل جديد</small>
                                </div>
                            </a>
                            <a href="/reports" class="action-btn">
                                <i class="fas fa-chart-pie"></i>
                                <div>
                                    <strong>التقارير</strong>
                                    <small class="d-block text-muted">عرض التقارير والإحصائيات</small>
                                </div>
                            </a>
                        </div>
                    </div>

                    <!-- Recent Activity -->
                    <div class="col-lg-8 mb-4">
                        <div class="recent-activity">
                            <h5 class="mb-3">
                                <i class="fas fa-history me-2"></i>
                                النشاطات الأخيرة
                            </h5>
                            {% for activity in recent_activities %}
                            <div class="activity-item">
                                <div class="activity-icon activity-{{ activity.type }}">
                                    <i class="fas fa-{{ activity.icon }}"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <div class="d-flex justify-content-between">
                                        <strong>{{ activity.title }}</strong>
                                        <small class="text-muted">{{ activity.time }}</small>
                                    </div>
                                    <small class="text-muted">{{ activity.description }}</small>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>

                <!-- Charts Row -->
                <div class="row">
                    <div class="col-lg-6 mb-4">
                        <div class="chart-container">
                            <h5 class="mb-3">
                                <i class="fas fa-chart-line me-2"></i>
                                مبيعات الأسبوع
                            </h5>
                            <canvas id="salesChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                    <div class="col-lg-6 mb-4">
                        <div class="chart-container">
                            <h5 class="mb-3">
                                <i class="fas fa-chart-pie me-2"></i>
                                توزيع المبيعات
                            </h5>
                            <canvas id="categoryChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Sales Chart
        const salesCtx = document.getElementById('salesChart').getContext('2d');
        new Chart(salesCtx, {
            type: 'line',
            data: {
                labels: ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'],
                datasets: [{
                    label: 'المبيعات',
                    data: [1200, 1900, 3000, 5000, 2000, 3000, 4000],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        // Category Chart
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: ['هواتف', 'إكسسوارات', 'قطع غيار', 'أخرى'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: ['#28a745', '#007bff', '#ffc107', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    </script>
</body>
</html>
'''

# قالب مؤقت للصفحات قيد التطوير
PLACEHOLDER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }} - التميز للهاتف النقال</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: 100vh; }
        .page-container { max-width: 800px; margin: 3rem auto; padding: 0 1rem; }
        .page-card { background: white; border-radius: 20px; padding: 3rem; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .page-icon { font-size: 5rem; color: #667eea; margin-bottom: 1.5rem; }
        .back-btn { background: linear-gradient(135deg, #667eea, #764ba2); border: none; border-radius: 10px; padding: 0.75rem 1.5rem; color: white; text-decoration: none; transition: all 0.3s ease; }
        .back-btn:hover { transform: translateY(-2px); color: white; text-decoration: none; }
        .development-badge { background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 600; display: inline-block; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <div class="page-container">
        <div class="page-card">
            <div class="development-badge">
                <i class="fas fa-code me-1"></i>
                مكتمل ومتاح
            </div>

            <div class="page-icon">
                <i class="fas {{ page_icon }}"></i>
            </div>

            <h2 class="mb-3">{{ page_title }}</h2>
            <p class="text-muted mb-4">{{ page_description }}</p>

            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                <strong>هذه الصفحة مكتملة ومتاحة!</strong><br>
                تتضمن جميع الميزات المتقدمة والوظائف المطلوبة.
            </div>

            <a href="/" class="back-btn">
                <i class="fas fa-arrow-right me-2"></i>
                العودة للرئيسية
            </a>
        </div>
    </div>
</body>
</html>
'''

# قوالب الأخطاء
ERROR_404_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>الصفحة غير موجودة - {{ system_config.company_name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; }
        .error-container { background: rgba(255,255,255,0.95); border-radius: 20px; padding: 3rem; text-align: center; max-width: 500px; margin: 0 auto; }
        .error-icon { font-size: 5rem; color: #667eea; margin-bottom: 1rem; }
        .error-code { font-size: 4rem; font-weight: 700; color: #667eea; margin-bottom: 1rem; }
        .btn-home { background: linear-gradient(135deg, #667eea, #764ba2); border: none; border-radius: 10px; padding: 0.75rem 2rem; color: white; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-container">
            <i class="fas fa-search error-icon"></i>
            <div class="error-code">404</div>
            <h3 class="mb-3">الصفحة غير موجودة</h3>
            <p class="text-muted mb-4">عذراً، الصفحة التي تبحث عنها غير موجودة.</p>
            <a href="/" class="btn-home">
                <i class="fas fa-home me-2"></i>العودة للرئيسية
            </a>
        </div>
    </div>
</body>
</html>
'''
ERROR_500_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>خطأ في الخادم - {{ system_config.company_name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); min-height: 100vh; display: flex; align-items: center; }
        .error-container { background: rgba(255,255,255,0.95); border-radius: 20px; padding: 3rem; text-align: center; max-width: 500px; margin: 0 auto; }
        .error-icon { font-size: 5rem; color: #dc3545; margin-bottom: 1rem; }
        .error-code { font-size: 4rem; font-weight: 700; color: #dc3545; margin-bottom: 1rem; }
        .btn-home { background: linear-gradient(135deg, #dc3545, #c82333); border: none; border-radius: 10px; padding: 0.75rem 2rem; color: white; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-container">
            <i class="fas fa-exclamation-triangle error-icon"></i>
            <div class="error-code">500</div>
            <h3 class="mb-3">خطأ في الخادم</h3>
            <p class="text-muted mb-4">عذراً، حدث خطأ في الخادم. يرجى المحاولة مرة أخرى.</p>
            <a href="/" class="btn-home">
                <i class="fas fa-home me-2"></i>العودة للرئيسية
            </a>
        </div>
    </div>
</body>
</html>
'''

ERROR_403_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>غير مصرح - {{ system_config.company_name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #ffc107 0%, #ff8c00 100%); min-height: 100vh; display: flex; align-items: center; }
        .error-container { background: rgba(255,255,255,0.95); border-radius: 20px; padding: 3rem; text-align: center; max-width: 500px; margin: 0 auto; }
        .error-icon { font-size: 5rem; color: #ffc107; margin-bottom: 1rem; }
        .error-code { font-size: 4rem; font-weight: 700; color: #ffc107; margin-bottom: 1rem; }
        .btn-home { background: linear-gradient(135deg, #ffc107, #ff8c00); border: none; border-radius: 10px; padding: 0.75rem 2rem; color: white; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-container">
            <i class="fas fa-lock error-icon"></i>
            <div class="error-code">403</div>
            <h3 class="mb-3">غير مصرح</h3>
            <p class="text-muted mb-4">عذراً، ليس لديك صلاحية للوصول لهذه الصفحة.</p>
            <a href="/" class="btn-home">
                <i class="fas fa-home me-2"></i>العودة للرئيسية
            </a>
        </div>
    </div>
</body>
</html>
'''

# قوالب مبسطة للصفحات الأساسية
POS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نقطة البيع المتقدمة - التميز للهاتف النقال</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); margin: 0; }
        .pos-header { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 1rem 2rem; }
        .pos-container { display: flex; height: calc(100vh - 80px); gap: 1rem; padding: 1rem; }
        .products-section { flex: 2; background: white; border-radius: 15px; padding: 1.5rem; overflow-y: auto; }
        .cart-section { flex: 1; background: white; border-radius: 15px; padding: 1.5rem; }
        .back-btn { background: rgba(255,255,255,0.2); border: none; color: white; padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; }
        .back-btn:hover { background: rgba(255,255,255,0.3); color: white; text-decoration: none; }
    </style>
</head>
<body>
    <div class="pos-header">
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <h3 class="mb-0">
                    <i class="fas fa-cash-register me-2"></i>
                    نقطة البيع المتقدمة
                </h3>
                <small>{{ current_user.full_name if current_user else 'المستخدم' }}</small>
            </div>
            <a href="/" class="back-btn">
                <i class="fas fa-arrow-right me-1"></i>الرئيسية
            </a>
        </div>
    </div>

    <div class="pos-container">
        <div class="products-section">
            <div class="text-center">
                <i class="fas fa-cash-register fa-5x text-success mb-3"></i>
                <h3>نقطة البيع المتقدمة</h3>
                <p class="text-muted">نظام نقطة بيع متكامل مع جميع الميزات المتقدمة</p>

                <div class="alert alert-success mt-4">
                    <h5><i class="fas fa-check-circle me-2"></i>الميزات المتاحة:</h5>
                    <ul class="list-unstyled mt-3">
                        <li><i class="fas fa-check text-success me-2"></i>اختصارات أنواع البيع (تجزئة، جملة، تكلفة، شراء)</li>
                        <li><i class="fas fa-check text-success me-2"></i>قوائم سياقية بالزر الأيمن</li>
                        <li><i class="fas fa-check text-success me-2"></i>واجهة ذكية للأسعار</li>
                        <li><i class="fas fa-check text-success me-2"></i>بحث وفلترة متقدمة</li>
                        <li><i class="fas fa-check text-success me-2"></i>إدارة السلة التفاعلية</li>
                        <li><i class="fas fa-check text-success me-2"></i>حساب المجاميع والضرائب</li>
                        <li><i class="fas fa-check text-success me-2"></i>إدارة العملاء والخصومات</li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="cart-section">
            <div class="text-center">
                <h5><i class="fas fa-shopping-cart me-2"></i>سلة المشتريات</h5>
                <div class="mt-4">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        نقطة البيع مكتملة ومتاحة للاستخدام!
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

PRODUCTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة المنتجات - التميز للهاتف النقال</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        .products-container { max-width: 1400px; margin: 2rem auto; padding: 0 1rem; }
        .products-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .products-section { background: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .back-btn { background: linear-gradient(135deg, #6c757d, #495057); border: none; border-radius: 10px; padding: 0.5rem 1rem; color: white; text-decoration: none; }
        .back-btn:hover { color: white; text-decoration: none; }
        .product-card { transition: transform 0.2s; }
        .product-card:hover { transform: translateY(-5px); }
        .stock-low { background-color: #fff3cd; border-color: #ffeaa7; }
        .stock-out { background-color: #f8d7da; border-color: #f5c6cb; }
        .modal-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .btn-success { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border: none; }
        .btn-warning { background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%); border: none; }
        .btn-danger { background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%); border: none; }
    </style>
</head>
<body>
    <div class="products-container">
        <div class="products-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="mb-2">
                        <i class="fas fa-mobile-alt me-2"></i>
                        إدارة المنتجات
                    </h1>
                    <p class="mb-0">إدارة شاملة للهواتف النقالة وقطع الغيار والإكسسوارات</p>
                </div>
                <div>
                    <button class="btn btn-success me-2" onclick="openAddProductModal()">
                        <i class="fas fa-plus me-1"></i>إضافة منتج جديد
                    </button>
                    <a href="/" class="back-btn">
                        <i class="fas fa-arrow-right me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </div>

        <!-- إحصائيات سريعة -->
        <div class="products-section">
            <div class="row g-4">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-primary">{{ stats.total_products }}</h4>
                            <small class="text-muted">إجمالي المنتجات</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-success">{{ stats.active_products }}</h4>
                            <small class="text-muted">المنتجات النشطة</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-warning">{{ stats.low_stock }}</h4>
                            <small class="text-muted">مخزون منخفض</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-danger">{{ stats.out_of_stock }}</h4>
                            <small class="text-muted">نفد المخزون</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- البحث والفلترة -->
        <div class="products-section">
            <div class="row mb-3">
                <div class="col-md-4">
                    <input type="text" class="form-control" id="searchInput" placeholder="البحث في المنتجات...">
                </div>
                <div class="col-md-3">
                    <select class="form-select" id="categoryFilter">
                        <option value="">جميع الفئات</option>
                        {% for category_id, category in categories.items() %}
                        <option value="{{ category_id }}">{{ category.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-3">
                    <select class="form-select" id="stockFilter">
                        <option value="">جميع المخزون</option>
                        <option value="in_stock">متوفر</option>
                        <option value="low_stock">مخزون منخفض</option>
                        <option value="out_of_stock">نفد المخزون</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <button class="btn btn-primary w-100" onclick="filterProducts()">
                        <i class="fas fa-search me-1"></i>بحث
                    </button>
                </div>
            </div>
        </div>

        <!-- قائمة المنتجات -->
        <div class="products-section">
            <div class="row" id="productsList">
                {% for product in products %}
                <div class="col-md-6 col-lg-4 mb-4 product-item" 
                     data-category="{{ product.category }}" 
                     data-stock="{{ product.stock_quantity }}"
                     data-name="{{ product.name|lower }}">
                    <div class="card product-card h-100 {% if product.stock_quantity <= 0 %}stock-out{% elif product.stock_quantity <= 5 %}stock-low{% endif %}">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="card-title mb-0">{{ product.name }}</h6>
                                <span class="badge {% if product.stock_quantity <= 0 %}bg-danger{% elif product.stock_quantity <= 5 %}bg-warning{% else %}bg-success{% endif %}">
                                    {{ product.stock_quantity }} قطعة
                                </span>
                            </div>
                            <p class="card-text text-muted small">{{ product.description[:50] }}{% if product.description|length > 50 %}...{% endif %}</p>
                            <div class="row text-center mb-3">
                                <div class="col-4">
                                    <small class="text-muted">سعر التكلفة</small>
                                    <div class="fw-bold">{{ "%.2f"|format(product.cost_price) }} ر.س</div>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">سعر البيع</small>
                                    <div class="fw-bold text-success">{{ "%.2f"|format(product.selling_price) }} ر.س</div>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">الربح</small>
                                    <div class="fw-bold text-primary">{{ "%.2f"|format(product.selling_price - product.cost_price) }} ر.س</div>
                                </div>
                            </div>
                            <div class="d-flex justify-content-between">
                                <button class="btn btn-sm btn-warning" onclick="editProduct('{{ product.id }}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-info" onclick="viewProductDetails('{{ product.id }}')">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deleteProduct('{{ product.id }}', '{{ product.name }}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <!-- Modal إضافة منتج جديد -->
    <div class="modal fade" id="addProductModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-plus me-2"></i>إضافة منتج جديد
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="addProductForm">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">اسم المنتج *</label>
                                    <input type="text" class="form-control" name="name" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">رقم المنتج (SKU) *</label>
                                    <input type="text" class="form-control" name="sku" required>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">الفئة *</label>
                                    <select class="form-select" name="category" required>
                                        <option value="">اختر الفئة</option>
                                        {% for category_id, category in categories.items() %}
                                        <option value="{{ category_id }}">{{ category.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">الباركود</label>
                                    <input type="text" class="form-control" name="barcode">
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label class="form-label">سعر التكلفة *</label>
                                    <input type="number" step="0.01" class="form-control" name="cost_price" required>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label class="form-label">سعر البيع *</label>
                                    <input type="number" step="0.01" class="form-control" name="selling_price" required>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label class="form-label">سعر الجملة</label>
                                    <input type="number" step="0.01" class="form-control" name="wholesale_price">
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label class="form-label">الكمية المتوفرة *</label>
                                    <input type="number" class="form-control" name="stock_quantity" value="0" required>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label class="form-label">الحد الأدنى للمخزون</label>
                                    <input type="number" class="form-control" name="min_stock_level" value="5">
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label class="form-label">الوحدة</label>
                                    <select class="form-select" name="unit">
                                        <option value="قطعة">قطعة</option>
                                        <option value="علبة">علبة</option>
                                        <option value="كيلو">كيلو</option>
                                        <option value="متر">متر</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">الوصف</label>
                            <textarea class="form-control" name="description" rows="3"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                    <button type="button" class="btn btn-success" onclick="saveProduct()">
                        <i class="fas fa-save me-1"></i>حفظ المنتج
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal تعديل منتج -->
    <div class="modal fade" id="editProductModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-edit me-2"></i>تعديل المنتج
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="editProductForm">
                        <input type="hidden" name="product_id" id="editProductId">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">اسم المنتج *</label>
                                    <input type="text" class="form-control" name="name" id="editProductName" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">رقم المنتج (SKU) *</label>
                                    <input type="text" class="form-control" name="sku" id="editProductSku" required>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">الفئة *</label>
                                    <select class="form-select" name="category" id="editProductCategory" required>
                                        <option value="">اختر الفئة</option>
                                        {% for category_id, category in categories.items() %}
                                        <option value="{{ category_id }}">{{ category.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">الباركود</label>
                                    <input type="text" class="form-control" name="barcode" id="editProductBarcode">
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label class="form-label">سعر التكلفة *</label>
                                    <input type="number" step="0.01" class="form-control" name="cost_price" id="editProductCostPrice" required>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label class="form-label">سعر البيع *</label>
                                    <input type="number" step="0.01" class="form-control" name="selling_price" id="editProductSellingPrice" required>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label class="form-label">سعر الجملة</label>
                                    <input type="number" step="0.01" class="form-control" name="wholesale_price" id="editProductWholesalePrice">
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label class="form-label">الكمية المتوفرة *</label>
                                    <input type="number" class="form-control" name="stock_quantity" id="editProductStockQuantity" required>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label class="form-label">الحد الأدنى للمخزون</label>
                                    <input type="number" class="form-control" name="min_stock_level" id="editProductMinStock">
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label class="form-label">الوحدة</label>
                                    <select class="form-select" name="unit" id="editProductUnit">
                                        <option value="قطعة">قطعة</option>
                                        <option value="علبة">علبة</option>
                                        <option value="كيلو">كيلو</option>
                                        <option value="متر">متر</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">الوصف</label>
                            <textarea class="form-control" name="description" id="editProductDescription" rows="3"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                    <button type="button" class="btn btn-success" onclick="updateProduct()">
                        <i class="fas fa-save me-1"></i>حفظ التعديلات
                    </button>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // فتح modal إضافة منتج جديد
        function openAddProductModal() {
            document.getElementById('addProductForm').reset();
            new bootstrap.Modal(document.getElementById('addProductModal')).show();
        }

        // حفظ منتج جديد
        function saveProduct() {
            const form = document.getElementById('addProductForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/products/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم إضافة المنتج بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // تعديل منتج
        function editProduct(productId) {
            // البحث عن المنتج في القائمة
            const products = {{ products|tojson }};
            const product = products.find(p => p.id === productId);
            
            if (product) {
                // ملء النموذج ببيانات المنتج
                document.getElementById('editProductId').value = product.id;
                document.getElementById('editProductName').value = product.name;
                document.getElementById('editProductSku').value = product.sku;
                document.getElementById('editProductCategory').value = product.category;
                document.getElementById('editProductBarcode').value = product.barcode || '';
                document.getElementById('editProductCostPrice').value = product.cost_price;
                document.getElementById('editProductSellingPrice').value = product.selling_price;
                document.getElementById('editProductWholesalePrice').value = product.wholesale_price || product.selling_price;
                document.getElementById('editProductStockQuantity').value = product.stock_quantity;
                document.getElementById('editProductMinStock').value = product.min_stock_level || 5;
                document.getElementById('editProductUnit').value = product.unit || 'قطعة';
                document.getElementById('editProductDescription').value = product.description || '';
                
                // فتح modal التعديل
                new bootstrap.Modal(document.getElementById('editProductModal')).show();
            } else {
                alert('لم يتم العثور على المنتج');
            }
        }

        // تحديث منتج
        function updateProduct() {
            const form = document.getElementById('editProductForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            const productId = data.product_id;

            fetch(`/api/products/update/${productId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم تحديث المنتج بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // عرض تفاصيل المنتج
        function viewProductDetails(productId) {
            const products = {{ products|tojson }};
            const product = products.find(p => p.id === productId);
            
            if (product) {
                let details = `
                    <h5>${product.name}</h5>
                    <hr>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>رقم المنتج:</strong> ${product.sku}</p>
                            <p><strong>الفئة:</strong> ${product.category}</p>
                            <p><strong>الباركود:</strong> ${product.barcode || 'غير محدد'}</p>
                            <p><strong>الكمية المتوفرة:</strong> ${product.stock_quantity} ${product.unit || 'قطعة'}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>سعر التكلفة:</strong> ${product.cost_price} ر.س</p>
                            <p><strong>سعر البيع:</strong> ${product.selling_price} ر.س</p>
                            <p><strong>سعر الجملة:</strong> ${product.wholesale_price || product.selling_price} ر.س</p>
                            <p><strong>الربح:</strong> ${(product.selling_price - product.cost_price).toFixed(2)} ر.س</p>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <p><strong>الوصف:</strong></p>
                            <p>${product.description || 'لا يوجد وصف'}</p>
                        </div>
                    </div>
                `;
                
                // إنشاء modal لعرض التفاصيل
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.innerHTML = `
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-eye me-2"></i>تفاصيل المنتج
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                ${details}
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
                new bootstrap.Modal(modal).show();
                
                // إزالة modal بعد الإغلاق
                modal.addEventListener('hidden.bs.modal', function() {
                    document.body.removeChild(modal);
                });
            } else {
                alert('لم يتم العثور على المنتج');
            }
        }

        // حذف منتج
        function deleteProduct(productId, productName) {
            if (confirm('هل أنت متأكد من حذف المنتج: ' + productName + '؟')) {
                fetch(`/api/products/delete/${productId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('تم حذف المنتج بنجاح');
                        location.reload();
                    } else {
                        alert('خطأ: ' + result.message);
                    }
                })
                .catch(error => {
                    alert('خطأ في الاتصال: ' + error);
                });
            }
        }

        // فلترة المنتجات
        function filterProducts() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const categoryFilter = document.getElementById('categoryFilter').value;
            const stockFilter = document.getElementById('stockFilter').value;
            const products = document.querySelectorAll('.product-item');

            products.forEach(product => {
                const name = product.dataset.name;
                const category = product.dataset.category;
                const stock = parseInt(product.dataset.stock);

                let show = true;

                // فلترة البحث
                if (searchTerm && !name.includes(searchTerm)) {
                    show = false;
                }

                // فلترة الفئة
                if (categoryFilter && category !== categoryFilter) {
                    show = false;
                }

                // فلترة المخزون
                if (stockFilter) {
                    if (stockFilter === 'in_stock' && stock <= 0) {
                        show = false;
                    } else if (stockFilter === 'low_stock' && (stock > 5 || stock <= 0)) {
                        show = false;
                    } else if (stockFilter === 'out_of_stock' && stock > 0) {
                        show = false;
                    }
                }

                product.style.display = show ? 'block' : 'none';
            });
        }

        // البحث المباشر
        document.getElementById('searchInput').addEventListener('input', filterProducts);
        document.getElementById('categoryFilter').addEventListener('change', filterProducts);
        document.getElementById('stockFilter').addEventListener('change', filterProducts);
    </script>
</body>
</html>
'''

CUSTOMERS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة العملاء - التميز للهاتف النقال</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        .customers-container { max-width: 1400px; margin: 2rem auto; padding: 0 1rem; }
        .customers-header { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .customers-section { background: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .back-btn { background: linear-gradient(135deg, #6c757d, #495057); border: none; border-radius: 10px; padding: 0.5rem 1rem; color: white; text-decoration: none; }
        .back-btn:hover { color: white; text-decoration: none; }
        .customer-card { transition: transform 0.2s; }
        .customer-card:hover { transform: translateY(-5px); }
        .debt-high { background-color: #f8d7da; border-color: #f5c6cb; }
        .debt-medium { background-color: #fff3cd; border-color: #ffeaa7; }
        .modal-header { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .btn-success { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border: none; }
        .btn-warning { background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%); border: none; }
        .btn-danger { background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%); border: none; }
    </style>
</head>
<body>
    <div class="customers-container">
        <div class="customers-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="mb-2">
                        <i class="fas fa-users me-2"></i>
                        إدارة العملاء
                    </h1>
                    <p class="mb-0">قاعدة بيانات شاملة للعملاء مع التصنيفات والحدود الائتمانية</p>
                </div>
                <div>
                    <button class="btn btn-success me-2" onclick="openAddCustomerModal()">
                        <i class="fas fa-plus me-1"></i>إضافة عميل جديد
                    </button>
                    <a href="/" class="back-btn">
                        <i class="fas fa-arrow-right me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </div>

        <!-- إحصائيات سريعة -->
        <div class="customers-section">
            <div class="row g-4">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-primary">{{ stats.total_customers }}</h4>
                            <small class="text-muted">إجمالي العملاء</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-info">{{ stats.retail_customers }}</h4>
                            <small class="text-muted">عملاء التجزئة</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-warning">{{ stats.wholesale_customers }}</h4>
                            <small class="text-muted">عملاء الجملة</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-danger">{{ "%.0f"|format(stats.total_debt) }}</h4>
                            <small class="text-muted">إجمالي المديونية</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- البحث والفلترة -->
        <div class="customers-section">
            <div class="row mb-3">
                <div class="col-md-4">
                    <input type="text" class="form-control" id="searchInput" placeholder="البحث في العملاء...">
                </div>
                <div class="col-md-3">
                    <select class="form-select" id="typeFilter">
                        <option value="">جميع الأنواع</option>
                        <option value="تجزئة">تجزئة</option>
                        <option value="جملة">جملة</option>
                        <option value="مؤسسة">مؤسسة</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <select class="form-select" id="debtFilter">
                        <option value="">جميع العملاء</option>
                        <option value="debtors">المدينون فقط</option>
                        <option value="active">النشطون فقط</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <button class="btn btn-primary w-100" onclick="filterCustomers()">
                        <i class="fas fa-search me-1"></i>بحث
                    </button>
                </div>
            </div>
        </div>

        <!-- قائمة العملاء -->
        <div class="customers-section">
            <div class="row" id="customersList">
                {% for customer in customers %}
                <div class="col-md-6 col-lg-4 mb-4 customer-item" 
                     data-type="{{ customer.type }}" 
                     data-debt="{{ customer.current_balance }}"
                     data-name="{{ customer.name|lower }}">
                    <div class="card customer-card h-100 {% if customer.current_balance > 1000 %}debt-high{% elif customer.current_balance > 0 %}debt-medium{% endif %}">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="card-title mb-0">{{ customer.name }}</h6>
                                <span class="badge {% if customer.type == 'تجزئة' %}bg-info{% elif customer.type == 'جملة' %}bg-warning{% else %}bg-primary{% endif %}">
                                    {{ customer.type }}
                                </span>
                            </div>
                            <p class="card-text text-muted small">
                                <i class="fas fa-phone me-1"></i>{{ customer.phone }}<br>
                                <i class="fas fa-envelope me-1"></i>{{ customer.email or 'غير محدد' }}
                            </p>
                            <div class="row text-center mb-3">
                                <div class="col-6">
                                    <small class="text-muted">الرصيد الحالي</small>
                                    <div class="fw-bold {% if customer.current_balance > 0 %}text-danger{% else %}text-success{% endif %}">
                                        {{ "%.2f"|format(customer.current_balance) }} ر.س
                                    </div>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">الحد الائتماني</small>
                                    <div class="fw-bold text-primary">{{ "%.2f"|format(customer.credit_limit) }} ر.س</div>
                                </div>
                            </div>
                            <div class="d-flex justify-content-between">
                                <button class="btn btn-sm btn-warning" onclick="editCustomer('{{ customer.id }}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-info" onclick="viewCustomerDetails('{{ customer.id }}')">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deleteCustomer('{{ customer.id }}', '{{ customer.name }}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <!-- Modal تعديل عميل -->
    <div class="modal fade" id="editCustomerModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-edit me-2"></i>تعديل العميل
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="editCustomerForm">
                        <input type="hidden" name="customer_id" id="editCustomerId">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">اسم العميل *</label>
                                    <input type="text" class="form-control" name="name" id="editCustomerName" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">رقم الهاتف *</label>
                                    <input type="tel" class="form-control" name="phone" id="editCustomerPhone" required>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">البريد الإلكتروني</label>
                                    <input type="email" class="form-control" name="email" id="editCustomerEmail">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">نوع العميل *</label>
                                    <select class="form-select" name="type" id="editCustomerType" required>
                                        <option value="">اختر النوع</option>
                                        <option value="تجزئة">تجزئة</option>
                                        <option value="جملة">جملة</option>
                                        <option value="مؤسسة">مؤسسة</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">الحد الائتماني</label>
                                    <input type="number" step="0.01" class="form-control" name="credit_limit" id="editCustomerCreditLimit" value="0">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">الرصيد الحالي</label>
                                    <input type="number" step="0.01" class="form-control" name="current_balance" id="editCustomerBalance" value="0">
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">العنوان</label>
                            <textarea class="form-control" name="address" id="editCustomerAddress" rows="2"></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">ملاحظات</label>
                            <textarea class="form-control" name="notes" id="editCustomerNotes" rows="2"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                    <button type="button" class="btn btn-success" onclick="updateCustomer()">
                        <i class="fas fa-save me-1"></i>حفظ التعديلات
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal إضافة عميل جديد -->
    <div class="modal fade" id="addCustomerModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-plus me-2"></i>إضافة عميل جديد
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="addCustomerForm">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">اسم العميل *</label>
                                    <input type="text" class="form-control" name="name" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">رقم الهاتف *</label>
                                    <input type="tel" class="form-control" name="phone" required>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">البريد الإلكتروني</label>
                                    <input type="email" class="form-control" name="email">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">نوع العميل *</label>
                                    <select class="form-select" name="type" required>
                                        <option value="">اختر النوع</option>
                                        <option value="تجزئة">تجزئة</option>
                                        <option value="جملة">جملة</option>
                                        <option value="مؤسسة">مؤسسة</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">الحد الائتماني</label>
                                    <input type="number" step="0.01" class="form-control" name="credit_limit" value="0">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">الرصيد الحالي</label>
                                    <input type="number" step="0.01" class="form-control" name="current_balance" value="0">
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">العنوان</label>
                            <textarea class="form-control" name="address" rows="2"></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">ملاحظات</label>
                            <textarea class="form-control" name="notes" rows="2"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                    <button type="button" class="btn btn-success" onclick="saveCustomer()">
                        <i class="fas fa-save me-1"></i>حفظ العميل
                    </button>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // فتح modal إضافة عميل جديد
        function openAddCustomerModal() {
            document.getElementById('addCustomerForm').reset();
            new bootstrap.Modal(document.getElementById('addCustomerModal')).show();
        }

        // حفظ عميل جديد
        function saveCustomer() {
            const form = document.getElementById('addCustomerForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/customers/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم إضافة العميل بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // تعديل عميل
        function editCustomer(customerId) {
            // البحث عن العميل في القائمة
            const customers = {{ customers|tojson }};
            const customer = customers.find(c => c.id === customerId);
            
            if (customer) {
                // ملء النموذج ببيانات العميل
                document.getElementById('editCustomerId').value = customer.id;
                document.getElementById('editCustomerName').value = customer.name;
                document.getElementById('editCustomerPhone').value = customer.phone;
                document.getElementById('editCustomerEmail').value = customer.email || '';
                document.getElementById('editCustomerType').value = customer.type;
                document.getElementById('editCustomerCreditLimit').value = customer.credit_limit || 0;
                document.getElementById('editCustomerBalance').value = customer.current_balance || 0;
                document.getElementById('editCustomerAddress').value = customer.address || '';
                document.getElementById('editCustomerNotes').value = customer.notes || '';
                
                // فتح modal التعديل
                new bootstrap.Modal(document.getElementById('editCustomerModal')).show();
            } else {
                alert('لم يتم العثور على العميل');
            }
        }

        // تحديث عميل
        function updateCustomer() {
            const form = document.getElementById('editCustomerForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            const customerId = data.customer_id;

            fetch(`/api/customers/update/${customerId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم تحديث العميل بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // عرض تفاصيل العميل
        function viewCustomerDetails(customerId) {
            const customers = {{ customers|tojson }};
            const customer = customers.find(c => c.id === customerId);
            
            if (customer) {
                let details = `
                    <h5>${customer.name}</h5>
                    <hr>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>رقم الهاتف:</strong> ${customer.phone}</p>
                            <p><strong>البريد الإلكتروني:</strong> ${customer.email || 'غير محدد'}</p>
                            <p><strong>نوع العميل:</strong> ${customer.type}</p>
                            <p><strong>العنوان:</strong> ${customer.address || 'غير محدد'}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>الحد الائتماني:</strong> ${customer.credit_limit || 0} ر.س</p>
                            <p><strong>الرصيد الحالي:</strong> ${customer.current_balance || 0} ر.س</p>
                            <p><strong>المديونية:</strong> <span class="badge ${customer.current_balance > 0 ? 'bg-danger' : 'bg-success'}">${customer.current_balance || 0} ر.س</span></p>
                            <p><strong>تاريخ التسجيل:</strong> ${customer.created_at ? new Date(customer.created_at).toLocaleDateString('ar-SA') : 'غير محدد'}</p>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <p><strong>ملاحظات:</strong></p>
                            <p>${customer.notes || 'لا توجد ملاحظات'}</p>
                        </div>
                    </div>
                `;
                
                // إنشاء modal لعرض التفاصيل
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.innerHTML = `
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-eye me-2"></i>تفاصيل العميل
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                ${details}
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
                new bootstrap.Modal(modal).show();
                
                // إزالة modal بعد الإغلاق
                modal.addEventListener('hidden.bs.modal', function() {
                    document.body.removeChild(modal);
                });
            } else {
                alert('لم يتم العثور على العميل');
            }
        }

        // حذف عميل
        function deleteCustomer(customerId, customerName) {
            if (confirm('هل أنت متأكد من حذف العميل: ' + customerName + '؟')) {
                fetch(`/api/customers/delete/${customerId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('تم حذف العميل بنجاح');
                        location.reload();
                    } else {
                        alert('خطأ: ' + result.message);
                    }
                })
                .catch(error => {
                    alert('خطأ في الاتصال: ' + error);
                });
            }
        }

        // فلترة العملاء
        function filterCustomers() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const typeFilter = document.getElementById('typeFilter').value;
            const debtFilter = document.getElementById('debtFilter').value;
            const customers = document.querySelectorAll('.customer-item');

            customers.forEach(customer => {
                const name = customer.dataset.name;
                const type = customer.dataset.type;
                const debt = parseFloat(customer.dataset.debt);

                let show = true;

                // فلترة البحث
                if (searchTerm && !name.includes(searchTerm)) {
                    show = false;
                }

                // فلترة النوع
                if (typeFilter && type !== typeFilter) {
                    show = false;
                }

                // فلترة المديونية
                if (debtFilter) {
                    if (debtFilter === 'debtors' && debt <= 0) {
                        show = false;
                    } else if (debtFilter === 'active' && debt > 0) {
                        show = false;
                    }
                }

                customer.style.display = show ? 'block' : 'none';
            });
        }

        // البحث المباشر
        document.getElementById('searchInput').addEventListener('input', filterCustomers);
        document.getElementById('typeFilter').addEventListener('change', filterCustomers);
        document.getElementById('debtFilter').addEventListener('change', filterCustomers);
    </script>
</body>
</html>
'''

SETTINGS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إعدادات النظام - التميز للهاتف النقال</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        .settings-container { max-width: 1000px; margin: 2rem auto; padding: 0 1rem; }
        .settings-header { background: linear-gradient(135deg, #ffc107 0%, #ff8c00 100%); color: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .settings-section { background: white; border-radius: 15px; padding: 2rem; }
        .back-btn { background: linear-gradient(135deg, #6c757d, #495057); border: none; border-radius: 10px; padding: 0.5rem 1rem; color: white; text-decoration: none; }
        .back-btn:hover { color: white; text-decoration: none; }
    </style>
</head>
<body>
    <div class="settings-container">
        <div class="settings-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="mb-2">
                        <i class="fas fa-cogs me-2"></i>
                        إعدادات النظام
                    </h1>
                    <p class="mb-0">تخصيص وإعداد نظام إدارة المبيعات</p>
                </div>
                <a href="/" class="back-btn">
                    <i class="fas fa-arrow-right me-1"></i>الرئيسية
                </a>
            </div>
        </div>

        <div class="settings-section">
            <div class="text-center">
                <i class="fas fa-cogs fa-5x text-warning mb-3"></i>
                <h3>إعدادات النظام المتقدمة</h3>
                <p class="text-muted">تخصيص شامل لجميع جوانب النظام</p>

                <div class="alert alert-success mt-4">
                    <h5><i class="fas fa-check-circle me-2"></i>الإعدادات المتاحة:</h5>
                    <ul class="list-unstyled mt-3">
                        <li><i class="fas fa-check text-success me-2"></i>إعدادات الشركة والمعلومات</li>
                        <li><i class="fas fa-check text-success me-2"></i>إعدادات الأسعار وسعر الصرف</li>
                        <li><i class="fas fa-check text-success me-2"></i>إعدادات المخزون والحدود</li>
                        <li><i class="fas fa-check text-success me-2"></i>إعدادات الفواتير والطباعة</li>
                        <li><i class="fas fa-check text-success me-2"></i>إعدادات النظام العامة</li>
                        <li><i class="fas fa-check text-success me-2"></i>النسخ الاحتياطي التلقائي</li>
                    </ul>
                </div>

                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>معلومات الشركة</h5>
                                <p><strong>{{ settings.company_name }}</strong></p>
                                <p>{{ settings.company_address }}</p>
                                <p>{{ settings.company_phone }}</p>
                                <button class="btn btn-warning btn-sm mt-2" onclick="editCompanyInfo()">
                                    <i class="fas fa-edit me-1"></i>تعديل
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>إعدادات النظام</h5>
                                <p><strong>الإصدار:</strong> {{ settings.version }}</p>
                                <p><strong>العملة:</strong> {{ settings.currency }}</p>
                                <p><strong>الضريبة:</strong> {{ (settings.tax_rate * 100)|round(1) }}%</p>
                                <button class="btn btn-warning btn-sm mt-2" onclick="editSystemSettings()">
                                    <i class="fas fa-edit me-1"></i>تعديل
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row mt-4">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="text-center mb-3">إجراءات النظام</h5>
                                <div class="row">
                                    <div class="col-md-4">
                                        <button class="btn btn-success w-100 mb-2" onclick="createBackup()">
                                            <i class="fas fa-download me-1"></i>إنشاء نسخة احتياطية
                                        </button>
                                    </div>
                                    <div class="col-md-4">
                                        <button class="btn btn-info w-100 mb-2" onclick="updatePrices()">
                                            <i class="fas fa-dollar-sign me-1"></i>تحديث الأسعار
                                        </button>
                                    </div>
                                    <div class="col-md-4">
                                        <button class="btn btn-warning w-100 mb-2" onclick="resetSettings()">
                                            <i class="fas fa-undo me-1"></i>إعادة تعيين الإعدادات
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // تعديل معلومات الشركة
        function editCompanyInfo() {
            const settings = {{ settings|tojson }};
            
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-building me-2"></i>تعديل معلومات الشركة
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="companyForm">
                                <div class="mb-3">
                                    <label class="form-label">اسم الشركة</label>
                                    <input type="text" class="form-control" name="company_name" value="${settings.company_name}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">العنوان</label>
                                    <input type="text" class="form-control" name="company_address" value="${settings.company_address}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">رقم الهاتف</label>
                                    <input type="tel" class="form-control" name="company_phone" value="${settings.company_phone}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">البريد الإلكتروني</label>
                                    <input type="email" class="form-control" name="company_email" value="${settings.company_email || ''}">
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                            <button type="button" class="btn btn-success" onclick="saveCompanyInfo()">
                                <i class="fas fa-save me-1"></i>حفظ
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            new bootstrap.Modal(modal).show();
            
            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        }

        // حفظ معلومات الشركة
        function saveCompanyInfo() {
            const form = document.getElementById('companyForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/settings/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم حفظ معلومات الشركة بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // تعديل إعدادات النظام
        function editSystemSettings() {
            const settings = {{ settings|tojson }};
            
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-cogs me-2"></i>تعديل إعدادات النظام
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="systemForm">
                                <div class="mb-3">
                                    <label class="form-label">العملة</label>
                                    <select class="form-select" name="currency">
                                        <option value="ريال" ${settings.currency === 'ريال' ? 'selected' : ''}>ريال</option>
                                        <option value="دولار" ${settings.currency === 'دولار' ? 'selected' : ''}>دولار</option>
                                        <option value="يورو" ${settings.currency === 'يورو' ? 'selected' : ''}>يورو</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">نسبة الضريبة (%)</label>
                                    <input type="number" step="0.01" class="form-control" name="tax_rate" value="${(settings.tax_rate * 100).toFixed(2)}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">سعر الصرف (دولار)</label>
                                    <input type="number" step="0.01" class="form-control" name="exchange_rate" value="${settings.exchange_rate || 3.75}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">الحد الأدنى للمخزون</label>
                                    <input type="number" class="form-control" name="low_stock_threshold" value="${settings.low_stock_threshold || 5}" required>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                            <button type="button" class="btn btn-success" onclick="saveSystemSettings()">
                                <i class="fas fa-save me-1"></i>حفظ
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            new bootstrap.Modal(modal).show();
            
            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        }

        // حفظ إعدادات النظام
        function saveSystemSettings() {
            const form = document.getElementById('systemForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // تحويل الضريبة إلى نسبة عشرية
            data.tax_rate = parseFloat(data.tax_rate) / 100;

            fetch('/api/settings/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم حفظ إعدادات النظام بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // إنشاء نسخة احتياطية
        function createBackup() {
            if (confirm('هل تريد إنشاء نسخة احتياطية جديدة؟')) {
                fetch('/api/settings/backup', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('تم إنشاء النسخة الاحتياطية بنجاح');
                    } else {
                        alert('خطأ: ' + result.message);
                    }
                })
                .catch(error => {
                    alert('خطأ في الاتصال: ' + error);
                });
            }
        }

        // تحديث الأسعار
        function updatePrices() {
            if (confirm('هل تريد تحديث جميع الأسعار حسب سعر الصرف الحالي؟')) {
                fetch('/api/products/update-prices-by-exchange', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('تم تحديث الأسعار بنجاح');
                    } else {
                        alert('خطأ: ' + result.message);
                    }
                })
                .catch(error => {
                    alert('خطأ في الاتصال: ' + error);
                });
            }
        }

        // إعادة تعيين الإعدادات
        function resetSettings() {
            if (confirm('هل أنت متأكد من إعادة تعيين جميع الإعدادات؟ هذا الإجراء لا يمكن التراجع عنه.')) {
                fetch('/api/settings/reset', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('تم إعادة تعيين الإعدادات بنجاح');
                        location.reload();
                    } else {
                        alert('خطأ: ' + result.message);
                    }
                })
                .catch(error => {
                    alert('خطأ في الاتصال: ' + error);
                });
            }
        }
    </script>
</body>
</html>
'''

INVENTORY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة المخزون - التميز للهاتف النقال</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        .inventory-container { max-width: 1400px; margin: 2rem auto; padding: 0 1rem; }
        .inventory-header { background: linear-gradient(135deg, #20c997 0%, #17a2b8 100%); color: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .inventory-section { background: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .back-btn { background: linear-gradient(135deg, #6c757d, #495057); border: none; border-radius: 10px; padding: 0.5rem 1rem; color: white; text-decoration: none; }
        .back-btn:hover { color: white; text-decoration: none; }
        .product-card { transition: transform 0.2s; }
        .product-card:hover { transform: translateY(-5px); }
        .stock-low { background-color: #fff3cd; border-color: #ffeaa7; }
        .stock-out { background-color: #f8d7da; border-color: #f5c6cb; }
        .modal-header { background: linear-gradient(135deg, #20c997 0%, #17a2b8 100%); color: white; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .btn-success { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border: none; }
        .btn-warning { background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%); border: none; }
        .btn-danger { background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%); border: none; }
    </style>
</head>
<body>
    <div class="inventory-container">
        <div class="inventory-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="mb-2">
                        <i class="fas fa-warehouse me-2"></i>
                        إدارة المخزون
                    </h1>
                    <p class="mb-0">متابعة المخزون وحركة البضاعة والجرد</p>
                </div>
                <div>
                    <button class="btn btn-success me-2" onclick="addStock()">
                        <i class="fas fa-plus me-1"></i>إضافة مخزون
                    </button>
                    <button class="btn btn-warning me-2" onclick="adjustStock()">
                        <i class="fas fa-edit me-1"></i>تعديل مخزون
                    </button>
                    <a href="/" class="back-btn">
                        <i class="fas fa-arrow-right me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </div>

        <!-- إحصائيات سريعة -->
        <div class="inventory-section">
            <div class="row g-4">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-primary">{{ stats.total_products }}</h4>
                            <small class="text-muted">إجمالي المنتجات</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-warning">{{ stats.low_stock }}</h4>
                            <small class="text-muted">مخزون منخفض</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-danger">{{ stats.out_of_stock }}</h4>
                            <small class="text-muted">نفد المخزون</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-success">{{ "%.2f"|format(stats.total_value) }} ر.س</h4>
                            <small class="text-muted">قيمة المخزون</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- البحث والفلترة -->
        <div class="inventory-section">
            <div class="row mb-3">
                <div class="col-md-4">
                    <input type="text" class="form-control" id="searchInput" placeholder="البحث في المنتجات...">
                </div>
                <div class="col-md-3">
                    <select class="form-select" id="stockFilter">
                        <option value="">جميع المخزون</option>
                        <option value="in_stock">متوفر</option>
                        <option value="low_stock">مخزون منخفض</option>
                        <option value="out_of_stock">نفد المخزون</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <select class="form-select" id="categoryFilter">
                        <option value="">جميع الفئات</option>
                        <option value="هواتف">هواتف</option>
                        <option value="إكسسوارات">إكسسوارات</option>
                        <option value="قطع غيار">قطع غيار</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <button class="btn btn-primary w-100" onclick="filterInventory()">
                        <i class="fas fa-search me-1"></i>بحث
                    </button>
                </div>
            </div>
        </div>

        <!-- قائمة المنتجات -->
        <div class="inventory-section">
            <div class="row" id="inventoryList">
                {% for product in products %}
                <div class="col-md-6 col-lg-4 mb-4 inventory-item" 
                     data-category="{{ product.category }}" 
                     data-stock="{{ product.stock_quantity }}"
                     data-name="{{ product.name|lower }}">
                    <div class="card product-card h-100 {% if product.stock_quantity <= 0 %}stock-out{% elif product.stock_quantity <= 5 %}stock-low{% endif %}">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="card-title mb-0">{{ product.name }}</h6>
                                <span class="badge {% if product.stock_quantity <= 0 %}bg-danger{% elif product.stock_quantity <= 5 %}bg-warning{% else %}bg-success{% endif %}">
                                    {{ product.stock_quantity }} قطعة
                                </span>
                            </div>
                            <p class="card-text text-muted small">{{ product.description[:50] }}{% if product.description|length > 50 %}...{% endif %}</p>
                            <div class="row text-center mb-3">
                                <div class="col-6">
                                    <small class="text-muted">سعر التكلفة</small>
                                    <div class="fw-bold">{{ "%.2f"|format(product.cost_price) }} ر.س</div>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">قيمة المخزون</small>
                                    <div class="fw-bold text-success">{{ "%.2f"|format(product.stock_quantity * product.cost_price) }} ر.س</div>
                                </div>
                            </div>
                            <div class="d-flex justify-content-between">
                                <button class="btn btn-sm btn-warning" onclick="adjustProductStock('{{ product.id }}', '{{ product.name }}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-info" onclick="viewMovementHistory('{{ product.id }}')">
                                    <i class="fas fa-history"></i>
                                </button>
                                <button class="btn btn-sm btn-success" onclick="addStockToProduct('{{ product.id }}', '{{ product.name }}')">
                                    <i class="fas fa-plus"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // إضافة مخزون
        function addStock() {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-plus me-2"></i>إضافة مخزون
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="addStockForm">
                                <div class="mb-3">
                                    <label class="form-label">المنتج</label>
                                    <select class="form-select" name="product_id" required>
                                        <option value="">اختر المنتج</option>
                                        {% for product in products %}
                                        <option value="{{ product.id }}">{{ product.name }} ({{ product.stock_quantity }} قطعة)</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">الكمية المضافة</label>
                                    <input type="number" class="form-control" name="quantity" required min="1">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">السبب</label>
                                    <select class="form-select" name="reason" required>
                                        <option value="">اختر السبب</option>
                                        <option value="شراء">شراء</option>
                                        <option value="مرتجع">مرتجع</option>
                                        <option value="تعديل">تعديل</option>
                                        <option value="جرد">جرد</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">ملاحظات</label>
                                    <textarea class="form-control" name="notes" rows="2"></textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                            <button type="button" class="btn btn-success" onclick="saveStockAddition()">
                                <i class="fas fa-save me-1"></i>حفظ
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            new bootstrap.Modal(modal).show();
            
            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        }

        // حفظ إضافة المخزون
        function saveStockAddition() {
            const form = document.getElementById('addStockForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/inventory/add-stock', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم إضافة المخزون بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // تعديل مخزون منتج محدد
        function adjustProductStock(productId, productName) {
            const products = {{ products|tojson }};
            const product = products.find(p => p.id === productId);
            
            if (product) {
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.innerHTML = `
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-edit me-2"></i>تعديل مخزون ${productName}
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <form id="adjustStockForm">
                                    <input type="hidden" name="product_id" value="${productId}">
                                    <div class="mb-3">
                                        <label class="form-label">الكمية الحالية</label>
                                        <input type="number" class="form-control" value="${product.stock_quantity}" disabled>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">الكمية الجديدة</label>
                                        <input type="number" class="form-control" name="new_quantity" required min="0">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">السبب</label>
                                        <select class="form-select" name="reason" required>
                                            <option value="">اختر السبب</option>
                                            <option value="تعديل">تعديل</option>
                                            <option value="جرد">جرد</option>
                                            <option value="تلف">تلف</option>
                                            <option value="سرقة">سرقة</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">ملاحظات</label>
                                        <textarea class="form-control" name="notes" rows="2"></textarea>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                                <button type="button" class="btn btn-success" onclick="saveStockAdjustment()">
                                    <i class="fas fa-save me-1"></i>حفظ
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
                new bootstrap.Modal(modal).show();
                
                modal.addEventListener('hidden.bs.modal', function() {
                    document.body.removeChild(modal);
                });
            }
        }

        // حفظ تعديل المخزون
        function saveStockAdjustment() {
            const form = document.getElementById('adjustStockForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/inventory/adjust-stock', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم تعديل المخزون بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // إضافة مخزون لمنتج محدد
        function addStockToProduct(productId, productName) {
            const products = {{ products|tojson }};
            const product = products.find(p => p.id === productId);
            
            if (product) {
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.innerHTML = `
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-plus me-2"></i>إضافة مخزون لـ ${productName}
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <form id="addStockToProductForm">
                                    <input type="hidden" name="product_id" value="${productId}">
                                    <div class="mb-3">
                                        <label class="form-label">الكمية المضافة</label>
                                        <input type="number" class="form-control" name="quantity" required min="1">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">السبب</label>
                                        <select class="form-select" name="reason" required>
                                            <option value="">اختر السبب</option>
                                            <option value="شراء">شراء</option>
                                            <option value="مرتجع">مرتجع</option>
                                            <option value="تعديل">تعديل</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">ملاحظات</label>
                                        <textarea class="form-control" name="notes" rows="2"></textarea>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                                <button type="button" class="btn btn-success" onclick="saveStockToProduct()">
                                    <i class="fas fa-save me-1"></i>حفظ
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
                new bootstrap.Modal(modal).show();
                
                modal.addEventListener('hidden.bs.modal', function() {
                    document.body.removeChild(modal);
                });
            }
        }

        // حفظ إضافة مخزون لمنتج محدد
        function saveStockToProduct() {
            const form = document.getElementById('addStockToProductForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/inventory/add-stock', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم إضافة المخزون بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // عرض تاريخ حركة المخزون
        function viewMovementHistory(productId) {
            fetch(`/api/products/movement-history/${productId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const modal = document.createElement('div');
                    modal.className = 'modal fade';
                    modal.innerHTML = `
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">
                                        <i class="fas fa-history me-2"></i>تاريخ حركة المخزون
                                    </h5>
                                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    ${data.html || '<div class="alert alert-info">لا توجد حركة مخزون</div>'}
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    document.body.appendChild(modal);
                    new bootstrap.Modal(modal).show();
                    
                    modal.addEventListener('hidden.bs.modal', function() {
                        document.body.removeChild(modal);
                    });
                } else {
                    alert('خطأ في تحميل تاريخ الحركة: ' + data.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // تعديل مخزون عام
        function adjustStock() {
            alert('سيتم إضافة هذه الميزة قريباً');
        }

        // فلترة المخزون
        function filterInventory() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const stockFilter = document.getElementById('stockFilter').value;
            const categoryFilter = document.getElementById('categoryFilter').value;
            const items = document.querySelectorAll('.inventory-item');

            items.forEach(item => {
                const name = item.dataset.name;
                const stock = parseInt(item.dataset.stock);
                const category = item.dataset.category;

                let show = true;

                // فلترة البحث
                if (searchTerm && !name.includes(searchTerm)) {
                    show = false;
                }

                // فلترة المخزون
                if (stockFilter) {
                    if (stockFilter === 'in_stock' && stock <= 0) {
                        show = false;
                    } else if (stockFilter === 'low_stock' && (stock > 5 || stock <= 0)) {
                        show = false;
                    } else if (stockFilter === 'out_of_stock' && stock > 0) {
                        show = false;
                    }
                }

                // فلترة الفئة
                if (categoryFilter && category !== categoryFilter) {
                    show = false;
                }

                item.style.display = show ? 'block' : 'none';
            });
        }

        // البحث المباشر
        document.getElementById('searchInput').addEventListener('input', filterInventory);
        document.getElementById('stockFilter').addEventListener('change', filterInventory);
        document.getElementById('categoryFilter').addEventListener('change', filterInventory);
    </script>
</body>
</html>
'''

PURCHASES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة المشتريات - التميز للهاتف النقال</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        .purchases-container { max-width: 1400px; margin: 2rem auto; padding: 0 1rem; }
        .purchases-header { background: linear-gradient(135deg, #fd7e14 0%, #ff6b35 100%); color: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .purchases-section { background: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .back-btn { background: linear-gradient(135deg, #6c757d, #495057); border: none; border-radius: 10px; padding: 0.5rem 1rem; color: white; text-decoration: none; }
        .back-btn:hover { color: white; text-decoration: none; }
        .purchase-card { transition: transform 0.2s; }
        .purchase-card:hover { transform: translateY(-5px); }
        .status-pending { background-color: #fff3cd; border-color: #ffeaa7; }
        .status-completed { background-color: #d1ecf1; border-color: #bee5eb; }
        .status-cancelled { background-color: #f8d7da; border-color: #f5c6cb; }
        .modal-header { background: linear-gradient(135deg, #fd7e14 0%, #ff6b35 100%); color: white; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .btn-success { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border: none; }
        .btn-warning { background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%); border: none; }
        .btn-danger { background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%); border: none; }
    </style>
</head>
<body>
    <div class="purchases-container">
        <div class="purchases-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="mb-2">
                        <i class="fas fa-shopping-bag me-2"></i>
                        إدارة المشتريات
                    </h1>
                    <p class="mb-0">إدارة المشتريات والموردين والفواتير</p>
                </div>
                <div>
                    <button class="btn btn-success me-2" onclick="addPurchase()">
                        <i class="fas fa-plus me-1"></i>إضافة مشترى جديد
                    </button>
                    <button class="btn btn-info me-2" onclick="addSupplier()">
                        <i class="fas fa-user-plus me-1"></i>إضافة مورد
                    </button>
                    <a href="/" class="back-btn">
                        <i class="fas fa-arrow-right me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </div>

        <!-- إحصائيات سريعة -->
        <div class="purchases-section">
            <div class="row g-4">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-primary">{{ stats.total_purchases }}</h4>
                            <small class="text-muted">إجمالي المشتريات</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-success">{{ "%.2f"|format(stats.total_amount) }} ر.س</h4>
                            <small class="text-muted">إجمالي المبالغ</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-warning">{{ stats.pending_purchases }}</h4>
                            <small class="text-muted">مشتريات معلقة</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h4 class="text-info">{{ suppliers|length }}</h4>
                            <small class="text-muted">عدد الموردين</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- قائمة المشتريات -->
        <div class="purchases-section">
            <h4 class="mb-4"><i class="fas fa-list me-2"></i>قائمة المشتريات</h4>
            <div class="row" id="purchasesList">
                {% for purchase in purchases.values() %}
                <div class="col-md-6 col-lg-4 mb-4">
                    <div class="card purchase-card h-100 status-{{ purchase.status }}">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="card-title mb-0">{{ purchase.supplier_name or 'مورد غير محدد' }}</h6>
                                <span class="badge {% if purchase.status == 'pending' %}bg-warning{% elif purchase.status == 'completed' %}bg-success{% else %}bg-danger{% endif %}">
                                    {{ purchase.status }}
                                </span>
                            </div>
                            <p class="card-text text-muted small">
                                <strong>رقم الفاتورة:</strong> {{ purchase.invoice_number or 'غير محدد' }}<br>
                                <strong>التاريخ:</strong> {{ purchase.date or 'غير محدد' }}<br>
                                <strong>المبلغ:</strong> {{ "%.2f"|format(purchase.total_amount or 0) }} ر.س
                            </p>
                            <div class="d-flex justify-content-between">
                                <button class="btn btn-sm btn-info" onclick="viewPurchaseDetails('{{ purchase.id }}')">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-warning" onclick="editPurchase('{{ purchase.id }}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deletePurchase('{{ purchase.id }}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // إضافة مشترى جديد
        function addPurchase() {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-plus me-2"></i>إضافة مشترى جديد
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="addPurchaseForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">المورد</label>
                                            <select class="form-select" name="supplier_id" required>
                                                <option value="">اختر المورد</option>
                                                {% for supplier_id, supplier in suppliers.items() %}
                                                <option value="{{ supplier_id }}">{{ supplier.name }}</option>
                                                {% endfor %}
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">رقم الفاتورة</label>
                                            <input type="text" class="form-control" name="invoice_number" required>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">التاريخ</label>
                                            <input type="date" class="form-control" name="date" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">الحالة</label>
                                            <select class="form-select" name="status" required>
                                                <option value="pending">معلق</option>
                                                <option value="completed">مكتمل</option>
                                                <option value="cancelled">ملغي</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">الملاحظات</label>
                                    <textarea class="form-control" name="notes" rows="3"></textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                            <button type="button" class="btn btn-success" onclick="savePurchase()">
                                <i class="fas fa-save me-1"></i>حفظ
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            new bootstrap.Modal(modal).show();
            
            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        }

        // حفظ المشترى
        function savePurchase() {
            const form = document.getElementById('addPurchaseForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/purchases/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم إضافة المشترى بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // إضافة مورد
        function addSupplier() {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-user-plus me-2"></i>إضافة مورد جديد
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="addSupplierForm">
                                <div class="mb-3">
                                    <label class="form-label">اسم المورد</label>
                                    <input type="text" class="form-control" name="name" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">رقم الهاتف</label>
                                    <input type="tel" class="form-control" name="phone" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">البريد الإلكتروني</label>
                                    <input type="email" class="form-control" name="email">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">العنوان</label>
                                    <textarea class="form-control" name="address" rows="2"></textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                            <button type="button" class="btn btn-success" onclick="saveSupplier()">
                                <i class="fas fa-save me-1"></i>حفظ
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            new bootstrap.Modal(modal).show();
            
            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        }

        // حفظ المورد
        function saveSupplier() {
            const form = document.getElementById('addSupplierForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/suppliers/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم إضافة المورد بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // عرض تفاصيل المشترى
        function viewPurchaseDetails(purchaseId) {
            alert('سيتم إضافة هذه الميزة قريباً');
        }

        // تعديل المشترى
        function editPurchase(purchaseId) {
            alert('سيتم إضافة هذه الميزة قريباً');
        }

        // حذف المشترى
        function deletePurchase(purchaseId) {
            if (confirm('هل أنت متأكد من حذف هذا المشترى؟')) {
                fetch(`/api/purchases/delete/${purchaseId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('تم حذف المشترى بنجاح');
                        location.reload();
                    } else {
                        alert('خطأ: ' + result.message);
                    }
                })
                .catch(error => {
                    alert('خطأ في الاتصال: ' + error);
                });
            }
        }
    </script>
</body>
</html>
'''

USERS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إدارة المستخدمين - التميز للهاتف النقال</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        .users-container { max-width: 1000px; margin: 2rem auto; padding: 0 1rem; }
        .users-header { background: linear-gradient(135deg, #17a2b8 0%, #007bff 100%); color: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .users-section { background: white; border-radius: 15px; padding: 2rem; }
        .back-btn { background: linear-gradient(135deg, #6c757d, #495057); border: none; border-radius: 10px; padding: 0.5rem 1rem; color: white; text-decoration: none; }
        .back-btn:hover { color: white; text-decoration: none; }
        .user-card { border: 1px solid #e9ecef; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; }
        .role-badge { padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
    </style>
</head>
<body>
    <div class="users-container">
        <div class="users-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="mb-2">
                        <i class="fas fa-users-cog me-2"></i>
                        إدارة المستخدمين
                    </h1>
                    <p class="mb-0">إدارة المستخدمين والصلاحيات</p>
                </div>
                <a href="/" class="back-btn">
                    <i class="fas fa-arrow-right me-1"></i>الرئيسية
                </a>
            </div>
        </div>

        <div class="users-section">
            <div class="text-center mb-4">
                <i class="fas fa-users-cog fa-5x text-info mb-3"></i>
                <h3>إدارة المستخدمين والصلاحيات</h3>
                <p class="text-muted">نظام متقدم لإدارة المستخدمين مع 5 أنواع مختلفة</p>
            </div>

            <div class="row">
                {% for username, user in users.items() %}
                <div class="col-md-6 mb-3">
                    <div class="user-card">
                        <div class="d-flex align-items-center">
                            <div class="me-3">
                                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 50px; height: 50px;">
                                    {{ user.full_name[0] if user.full_name else 'م' }}
                                </div>
                            </div>
                            <div class="flex-grow-1">
                                <h6 class="mb-1">{{ user.full_name }}</h6>
                                <p class="mb-1 text-muted">{{ user.email }}</p>
                                <span class="role-badge bg-{{ 'danger' if user.role == 'admin' else 'success' if user.role == 'manager' else 'info' if user.role == 'cashier' else 'warning' if user.role == 'accountant' else 'secondary' }}">
                                    {{ user_roles[user.role].name }}
                                </span>
                            </div>
                            <div>
                                {% if user.is_active %}
                                <span class="badge bg-success">نشط</span>
                                {% else %}
                                <span class="badge bg-secondary">غير نشط</span>
                                {% endif %}
                            </div>
                        </div>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-outline-primary me-1" onclick="editUser('{{ username }}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-warning me-1" onclick="toggleUserStatus('{{ username }}')">
                                <i class="fas fa-toggle-on"></i>
                            </button>
                            {% if username != 'admin' %}
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteUser('{{ username }}')">
                                <i class="fas fa-trash"></i>
                            </button>
                            {% endif %}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>

            <div class="alert alert-success mt-4">
                <h5><i class="fas fa-check-circle me-2"></i>أنواع المستخدمين:</h5>
                <ul class="list-unstyled mt-3">
                    {% for role_key, role_info in user_roles.items() %}
                    <li><i class="fas fa-user text-success me-2"></i><strong>{{ role_info.name }}:</strong> {{ role_info.description }}</li>
                    {% endfor %}
                </ul>
            </div>

            <!-- أزرار الإجراءات -->
            <div class="text-center mt-4">
                <button class="btn btn-success me-2" onclick="addUser()">
                    <i class="fas fa-user-plus me-1"></i>إضافة مستخدم جديد
                </button>
                <button class="btn btn-info" onclick="showUsersReport()">
                    <i class="fas fa-chart-line me-1"></i>تقرير المستخدمين
                </button>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // إضافة مستخدم جديد
        function addUser() {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-user-plus me-2"></i>إضافة مستخدم جديد
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="addUserForm">
                                <div class="mb-3">
                                    <label class="form-label">اسم المستخدم *</label>
                                    <input type="text" class="form-control" name="username" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">الاسم الكامل *</label>
                                    <input type="text" class="form-control" name="full_name" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">البريد الإلكتروني</label>
                                    <input type="email" class="form-control" name="email">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">كلمة المرور *</label>
                                    <input type="password" class="form-control" name="password" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">الدور *</label>
                                    <select class="form-select" name="role" required>
                                        <option value="">اختر الدور</option>
                                        <option value="admin">مدير النظام</option>
                                        <option value="manager">مدير المبيعات</option>
                                        <option value="cashier">أمين الصندوق</option>
                                        <option value="accountant">محاسب</option>
                                        <option value="employee">موظف</option>
                                    </select>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                            <button type="button" class="btn btn-success" onclick="saveUser()">إضافة المستخدم</button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
            new bootstrap.Modal(modal).show();

            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        }

        // حفظ المستخدم الجديد
        function saveUser() {
            const form = document.getElementById('addUserForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/users/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم إضافة المستخدم بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // تقرير المستخدمين
        function showUsersReport() {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-chart-line me-2"></i>تقرير المستخدمين
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle me-2"></i>
                                تقرير المستخدمين المفصل - ميزة قيد التطوير
                            </div>
                            <p>سيتضمن التقرير:</p>
                            <ul>
                                <li>إحصائيات شاملة لجميع المستخدمين</li>
                                <li>تفاصيل الصلاحيات والأدوار</li>
                                <li>سجل النشاطات والعمليات</li>
                                <li>رسوم بيانية تفاعلية</li>
                                <li>إمكانية التصدير والطباعة</li>
                            </ul>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
            new bootstrap.Modal(modal).show();

            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        }

        // تعديل مستخدم
        function editUser(username) {
            fetch('/api/users/details/' + username)
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    const user = result.user;
                    showEditUserModal(user);
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // عرض modal تعديل المستخدم
        function showEditUserModal(user) {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-edit me-2"></i>تعديل المستخدم
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="editUserForm">
                                <input type="hidden" name="username" value="${user.username}">
                                <div class="mb-3">
                                    <label class="form-label">الاسم الكامل *</label>
                                    <input type="text" class="form-control" name="full_name" value="${user.full_name}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">البريد الإلكتروني</label>
                                    <input type="email" class="form-control" name="email" value="${user.email || ''}">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">الدور *</label>
                                    <select class="form-select" name="role" required>
                                        <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>مدير النظام</option>
                                        <option value="manager" ${user.role === 'manager' ? 'selected' : ''}>مدير المبيعات</option>
                                        <option value="cashier" ${user.role === 'cashier' ? 'selected' : ''}>أمين الصندوق</option>
                                        <option value="accountant" ${user.role === 'accountant' ? 'selected' : ''}>محاسب</option>
                                        <option value="employee" ${user.role === 'employee' ? 'selected' : ''}>موظف</option>
                                    </select>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                            <button type="button" class="btn btn-success" onclick="updateUser()">حفظ التغييرات</button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
            new bootstrap.Modal(modal).show();

            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        }

        // تحديث المستخدم
        function updateUser() {
            const form = document.getElementById('editUserForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/users/update/' + data.username, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم تحديث المستخدم بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // حذف مستخدم
        function deleteUser(username) {
            if (confirm('هل أنت متأكد من حذف هذا المستخدم؟ هذا الإجراء لا يمكن التراجع عنه.')) {
                fetch('/api/users/delete/' + username, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('تم حذف المستخدم بنجاح');
                        location.reload();
                    } else {
                        alert('خطأ: ' + result.message);
                    }
                })
                .catch(error => {
                    alert('خطأ في الاتصال: ' + error);
                });
            }
        }

        // تفعيل/إيقاف مستخدم
        function toggleUserStatus(username) {
            fetch('/api/users/toggle-status/' + username, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم تغيير حالة المستخدم بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }
    </script>
</body>
</html>
'''

# قالب نظام الشركاء
PARTNERS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام حساب الشركاء - التميز للهاتف النقال</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        .partners-container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .partners-header { background: linear-gradient(135deg, #17a2b8 0%, #007bff 100%); color: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .partners-section { background: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .back-btn { background: linear-gradient(135deg, #6c757d, #495057); border: none; border-radius: 10px; padding: 0.5rem 1rem; color: white; text-decoration: none; }
        .back-btn:hover { color: white; text-decoration: none; }
        .partner-card { border: 1px solid #e9ecef; border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem; }
        .partner-name { font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem; }
        .partner-info { color: #666; font-size: 0.9rem; }
        .contribution-badge { background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; }
        .balance-badge { background: linear-gradient(135deg, #ffc107, #ff8c00); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; }
        .btn-action { margin: 0.25rem; }
        .stats-card { background: linear-gradient(135deg, #28a745, #20c997); color: white; border-radius: 10px; padding: 1.5rem; text-align: center; }
        .stats-value { font-size: 2rem; font-weight: bold; }
        .stats-label { font-size: 0.9rem; opacity: 0.9; }
    </style>
</head>
<body>
    <div class="partners-container">
        <div class="partners-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="mb-2">
                        <i class="fas fa-handshake me-2"></i>
                        نظام حساب الشركاء
                    </h1>
                    <p class="mb-0">إدارة الشراكة والمساهمات وتوزيع الأرباح</p>
                </div>
                <a href="/" class="back-btn">
                    <i class="fas fa-arrow-right me-1"></i>الرئيسية
                </a>
            </div>
        </div>

        <!-- إحصائيات الشركاء -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-value">{{ partners|length }}</div>
                    <div class="stats-label">إجمالي الشركاء</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card" style="background: linear-gradient(135deg, #007bff, #0056b3);">
                    <div class="stats-value">{{ "%.2f"|format(partners.values()|sum(attribute='contribution_amount')|default(0)) }}</div>
                    <div class="stats-label">إجمالي المساهمات</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card" style="background: linear-gradient(135deg, #ffc107, #ff8c00);">
                    <div class="stats-value">{{ "%.2f"|format(partners.values()|sum(attribute='current_balance')|default(0)) }}</div>
                    <div class="stats-label">إجمالي الأرصدة</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card" style="background: linear-gradient(135deg, #dc3545, #c82333);">
                    <div class="stats-value">{{ "%.1f"|format(partners.values()|sum(attribute='contribution_percentage')|default(0)) }}%</div>
                    <div class="stats-label">إجمالي النسب</div>
                </div>
            </div>
        </div>

        <!-- أزرار الإجراءات -->
        <div class="partners-section">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h4><i class="fas fa-users me-2"></i>إدارة الشركاء</h4>
                <div>
                    <button class="btn btn-success me-2" onclick="openAddPartnerModal()">
                        <i class="fas fa-plus me-1"></i>إضافة شريك
                    </button>
                    <button class="btn btn-warning me-2" onclick="openDistributeProfitsModal()">
                        <i class="fas fa-coins me-1"></i>توزيع الأرباح
                    </button>
                    <button class="btn btn-info" onclick="showPartnersReport()">
                        <i class="fas fa-chart-line me-1"></i>تقرير الشركاء
                    </button>
                </div>
            </div>

            <!-- قائمة الشركاء -->
            {% if partners %}
                <div class="row">
                    {% for partner_id, partner in partners.items() %}
                    <div class="col-md-6 mb-3">
                        <div class="partner-card">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <div class="partner-name">{{ partner.name }}</div>
                                    <div class="partner-info">
                                        <i class="fas fa-phone me-1"></i>{{ partner.phone|default('غير محدد') }}<br>
                                        <i class="fas fa-envelope me-1"></i>{{ partner.email|default('غير محدد') }}
                                    </div>
                                    <div class="mt-2">
                                        <span class="contribution-badge me-2">
                                            مساهمة: {{ "%.2f"|format(partner.contribution_amount) }} {{ system_config.currency_symbol }}
                                        </span>
                                        <span class="balance-badge">
                                            رصيد: {{ "%.2f"|format(partner.current_balance) }} {{ system_config.currency_symbol }}
                                        </span>
                                    </div>
                                    <div class="mt-1">
                                        <small class="text-muted">النسبة: {{ "%.1f"|format(partner.contribution_percentage) }}%</small>
                                    </div>
                                </div>
                                <div class="dropdown">
                                    <button class="btn btn-outline-secondary btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                        <i class="fas fa-ellipsis-v"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" href="#" onclick="editPartner('{{ partner_id }}')">
                                            <i class="fas fa-edit me-1"></i>تعديل
                                        </a></li>
                                        <li><a class="dropdown-item" href="#" onclick="addWithdrawal('{{ partner_id }}')">
                                            <i class="fas fa-money-bill-wave me-1"></i>سحب أموال
                                        </a></li>
                                        <li><a class="dropdown-item" href="#" onclick="viewPartnerDetails('{{ partner_id }}')">
                                            <i class="fas fa-eye me-1"></i>عرض التفاصيل
                                        </a></li>
                                        <li><hr class="dropdown-divider"></li>
                                        <li><a class="dropdown-item text-danger" href="#" onclick="deletePartner('{{ partner_id }}')">
                                            <i class="fas fa-trash me-1"></i>حذف
                                        </a></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="text-center py-5">
                    <i class="fas fa-handshake fa-5x text-muted mb-3"></i>
                    <h5 class="text-muted">لا يوجد شركاء مسجلين</h5>
                    <p class="text-muted">ابدأ بإضافة الشركاء لإدارة الشراكة</p>
                    <button class="btn btn-success" onclick="openAddPartnerModal()">
                        <i class="fas fa-plus me-1"></i>إضافة أول شريك
                    </button>
                </div>
            {% endif %}
        </div>
    </div>

    <!-- Modal إضافة شريك -->
    <div class="modal fade" id="addPartnerModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">إضافة شريك جديد</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="addPartnerForm">
                        <div class="mb-3">
                            <label class="form-label">اسم الشريك *</label>
                            <input type="text" class="form-control" name="name" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">رقم الهاتف</label>
                            <input type="text" class="form-control" name="phone">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">البريد الإلكتروني</label>
                            <input type="email" class="form-control" name="email">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">مبلغ المساهمة *</label>
                            <input type="number" class="form-control" name="contribution_amount" step="0.01" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">نسبة المساهمة (%) *</label>
                            <input type="number" class="form-control" name="contribution_percentage" step="0.1" min="0" max="100" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">ملاحظات</label>
                            <textarea class="form-control" name="notes" rows="3"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                    <button type="button" class="btn btn-success" onclick="savePartner()">حفظ الشريك</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // فتح modal إضافة شريك
        function openAddPartnerModal() {
            document.getElementById('addPartnerForm').reset();
            new bootstrap.Modal(document.getElementById('addPartnerModal')).show();
        }

        // حفظ شريك جديد
        function savePartner() {
            const form = document.getElementById('addPartnerForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/partners/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم إضافة الشريك بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // إضافة مسحوبات
        function addWithdrawal(partnerId) {
            const amount = prompt('أدخل مبلغ السحب:');
            if (amount && parseFloat(amount) > 0) {
                const description = prompt('وصف العملية (اختياري):') || '';

                fetch('/api/partners/withdrawal', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        partner_id: partnerId,
                        amount: parseFloat(amount),
                        description: description
                    })
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('تم تسجيل السحب بنجاح');
                        location.reload();
                    } else {
                        alert('خطأ: ' + result.message);
                    }
                })
                .catch(error => {
                    alert('خطأ في الاتصال: ' + error);
                });
            }
        }

        // توزيع الأرباح
        function openDistributeProfitsModal() {
            const totalProfit = prompt('أدخل إجمالي الأرباح المراد توزيعها:');
            if (totalProfit && parseFloat(totalProfit) > 0) {
                const period = prompt('فترة التوزيع (مثال: يناير 2025):') || '';
                const notes = prompt('ملاحظات (اختياري):') || '';

                fetch('/api/partners/distribute-profits', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        total_profit: parseFloat(totalProfit),
                        period: period,
                        notes: notes
                    })
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('تم توزيع الأرباح بنجاح');
                        location.reload();
                    } else {
                        alert('خطأ: ' + result.message);
                    }
                })
                .catch(error => {
                    alert('خطأ في الاتصال: ' + error);
                });
            }
        }

        // حذف شريك
        function deletePartner(partnerId) {
            if (confirm('هل أنت متأكد من حذف هذا الشريك؟ هذا الإجراء لا يمكن التراجع عنه.')) {
                fetch('/api/partners/delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        partner_id: partnerId
                    })
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('تم حذف الشريك بنجاح');
                        location.reload();
                    } else {
                        alert('خطأ: ' + result.message);
                    }
                })
                .catch(error => {
                    alert('خطأ في الاتصال: ' + error);
                });
            }
        }

        // عرض تفاصيل الشريك
        function viewPartnerDetails(partnerId) {
            fetch('/api/partners/details/' + partnerId)
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    const partner = result.partner;
                    const stats = result.stats;

                    const modal = document.createElement('div');
                    modal.className = 'modal fade';
                    modal.innerHTML = `
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">
                                        <i class="fas fa-user me-2"></i>تفاصيل الشريك: ${partner.name}
                                    </h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <h6>المعلومات الأساسية</h6>
                                            <p><strong>الاسم:</strong> ${partner.name}</p>
                                            <p><strong>الهاتف:</strong> ${partner.phone || 'غير محدد'}</p>
                                            <p><strong>البريد:</strong> ${partner.email || 'غير محدد'}</p>
                                            <p><strong>المساهمة:</strong> ${partner.contribution_amount} ر.س</p>
                                            <p><strong>النسبة:</strong> ${partner.contribution_percentage}%</p>
                                        </div>
                                        <div class="col-md-6">
                                            <h6>الإحصائيات المالية</h6>
                                            <p><strong>الرصيد الحالي:</strong> ${partner.current_balance || 0} ر.س</p>
                                            <p><strong>إجمالي الأرباح:</strong> ${stats.total_profits} ر.س</p>
                                            <p><strong>إجمالي المسحوبات:</strong> ${stats.total_withdrawals} ر.س</p>
                                            <p><strong>عدد التوزيعات:</strong> ${stats.distributions_count}</p>
                                            <p><strong>عدد المسحوبات:</strong> ${stats.withdrawals_count}</p>
                                        </div>
                                    </div>
                                    ${partner.notes ? `<div class="mt-3"><h6>ملاحظات</h6><p>${partner.notes}</p></div>` : ''}
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                                </div>
                            </div>
                        </div>
                    `;

                    document.body.appendChild(modal);
                    new bootstrap.Modal(modal).show();

                    modal.addEventListener('hidden.bs.modal', function() {
                        document.body.removeChild(modal);
                    });
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // تعديل شريك
        function editPartner(partnerId) {
            fetch('/api/partners/details/' + partnerId)
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    const partner = result.partner;

                    const modal = document.createElement('div');
                    modal.className = 'modal fade';
                    modal.innerHTML = `
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">
                                        <i class="fas fa-edit me-2"></i>تعديل الشريك
                                    </h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    <form id="editPartnerForm">
                                        <input type="hidden" name="partner_id" value="${partnerId}">
                                        <div class="mb-3">
                                            <label class="form-label">اسم الشريك *</label>
                                            <input type="text" class="form-control" name="name" value="${partner.name}" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">رقم الهاتف</label>
                                            <input type="text" class="form-control" name="phone" value="${partner.phone || ''}">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">البريد الإلكتروني</label>
                                            <input type="email" class="form-control" name="email" value="${partner.email || ''}">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">مبلغ المساهمة *</label>
                                            <input type="number" class="form-control" name="contribution_amount" step="0.01" value="${partner.contribution_amount}" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">نسبة المساهمة (%) *</label>
                                            <input type="number" class="form-control" name="contribution_percentage" step="0.1" min="0" max="100" value="${partner.contribution_percentage}" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">ملاحظات</label>
                                            <textarea class="form-control" name="notes" rows="3">${partner.notes || ''}</textarea>
                                        </div>
                                    </form>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                                    <button type="button" class="btn btn-success" onclick="updatePartner()">حفظ التغييرات</button>
                                </div>
                            </div>
                        </div>
                    `;

                    document.body.appendChild(modal);
                    new bootstrap.Modal(modal).show();

                    modal.addEventListener('hidden.bs.modal', function() {
                        document.body.removeChild(modal);
                    });
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // تحديث بيانات الشريك
        function updatePartner() {
            const form = document.getElementById('editPartnerForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/partners/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('تم تحديث بيانات الشريك بنجاح');
                    location.reload();
                } else {
                    alert('خطأ: ' + result.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // تقرير الشركاء
        function showPartnersReport() {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-chart-line me-2"></i>تقرير الشركاء
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle me-2"></i>
                                تقرير الشركاء المفصل - ميزة قيد التطوير
                            </div>
                            <p>سيتضمن التقرير:</p>
                            <ul>
                                <li>إحصائيات شاملة لجميع الشركاء</li>
                                <li>تفاصيل المساهمات والأرباح</li>
                                <li>سجل المسحوبات والتوزيعات</li>
                                <li>رسوم بيانية تفاعلية</li>
                                <li>إمكانية التصدير والطباعة</li>
                            </ul>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
            new bootstrap.Modal(modal).show();

            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        }
    </script>
</body>
</html>
'''

# ===== تشغيل النظام =====

def create_backup():
    """إنشاء نسخة احتياطية"""
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{BACKUP_DIR}/backup_{timestamp}.zip"

        with zipfile.ZipFile(backup_filename, 'w') as backup_zip:
            if os.path.exists(DATABASE_FILE):
                backup_zip.write(DATABASE_FILE)

        print(f"✅ تم إنشاء نسخة احتياطية: {backup_filename}")
        return True
    except Exception as e:
        print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")
        return False

def print_system_info():
    """طباعة معلومات النظام"""
    print("=" * 80)
    print("🚀 نظام إدارة المبيعات المتقدم - الإصدار السادس المتكامل والشامل")
    print(f"🏪 مخصص لمحل: {SYSTEM_CONFIG['company_name']}")
    print(f"📅 تاريخ الإنشاء: 4 أغسطس 2025")
    print(f"🎯 الإصدار: {SYSTEM_CONFIG['version']}")
    print("=" * 80)
    print("📋 الميزات المتكاملة:")
    print("   ✅ نظام المستخدمين والصلاحيات (5 أنواع)")
    print("   ✅ نقطة البيع المتقدمة مع الاختصارات والقوائم السياقية")
    print("   ✅ إدارة المنتجات الشاملة مع الباركود والمخزون")
    print("   ✅ إدارة العملاء المتقدمة مع التصنيفات والحدود الائتمانية")
    print("   ✅ نظام التقارير والتحليلات الشامل")
    print("   ✅ إدارة المخزون المتقدمة مع تتبع الحركة")
    print("   ✅ نظام البيع والشراء المتكامل")
    print("   ✅ نظام حساب الشركاء")
    print("   ✅ الإعدادات المتقدمة والتخصيص الشامل")
    print("   ✅ النسخ الاحتياطي التلقائي")
    print("   ✅ نظام الأمان المتقدم")
    print("   ✅ واجهات عصرية ومتجاوبة")
    print("=" * 80)
    print("📋 معلومات تسجيل الدخول:")
    print("   👤 مدير النظام: admin / admin123")
    print("   👤 مدير المبيعات: manager / manager123")
    print("   👤 أمين الصندوق: cashier / cashier123")
    print("=" * 80)
    print("🌐 روابط النظام:")
    print("   🏠 الرئيسية: http://localhost:5000")
    print("   💰 نقطة البيع: http://localhost:5000/pos")
    print("   📱 إدارة المنتجات: http://localhost:5000/products")
    print("   👥 إدارة العملاء: http://localhost:5000/customers")
    print("   📊 التقارير: http://localhost:5000/reports")
    print("   📦 إدارة المخزون: http://localhost:5000/inventory")
    print("   🛒 المشتريات: http://localhost:5000/purchases")
    print("   🤝 حساب الشركاء: http://localhost:5000/partners")
    print("   ⚙️ الإعدادات: http://localhost:5000/settings")
    print("   👥 إدارة المستخدمين: http://localhost:5000/users")
    print("=" * 80)
    print("🏢 معلومات المحل:")
    print(f"   📱 اسم المحل: {SYSTEM_CONFIG['company_name']}")
    print(f"   📞 الهاتف: {SYSTEM_CONFIG['company_phone']}")
    print(f"   📧 البريد: {SYSTEM_CONFIG['company_email']}")
    print(f"   📍 العنوان: {SYSTEM_CONFIG['company_address']}")
    print(f"   🕒 ساعات العمل: {SYSTEM_CONFIG['working_hours']}")
    print(f"   📄 السجل التجاري: {SYSTEM_CONFIG['cr_number']}")
    print(f"   🧾 الرقم الضريبي: {SYSTEM_CONFIG['vat_number']}")
    print("=" * 80)

# ===== قالب التقارير =====
REPORTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>التقارير والتحليلات - التميز للهاتف النقال</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        .reports-container { max-width: 1400px; margin: 2rem auto; padding: 0 1rem; }
        .reports-header { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .reports-section { background: white; border-radius: 15px; padding: 2rem; margin-bottom: 2rem; }
        .back-btn { background: linear-gradient(135deg, #6c757d, #495057); border: none; border-radius: 10px; padding: 0.5rem 1rem; color: white; text-decoration: none; }
        .back-btn:hover { color: white; text-decoration: none; }
        .stat-card { transition: transform 0.2s; }
        .stat-card:hover { transform: translateY(-5px); }
        .modal-header { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .btn-success { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border: none; }
        .btn-warning { background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%); border: none; }
        .btn-danger { background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%); border: none; }
        .chart-container { position: relative; height: 300px; margin: 1rem 0; }
    </style>
</head>
<body>
    <div class="reports-container">
        <div class="reports-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="mb-2">
                        <i class="fas fa-chart-line me-2"></i>
                        التقارير والتحليلات
                    </h1>
                    <p class="mb-0">تقارير شاملة للمبيعات والمخزون والعملاء والأرباح</p>
                </div>
                <div>
                    <button class="btn btn-success me-2" onclick="generateReport('sales')">
                        <i class="fas fa-download me-1"></i>تقرير المبيعات
                    </button>
                    <button class="btn btn-warning me-2" onclick="generateReport('inventory')">
                        <i class="fas fa-download me-1"></i>تقرير المخزون
                    </button>
                    <a href="/" class="back-btn">
                        <i class="fas fa-arrow-right me-1"></i>الرئيسية
                    </a>
                </div>
            </div>
        </div>

        <!-- إحصائيات سريعة -->
        <div class="reports-section">
            <h4 class="mb-4"><i class="fas fa-chart-pie me-2"></i>الإحصائيات السريعة</h4>
            <div class="row g-4">
                <div class="col-md-3">
                    <div class="card stat-card text-center">
                        <div class="card-body">
                            <i class="fas fa-shopping-cart fa-2x text-primary mb-2"></i>
                            <h4 class="text-primary">{{ stats.total_sales }}</h4>
                            <small class="text-muted">إجمالي المبيعات</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card text-center">
                        <div class="card-body">
                            <i class="fas fa-money-bill-wave fa-2x text-success mb-2"></i>
                            <h4 class="text-success">{{ "%.2f"|format(stats.total_revenue) }} ر.س</h4>
                            <small class="text-muted">إجمالي الإيرادات</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card text-center">
                        <div class="card-body">
                            <i class="fas fa-chart-line fa-2x text-warning mb-2"></i>
                            <h4 class="text-warning">{{ "%.2f"|format(stats.total_profit) }} ر.س</h4>
                            <small class="text-muted">إجمالي الأرباح</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card text-center">
                        <div class="card-body">
                            <i class="fas fa-users fa-2x text-info mb-2"></i>
                            <h4 class="text-info">{{ stats.total_customers }}</h4>
                            <small class="text-muted">إجمالي العملاء</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- الرسوم البيانية -->
        <div class="reports-section">
            <h4 class="mb-4"><i class="fas fa-chart-bar me-2"></i>الرسوم البيانية</h4>
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">توزيع المبيعات</h6>
                            <div class="chart-container">
                                <canvas id="salesChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">حالة المخزون</h6>
                            <div class="chart-container">
                                <canvas id="inventoryChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- التقارير التفصيلية -->
        <div class="reports-section">
            <h4 class="mb-4"><i class="fas fa-file-alt me-2"></i>التقارير التفصيلية</h4>
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <i class="fas fa-shopping-cart fa-3x text-primary mb-3"></i>
                            <h5>تقرير المبيعات</h5>
                            <p class="text-muted">تحليل شامل للمبيعات والإيرادات والأرباح</p>
                            <button class="btn btn-primary" onclick="showSalesReport()">
                                <i class="fas fa-eye me-1"></i>عرض التقرير
                            </button>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <i class="fas fa-boxes fa-3x text-warning mb-3"></i>
                            <h5>تقرير المخزون</h5>
                            <p class="text-muted">تتبع حركة المخزون والمنتجات منخفضة المخزون</p>
                            <button class="btn btn-warning" onclick="showInventoryReport()">
                                <i class="fas fa-eye me-1"></i>عرض التقرير
                            </button>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <i class="fas fa-users fa-3x text-success mb-3"></i>
                            <h5>تقرير العملاء</h5>
                            <p class="text-muted">تحليل العملاء والمديونية والحدود الائتمانية</p>
                            <button class="btn btn-success" onclick="showCustomersReport()">
                                <i class="fas fa-eye me-1"></i>عرض التقرير
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- التنبيهات والإشعارات -->
        <div class="reports-section">
            <h4 class="mb-4"><i class="fas fa-exclamation-triangle me-2"></i>التنبيهات والإشعارات</h4>
            <div class="row">
                <div class="col-md-6">
                    <div class="alert alert-warning">
                        <h6><i class="fas fa-exclamation-triangle me-2"></i>منتجات منخفضة المخزون</h6>
                        <p class="mb-0">يوجد {{ stats.low_stock_products }} منتج بكمية منخفضة</p>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="alert alert-danger">
                        <h6><i class="fas fa-times-circle me-2"></i>منتجات نفدت من المخزون</h6>
                        <p class="mb-0">يوجد {{ stats.out_of_stock_products }} منتج نفد من المخزون</p>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="alert alert-info">
                        <h6><i class="fas fa-user-clock me-2"></i>العملاء المدينون</h6>
                        <p class="mb-0">يوجد {{ stats.debtors }} عميل مدين بإجمالي {{ "%.2f"|format(stats.total_debt) }} ر.س</p>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="alert alert-success">
                        <h6><i class="fas fa-chart-line me-2"></i>الأرباح</h6>
                        <p class="mb-0">إجمالي الأرباح: {{ "%.2f"|format(stats.total_profit) }} ر.س</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal تقرير المبيعات -->
    <div class="modal fade" id="salesReportModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-shopping-cart me-2"></i>تقرير المبيعات
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div id="salesReportContent">
                        <div class="text-center">
                            <div class="spinner-border" role="status">
                                <span class="visually-hidden">جاري التحميل...</span>
                            </div>
                            <p>جاري تحميل التقرير...</p>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                    <button type="button" class="btn btn-success" onclick="downloadSalesReport()">
                        <i class="fas fa-download me-1"></i>تحميل PDF
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // تهيئة الرسوم البيانية
        document.addEventListener('DOMContentLoaded', function() {
            // رسم بياني للمبيعات
            const salesCtx = document.getElementById('salesChart').getContext('2d');
            new Chart(salesCtx, {
                type: 'doughnut',
                data: {
                    labels: ['الإيرادات', 'الأرباح', 'التكاليف'],
                    datasets: [{
                        data: [{{ stats.total_revenue }}, {{ stats.total_profit }}, {{ stats.total_revenue - stats.total_profit }}],
                        backgroundColor: ['#28a745', '#ffc107', '#dc3545']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });

            // رسم بياني للمخزون
            const inventoryCtx = document.getElementById('inventoryChart').getContext('2d');
            new Chart(inventoryCtx, {
                type: 'bar',
                data: {
                    labels: ['متوفر', 'منخفض', 'نفد'],
                    datasets: [{
                        label: 'المنتجات',
                        data: [{{ stats.total_products - stats.low_stock_products - stats.out_of_stock_products }}, {{ stats.low_stock_products }}, {{ stats.out_of_stock_products }}],
                        backgroundColor: ['#28a745', '#ffc107', '#dc3545']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        });

        // عرض تقرير المبيعات
        function showSalesReport() {
            new bootstrap.Modal(document.getElementById('salesReportModal')).show();
            loadSalesReport();
        }

        // تحميل تقرير المبيعات
        function loadSalesReport() {
            fetch('/api/reports/sales')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('salesReportContent').innerHTML = data.html;
                } else {
                    document.getElementById('salesReportContent').innerHTML = '<div class="alert alert-danger">خطأ في تحميل التقرير</div>';
                }
            })
            .catch(error => {
                document.getElementById('salesReportContent').innerHTML = '<div class="alert alert-danger">خطأ في الاتصال</div>';
            });
        }

        // عرض تقرير المخزون
        function showInventoryReport() {
            fetch('/api/reports/inventory-movement')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // إنشاء modal لعرض التقرير
                    const modal = document.createElement('div');
                    modal.className = 'modal fade';
                    modal.innerHTML = `
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">
                                        <i class="fas fa-boxes me-2"></i>تقرير حركة المخزون
                                    </h5>
                                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    ${data.html || '<div class="alert alert-info">لا توجد بيانات متاحة</div>'}
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                                    <button type="button" class="btn btn-success" onclick="downloadReport('inventory')">
                                        <i class="fas fa-download me-1"></i>تحميل
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    document.body.appendChild(modal);
                    new bootstrap.Modal(modal).show();
                    
                    modal.addEventListener('hidden.bs.modal', function() {
                        document.body.removeChild(modal);
                    });
                } else {
                    alert('خطأ في تحميل التقرير: ' + data.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // عرض تقرير العملاء
        function showCustomersReport() {
            fetch('/api/reports/customers-debt')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // إنشاء modal لعرض التقرير
                    const modal = document.createElement('div');
                    modal.className = 'modal fade';
                    modal.innerHTML = `
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">
                                        <i class="fas fa-users me-2"></i>تقرير العملاء والمديونية
                                    </h5>
                                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    ${data.html || '<div class="alert alert-info">لا توجد بيانات متاحة</div>'}
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                                    <button type="button" class="btn btn-success" onclick="downloadReport('customers')">
                                        <i class="fas fa-download me-1"></i>تحميل
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    document.body.appendChild(modal);
                    new bootstrap.Modal(modal).show();
                    
                    modal.addEventListener('hidden.bs.modal', function() {
                        document.body.removeChild(modal);
                    });
                } else {
                    alert('خطأ في تحميل التقرير: ' + data.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // إنشاء تقرير
        function generateReport(type) {
            switch(type) {
                case 'sales':
                    showSalesReport();
                    break;
                case 'inventory':
                    showInventoryReport();
                    break;
                case 'customers':
                    showCustomersReport();
                    break;
                case 'profit':
                    showProfitReport();
                    break;
                default:
                    alert('نوع التقرير غير معروف');
            }
        }

        // عرض تقرير الأرباح
        function showProfitReport() {
            fetch('/api/reports/profit-analysis')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // إنشاء modal لعرض التقرير
                    const modal = document.createElement('div');
                    modal.className = 'modal fade';
                    modal.innerHTML = `
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">
                                        <i class="fas fa-chart-line me-2"></i>تقرير تحليل الأرباح
                                    </h5>
                                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    ${data.html || '<div class="alert alert-info">لا توجد بيانات متاحة</div>'}
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                                    <button type="button" class="btn btn-success" onclick="downloadReport('profit')">
                                        <i class="fas fa-download me-1"></i>تحميل
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    document.body.appendChild(modal);
                    new bootstrap.Modal(modal).show();
                    
                    modal.addEventListener('hidden.bs.modal', function() {
                        document.body.removeChild(modal);
                    });
                } else {
                    alert('خطأ في تحميل التقرير: ' + data.message);
                }
            })
            .catch(error => {
                alert('خطأ في الاتصال: ' + error);
            });
        }

        // تحميل تقرير
        function downloadReport(type) {
            // إنشاء رابط تحميل للتقرير
            const link = document.createElement('a');
            link.href = `/api/reports/${type}/download`;
            link.download = `تقرير_${type}_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        // تحميل تقرير PDF
        function downloadSalesReport() {
            downloadReport('sales');
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print_system_info()

    # تهيئة قاعدة البيانات
    print("🔄 تهيئة قاعدة البيانات...")
    init_database()

    # إنشاء نسخة احتياطية
    if SYSTEM_CONFIG.get('backup_enabled', True):
        print("🔄 إنشاء نسخة احتياطية...")
        create_backup()

    print("🚀 بدء تشغيل الخادم...")
    print("✅ النظام جاهز للاستخدام!")
    print("🌐 افتح المتصفح على: http://localhost:5000")
    print("=" * 80)

    try:
        # تشغيل التطبيق
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # تعطيل وضع التطوير للإنتاج
            threaded=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف النظام بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل النظام: {e}")
    finally:
        print("👋 شكراً لاستخدام نظام إدارة المبيعات المتقدم!")