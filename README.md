<div align="center">
  <h1>Digitbox Manufacturing ERP</h1>
  <p><strong>حل متكامل لتخطيط موارد المصانع والشركات الصناعية</strong> — مُعدّ ومُخصّص ومُسلّم بواسطة شركة <a href="https://digitbox.tech"><strong>Digitbox</strong></a></p>
  <p>مبني على منصة <strong>ERPNext v16</strong> مفتوحة المصدر بترخيص <code>GNU GPL v3</code></p>

  <p>
    <a href="https://digitbox.tech"><img src="https://img.shields.io/badge/Delivered%20by-Digitbox-0F172A?style=flat-square" alt="Delivered by Digitbox" /></a>
    <a href="https://github.com/frappe/erpnext"><img src="https://img.shields.io/badge/Powered%20by-ERPNext%20v16-0089FF?style=flat-square" alt="Powered by ERPNext v16" /></a>
    <a href="./license.txt"><img src="https://img.shields.io/badge/License-GNU%20GPL%20v3-green?style=flat-square" alt="License GNU GPL v3" /></a>
    <a href="./frappe_docker/pwd.yml"><img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square" alt="Docker Ready" /></a>
  </p>
</div>

---

## نبذة عن الحل ودور شركة Digitbox

يمثّل هذا المستودع حزمة التشغيل والتسليم الخاصة بشركة **[Digitbox](https://digitbox.tech)** لتطبيق نظام تخطيط موارد المؤسسة (**ERP**) في قطاع المصانع (وعلى وجه الخصوص مصانع الأجهزة المنزلية والقطاعات الصناعية والتجارية المرتبطة بها).

تعتمد فلسفة التسليم في **Digitbox** على الشفافية الكاملة واستقلالية العميل عبر طبقتين متكاملتين:

1. **القيمة المضافة والتسليم من شركة Digitbox:**
   - تجهيز بيئة تشغيل محلية فورية عبر Docker (`frappe_docker/pwd.yml`) وسكريبتات تشغيل مخصصة لويندوز.
   - بناء نماذج محاكاة عملية جاهزة للتجربة والعرض (`Seed Data`)، تشمل دورة تصنيع كاملة لمصنع بوتاجازات وثلاجات (المخازن، قوائم المواد متعددة المستويات `BOM`، أوامر التشغيل، الهالك، الأرقام التسلسلية، والضمان).
   - توفير أدلة تحليل وتنفيذ عربية شاملة تُستخدم في جلسات جمع المتطلبات (`Discovery`) وتدريب فرق العمل والتسليم الرسمي.
   - التخصيص الهندسي والمحاسبي، والربط مع الأنظمة الخارجية (مثل الفاتورة الإلكترونية أو خطوط الإنتاج)، والدعم الفني وفق منهجية تحافظ على استقرار النظام وقابليته للتحديث.

2. **النواة مفتوحة المصدر (`Powered by ERPNext & Frappe`):**
   - يرتكز النظام على منصة **ERPNext v16** وإطار العمل **Frappe Framework** الموزّعَين بموجب رخصة البرمجيات الحرة **`GNU GPL v3`**.
   - تمنح هذه البنية العميل حرية كاملة دون احتكار (`No Vendor Lock-in`)، مع امتلاك الكود المصدري وقابلية التوسع والترقية المستمرة.

---

## محتويات المستودع (هيكل المشروع)

### أولاً: تجهيزات وأدوات شركة Digitbox

| الملف / المجلد | الوصف |
| :--- | :--- |
| [`start-erpnext.ps1`](./start-erpnext.ps1) | سكريبت PowerShell لتشغيل Docker Desktop وسحب الصور وبدء الحاويات والتحقق من جاهزية الموقع على `http://localhost:8080`. |
| [`run-erpnext-window.cmd`](./run-erpnext-window.cmd) | ملف تشغيل سريع لنظام ويندوز يفتح نافذة PowerShell لتنفيذ `start-erpnext.ps1`. |
| [`frappe_docker/pwd.yml`](./frappe_docker/pwd.yml) | إعداد Docker Compose المجهّز للتشغيل المحلي (`backend`, `frontend`, `db`, `redis`, `websocket`, وغيرها). |
| [`seed_demo_data.py`](./seed_demo_data.py) | سكريبت تعبئة بيانات تجريبية عامة (موردون، عملاء، أصناف، دورة بيع وشراء، مدفوعات، CRM، ومشروع ومهام). |
| [`seed_appliance_factory.py`](./seed_appliance_factory.py) | سكريبت محاكاة دورة تصنيع كاملة لمصنع بوتاجازات وثلاجات (مخازن الخامات/WIP/المنتج التام/الهالك، `BOM`، أوامر تشغيل، تسليم بالسيريال، وضمان). |
| [`SYSTEM_OVERVIEW.md`](./SYSTEM_OVERVIEW.md) | الدليل التعريفي الشامل لوحدات النظام الـ 12 ورحلات العمل المتكاملة باللغة العربية. |
| [`FACTORY_DISCOVERY_CHECKLIST.md`](./FACTORY_DISCOVERY_CHECKLIST.md) | دليل التحليل (`Discovery Checklist`) ومصفوفة التعديلات وخطة التنفيذ المرحلية لمصنع البوتاجازات والثلاجات. |

### ثانياً: النواة مفتوحة المصدر

| المجلد | الوصف |
| :--- | :--- |
| `erpnext/` | الكود المصدري الأساسي لتطبيق ERPNext v16 مفتوح المصدر (المحاسبة، المخازن، المشتريات، المبيعات، التصنيع، الجودة، الأصول، المشاريع، والدعم). |
| `banking/` & `islands/` | مكونات وواجهات التكامل البنكي ولوحات متابعة المشاريع المضمنة في الحزمة. |

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

- **[SYSTEM_OVERVIEW.md](./SYSTEM_OVERVIEW.md):** الدليل التعريفي الشامل لنظام ERP؛ يوضح الهيكل العام، القطاعات المدعومة، خريطة ترابط الأقسام الـ 12، وأهم العمليات والتقارير ومؤشرات الأداء لكل إدارة.
- **[FACTORY_DISCOVERY_CHECKLIST.md](./FACTORY_DISCOVERY_CHECKLIST.md):** خارطة التحليل والتنفيذ لمصنع بوتاجازات وثلاجات؛ تتضمن قائمة أسئلة الـ Discovery مع العميل، مصفوفة اختيار أداة التعديل المناسبة، وخطة التنفيذ على 4 مراحل.

---

## منهجية Digitbox في التخصيص والتطوير

> [!IMPORTANT]
> **لا تعدّل ملفات نواة `erpnext/` مباشرة.**
> عند تنفيذ متطلبات إضافية للمصانع أو العملاء، تتبع **Digitbox** الأدوات الرسمية لضمان استقرار الحسابات وسهولة التحديث والترقية مستقبلاً:
> - **تخصيص الشاشات والحقول:** `Workspaces` و`Customize Form` و`Custom Field`
> - **المستندات والطباعة:** `Print Format` (HTML/Jinja)
> - **الاعتمادات والأتمتة:** `Workflow` و`Client Script` و`Server Script`
> - **التكاملات الخارجية والمنطق المتقدم:** إنشاء **`Custom Frappe App`** منفصل (كما هو موضح في [مصفوفة التعديلات](./FACTORY_DISCOVERY_CHECKLIST.md)).

---

## الترخيص والإسناد مفتوح المصدر (License & Attribution)

- يعتمد هذا الحل على نظام **[ERPNext](https://github.com/frappe/erpnext)** وإطار العمل **[Frappe Framework](https://github.com/frappe/frappe)**، وكلاهما برمجيات مفتوحة المصدر مرخّصة بموجب رخصة **`GNU General Public License v3.0 (GPL-3.0)`** (انظر [`license.txt`](./license.txt) و[`attributions.md`](./attributions.md)).
- اسم **ERPNext** وشعاره هما علامتان تجاريتان مسجلتان لشركة **Frappe Technologies Pvt. Ltd.** (انظر [`TRADEMARK_POLICY.md`](./TRADEMARK_POLICY.md)).
- شركة **Digitbox** ([digitbox.tech](https://digitbox.tech)) هي شركة تنفيذ وتخصيص وتسليم مستقلة، ويُذكر اسم **ERPNext** هنا للإشارة إلى المنصة مفتوحة المصدر التي يقوم عليها النظام دون أي ادعاء بالملكية الحصرية للنواة أو بالارتباط الرسمي بشركة Frappe Technologies.

---

<div align="center">
  <p>تم التجهيز والتوثيق للتسليم بواسطة <strong>Digitbox</strong> · <a href="https://digitbox.tech">digitbox.tech</a></p>
</div>
