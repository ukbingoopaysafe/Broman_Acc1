# دليل النشر السريع - نظام BroMan

## التثبيت السريع (5 دقائق)

### 1. تحميل المشروع
```bash
git clone https://github.com/ukbingoopaysafe/Broman_Acc1.git
cd Broman_Acc1
```

### 2. إنشاء البيئة الافتراضية
```bash
python -m venv broman_env

# Windows
broman_env\Scripts\activate

# Linux/Mac
source broman_env/bin/activate
```

### 3. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 4. إعداد قاعدة البيانات
```bash
python src/utils/init_data.py
```

### 5. تشغيل النظام
```bash
python src/main.py
```

### 6. الوصول إلى النظام
- افتح المتصفح واذهب إلى: `http://localhost:5000`
- اسم المستخدم: `admin`
- كلمة المرور: `admin123`

## للوصول من أجهزة أخرى في الشبكة
- استبدل `localhost` بعنوان IP للخادم
- مثال: `http://192.168.1.100:5000`

## ملاحظات مهمة
- غيّر كلمة مرور المدير فور تسجيل الدخول الأول
- تأكد من عمل نسخ احتياطية دورية لملف `broman.db`
- راجع الوثائق الكاملة في مجلد `docs/`

## الدعم الفني
للمساعدة، راجع:
- [دليل المستخدم](docs/user_manual.md)
- [دليل حل المشاكل](docs/troubleshooting_guide.md)
- [دليل التثبيت المفصل](docs/installation_guide.md)

