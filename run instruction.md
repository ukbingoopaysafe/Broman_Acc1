### خطوات تشغيل مشروع Broman_Acc1 على ويندوز

- **المتطلبات**
  - وجود Python مثبت (المشروع يحتوي بيئة افتراضية جاهزة `broman_env`).
  - PowerShell بامتيازات تسمح بتشغيل السكربتات.

### 1) فتح المشروع
- افتح PowerShell على المسار:
```powershell
cd E:\Projects\Broman_Acc1
```

### 2) تفعيل البيئة الافتراضية الجاهزة
```powershell
.\broman_env\Scripts\Activate.ps1
```
- ستلاحظ اسم البيئة يظهر في بداية السطر (مثال: `(broman_env)`).

### 3) تثبيت الاعتماديات (إن لزم)
```powershell
pip install -r requirements.txt
```

### 4) تهيئة قاعدة البيانات (اختياري عند أول مرة)
- قاعدة بيانات SQLite موجودة في `src\database\broman_accounting.db`.  
- إن أردت تعبئة بيانات مبدئية:
```powershell
python .\src\utils\init_data.py
```

### 5) تشغيل الخادم
اختر أحد الطريقتين:

- الطريقة A: تشغيل مباشرة عبر Python (غالباً تعمل دون إعداد متغيرات بيئة):
```powershell
python .\src\main.py
```

- الطريقة B: عبر Flask CLI:
```powershell
$env:FLASK_APP = "src.main"
$env:FLASK_ENV = "development"   # اختياري للتصحيح
flask run --debug
```

### 6) الوصول للتطبيق
- افتح المتصفح على:
`http://127.0.0.1:5000`

### 7) الإيقاف والسجلات
- إيقاف الخادم: Ctrl+C في PowerShell.
- السجلات:
  - أخطاء: `tmp\server.err.log`
  - تشغيل: `tmp\server.log`

### مشاكل شائعة وحلول سريعة
- **Activate.ps1 محظور**: فعّل التنفيذ مؤقتاً ثم أعد تفعيل البيئة.
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\broman_env\Scripts\Activate.ps1
```
- **منفذ 5000 مشغول**: شغّل على منفذ آخر.
```powershell
flask run --debug --port 5050
```
- **مكتبات ناقصة**: أعد تثبيت الاعتماديات داخل البيئة المفعلة.
```powershell
pip install -r requirements.txt
```

- **لا يتم التعرف على FLASK_APP**: استخدم الطريقة A (`python src\main.py`) أو تأكد أن قيمة `FLASK_APP` هي `src.main`.

- **حروف غير مفهومة في الطرفية**: استخدم PowerShell بدل CMD وتأكد الترميز UTF-8:
```powershell
chcp 65001 | Out-Null
```

إذا أردت، أقدر أشغل لك الأوامر تلقائياً خطوة بخطوة من هنا.