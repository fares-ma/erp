<div align="center">
  <img src="./erpnext/public/images/v16/erpnext.svg" alt="ERPNext Logo" height="80" width="80" />
  <h1>نظام إدارة موارد المؤسسة (ERPNext)</h1>
  <p>بيئة العمل الكاملة لتشغيل وتخصيص وتجربة <strong>ERPNext v16</strong> محلياً عبر Docker مع سكريبتات البيانات التجريبية وأدلة التحليل والتنفيذ.</p>
</div>

---

## نبذة عن المشروع

يضم هذا المستودع بيئة متكاملة لتشغيل نظام **ERPNext** محلياً وتجهيزه للعرض أو التحليل والتنفيذ الفعلي، ويشمل:

- **نواة النظام (`erpnext/`):** الكود المصدري لـ ERPNext مع واجهات `islands/` وتطبيق/ملفات `banking/`.
- **بيئة التشغيل الجاهزة (`frappe_docker/`):** ملفات Docker Compose لتشغيل الموقع وقاعدة البيانات وRedis محلياً بدون إعداد يدوي معقد.
- **سكريبتات تشغيل سريعة لنظام ويندوز:** لتشغيل Docker Desktop وسحب الصور وتشغيل الحاويات والتحقق من جاهزية الموقع تلقائياً.
- **سكريبتات تعبئة البيانات التجريبية (`Seed Data`):** لإنشاء دورات عمل كاملة جاهزة للعرض أو لاختبار دورة تصنيع مصنع أجهزة منزلية (بوتاجازات وثلاجات).
- **أدلة عمل عربية متكاملة:** شرح أقسام النظام من منظور الأعمال، وخارطة التحليل والتنفيذ لمصانع الأجهزة المنزلية.

---

## محتويات المستودع (هيكل المشروع)

| الملف / المجلد | الوصف |
| :--- | :--- |
| [`start-erpnext.ps1`](./start-erpnext.ps1) | سكريبت PowerShell لتشغيل Docker Desktop وسحب الصور وبدء الحاويات والتحقق من `http://localhost:8080`. |
| [`run-erpnext-window.cmd`](./run-erpnext-window.cmd) | ملف تشغيل سريع لنظام ويندوز يفتح نافذة PowerShell لتنفيذ `start-erpnext.ps1`. |
| [`frappe_docker/pwd.yml`](./frappe_docker/pwd.yml) | ملف `Docker Compose` المحلي لتشغيل خدمات ERPNext (`backend`, `frontend`, `db`, `redis`, `websocket`, وغيرها). |
| [`seed_demo_data.py`](./seed_demo_data.py) | سكريبت إنشاء بيانات تجريبية عامة (موردون، عملاء، أصناف، دورة بيع وشراء، مدفوعات، CRM، ومشروع ومهام). |
| [`seed_appliance_factory.py`](./seed_appliance_factory.py) | سكريبت محاكاة دورة تصنيع كاملة لمصنع بوتاجازات وثلاجات (مخازن، قوائم مواد BOM، أوامر تشغيل، هالك، تسليم بالسيريال، وضمان). |
| [`SYSTEM_OVERVIEW.md`](./SYSTEM_OVERVIEW.md) | الدليل التعريفي الشامل لأقسام ووحدات النظام الـ 12 ورحلات العمل المتكاملة باللغة العربية. |
| [`FACTORY_DISCOVERY_CHECKLIST.md`](./FACTORY_DISCOVERY_CHECKLIST.md) | دليل التحليل (`Discovery Checklist`) ومصفوفة التعديلات وخطة التنفيذ لمصنع البوتاجازات والثلاجات. |
| `erpnext/` / `banking/` / `islands/` | الكود المصدري الأساسي لوحدات ERPNext وواجهات المشاريع والربط البنكي. |

---

## المتطلبات الأساسية

- [Docker Desktop](https://docs.docker.com/get-docker/) (مع **Docker Compose v2**).
- [Git](https://git-scm.com/).

---

## التشغيل السريع

### الطريقة الأولى: عبر سكريبت ويندوز (موصى بها على Windows)

من داخل مجلد المشروع، شغّل الأمر التالي في PowerShell:

```powershell
.\start-erpnext.ps1
```

يقوم السكريبت تلقائياً بالآتي:
1. التحقق من تشغيل Docker (وتشغيل Docker Desktop تلقائياً إذا لم يكن يعمل).
2. سحب الصور المطلوبة (`redis:6.2-alpine`، `mariadb:11.8`، `frappe/erpnext:v16.60.0`) عند الحاجة.
3. تشغيل الحاويات عبر `frappe_docker/pwd.yml`.
4. متابعة سجلات إنشاء الموقع (`create-site`) والتحقق من استجابة الرابط `http://localhost:8080/api/method/ping`.

> **ملاحظة:** في حال استخدام [`run-erpnext-window.cmd`](./run-erpnext-window.cmd) بعد نسخ المستودع لمسار جديد، حدّث مسار `start-erpnext.ps1` داخل الملف إذا اختلف عن المسار الافتراضي.

### الطريقة الثانية: يدوياً عبر Docker Compose

```sh
cd frappe_docker
docker compose -f pwd.yml up -d
docker compose -f pwd.yml logs -f create-site
```

> يستغرق إنشاء الموقع في المرة الأولى (`create-site`) عادةً من **2 إلى 5 دقائق** قبل أن تصبح الواجهة متاحة.

### بيانات الدخول الافتراضية للبيئة المحلية

| البند | القيمة |
| :--- | :--- |
| **الرابط المحلي** | `http://localhost:8080` |
| **اسم الموقع (`Site`)** | `frontend` |
| **اسم المستخدم** | `Administrator` |
| **كلمة المرور** | `admin` |
| **صور Docker المستخدمة** | `frappe/erpnext:v16.60.0` · `mariadb:11.8` · `redis:6.2-alpine` |

---

## تشغيل سكريبتات البيانات التجريبية (Seed Data)

بعد تشغيل النظام وإتمام معالج الإعداد الأولي (`Setup Wizard`) للشركة، يمكنك تعبئة الموقع ببيانات جاهزة عبر نسخ السكريبت داخل حاوية `backend` وتنفيذه بمفسّر بايثون الخاص بـ Bench.

> **ملاحظة مهمة:** السكريبتان مضبوطان افتراضياً على القيم:
> `SITE = "frontend"` · `COMPANY = "Fares-Test-company"` · `CURRENCY = "EGP"`
> تأكد من إنشاء هذه الشركة أثناء الـ Setup Wizard، أو عدّل الثوابت في أعلى السكريبت قبل تشغيله لتطابق اسم شركتك وعملتك.

### 1. البيانات التجريبية العامة (`seed_demo_data.py`)

ينشئ موردين وعملاء وأصنافاً، وعروض أسعار وأوامر بيع وشراء، وفواتير وسندات قبض وصرف، وعملاء محتملين (`Leads`)، ومشروعاً مع مهام مرتبطة.

```powershell
docker compose -f frappe_docker/pwd.yml cp seed_demo_data.py backend:/tmp/seed_demo_data.py
docker compose -f frappe_docker/pwd.yml exec backend /home/frappe/frappe-bench/env/bin/python /tmp/seed_demo_data.py
```

### 2. نموذج مصنع الأجهزة المنزلية (`seed_appliance_factory.py`)

ينشئ دورة تصنيع كاملة لمصنع بوتاجازات وثلاجات: مخازن (`Raw Materials`, `Work In Progress`, `Finished Goods`, `Scrap Warehouse`)، قوائم مواد متعددة المستويات (`BOM`)، أوامر تصنيع (`Work Orders`) مكتملة وقيد التشغيل، قيد هالك الصاج (`Scrap`)، وتسليم للتجار بالأرقام التسلسلية (`Serial No`) مع تفعيل الضمان وفاتورة المبيعات.

```powershell
docker compose -f frappe_docker/pwd.yml cp seed_appliance_factory.py backend:/tmp/seed_appliance_factory.py
docker compose -f frappe_docker/pwd.yml exec backend /home/frappe/frappe-bench/env/bin/python /tmp/seed_appliance_factory.py
```

---

## أوامر إدارة Docker المفيدة

تُنفَّذ هذه الأوامر من داخل مجلد `frappe_docker` (أو بإضافة `-f frappe_docker/pwd.yml` من جذر المشروع):

```sh
# عرض حالة الحاويات
docker compose -f pwd.yml ps

# متابعة السجلات الحية
docker compose -f pwd.yml logs -f backend

# إيقاف الحاويات مؤقتاً مع الاحتفاظ بالبيانات
docker compose -f pwd.yml stop

# إيقاف وإزالة الحاويات فقط (تبقى قاعدة البيانات والملفات)
docker compose -f pwd.yml down
```

> ⚠️ **تحذير:** تشغيل `docker compose -f pwd.yml down -v` يحذف الـ Volumes بالكامل بما فيها قاعدة بيانات MariaDB وملفات الموقع.

---

## التوثيق والأدلة المرفقة

- **[SYSTEM_OVERVIEW.md](./SYSTEM_OVERVIEW.md):** الدليل التعريفي الشامل لنظام ERPNext؛ يوضح الهيكل العام، القطاعات المدعومة، خريطة ترابط الأقسام الـ 12، وأهم العمليات والتقارير ومؤشرات الأداء لكل إدارة.
- **[FACTORY_DISCOVERY_CHECKLIST.md](./FACTORY_DISCOVERY_CHECKLIST.md):** خارطة التحليل والتنفيذ لمصنع بوتاجازات وثلاجات؛ تتضمن قائمة أسئلة الـ Discovery مع العميل، مصفوفة اختيار أداة التعديل المناسبة، وخطة التنفيذ على 4 مراحل.

---

## ملاحظة مهمة للتخصيص والتطوير

> [!IMPORTANT]
> **لا تعدّل ملفات نواة `erpnext/` مباشرة.**
> عند تنفيذ متطلبات إضافية للعملاء، استخدم الأدوات الرسمية لضمان استقرار الحسابات وسهولة التحديث مستقبلاً:
> - **تخصيص الشاشات والحقول:** `Workspaces` و`Customize Form` و`Custom Field`
> - **المستندات والطباعة:** `Print Format` (HTML/Jinja)
> - **الاعتمادات والأتمتة:** `Workflow` و`Client Script` و`Server Script`
> - **التكاملات الخارجية والمنطق المتقدم:** إنشاء **`Custom Frappe App`** منفصل (كما هو موضح في [مصفوفة التعديلات](./FACTORY_DISCOVERY_CHECKLIST.md)).
