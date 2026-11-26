<div align="center">
  <h1>Digitbox Manufacturing ERP</h1>
  <p><strong>منصة متكاملة لتخطيط موارد المصانع والشركات الصناعية والتجارية</strong> — مُعدّة ومُخصّصة ومُسلّمة بواسطة شركة <a href="https://digitbox.tech"><strong>Digitbox</strong></a></p>
  <p>مبنية على نواة <strong>ERPNext v16</strong> و<strong>Frappe Framework</strong> مفتوحة المصدر بترخيص <code>GNU GPL v3</code> · جاهزة للتشغيل الفوري على أي جهاز Windows أو سيرفر Linux عبر Docker</p>

  <p>
    <a href="https://digitbox.tech"><img src="https://img.shields.io/badge/Delivered%20by-Digitbox-0F172A?style=flat-square" alt="Delivered by Digitbox" /></a>
    <a href="https://github.com/frappe/erpnext"><img src="https://img.shields.io/badge/Powered%20by-ERPNext%20v16-0089FF?style=flat-square" alt="Powered by ERPNext v16" /></a>
    <a href="./license.txt"><img src="https://img.shields.io/badge/License-GNU%20GPL%20v3-green?style=flat-square" alt="License GNU GPL v3" /></a>
    <a href="./frappe_docker/pwd.yml"><img src="https://img.shields.io/badge/Docker-Compose%20Ready-2496ED?style=flat-square" alt="Docker Compose Ready" /></a>
    <a href="#دليل-التشغيل-خطوة-بخطوة-على-أي-جهاز-أو-سيرفر"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20Server-64748B?style=flat-square" alt="Windows and Linux Server Ready" /></a>
  </p>
</div>

---

## فهرس المحتويات

1. [نبذة عن الحل ودور شركة Digitbox](#نبذة-عن-الحل-ودور-شركة-digitbox)
2. [المميزات والوحدات الأساسية للنظام](#المميزات-والوحدات-الأساسية-للنظام)
3. [هيكل المشروع ومحتويات المستودع](#هيكل-المشروع-ومحتويات-المستودع)
4. [روابط التحميل والمتطلبات الأساسية](#روابط-التحميل-والمتطلبات-الأساسية)
5. [دليل التشغيل خطوة بخطوة على أي جهاز أو سيرفر](#دليل-التشغيل-خطوة-بخطوة-على-أي-جهاز-أو-سيرفر)
6. [بيانات الدخول وحسابات المستخدمين الجاهزة للتجربة](#بيانات-الدخول-وحسابات-المستخدمين-الجاهزة-للتجربة)
7. [تشغيل سكريبتات البيانات التجريبية (Seed Data)](#تشغيل-سكريبتات-البيانات-التجريبية-seed-data)
8. [إدارة السيرفر والنسخ الاحتياطي وحل المشاكل الشائعة](#إدارة-السيرفر-والنسخ-الاحتياطي-وحل-المشاكل-الشائعة)
9. [بيئة التطوير المحلية بدون Docker (Frappe Bench)](#بيئة-التطوير-المحلية-بدون-docker-frappe-bench)
10. [الوثائق والمراجع الرسمية الأصلية](#الوثائق-والمراجع-الرسمية-الأصلية)
11. [منهجية Digitbox في التخصيص والتطوير](#منهجية-digitbox-في-التخصيص-والتطوير)
12. [الترخيص والإسناد مفتوح المصدر (License & Attribution)](#الترخيص-والإسناد-مفتوح-المصدر-license--attribution)

---

## نبذة عن الحل ودور شركة Digitbox

يمثّل هذا المستودع حزمة التشغيل والتسليم المتكاملة من شركة **[Digitbox](https://digitbox.tech)** لتطبيق وتشغيل نظام تخطيط موارد المؤسسة (**ERP**) للشركات الصناعية والمصانع (مع نموذج عملي متكامل لمصانع الأجهزة المنزلية: البوتاجازات والثلاجات).

تعتمد منهجية **Digitbox** في التسليم على مبدأ **الشفافية الكاملة واستقلالية العميل** عبر طبقتين متكاملتين:

1. **القيمة المضافة والتسليم من شركة Digitbox:**
   - **قابلية النقل والتشغيل الفوري (`Clone & Run`):** يعمل المشروع مباشرة بعد عمل `git clone` على أي جهاز **Windows** أو سيرفر **Linux / Ubuntu VPS** دون تعديل يدوي للمسارات.
   - **بيئة Docker متكاملة (`frappe_docker/pwd.yml`):** تضم قاعدة بيانات MariaDB وRedis والخادم الخلفي وNginx وWorkers، مع دعم تغيير البورت عبر `ERPNEXT_PORT`.
   - **سكريبتات تعبئة بيانات ذكية ومستقلة (`Seed Data`):** تقوم تلقائياً بإكمال معالج الإعداد الأولي إذا كان الموقع جديداً تماماً، أو التكيّف مع الشركة الموجودة، لإنشاء دورة مبيعات ومشتريات وتصنيع ومستخدمين وصلاحيات كاملة خلال ثوانٍ.
   - **أدلة تحليل وتسليم عربية:** توثيق شامل لوحدات النظام وخارطة التنفيذ وجلسات الـ `Discovery` مع العميل.
   - **التخصيص والتكامل والدعم:** ربط الفاتورة الإلكترونية، التقارير، الصلاحيات، والتدريب وفق أفضل ممارسات Frappe.

2. **النواة مفتوحة المصدر (`Powered by ERPNext v16 & Frappe`):**
   - مبني على منصة **ERPNext v16** وإطار العمل **Frappe Framework** بترخيص **`GNU GPL v3`**.
   - يضمن للعميل امتلاك بياناته ونظامه بالكامل دون أي احتكار (`No Vendor Lock-in`) مع مجتمع عالمي وتحديثات مستمرة.

---

## المميزات والوحدات الأساسية للنظام

- **الإدارة المالية والمحاسبة (`Accounting`):** شجرة حسابات مرنة، قيود آلية، مراكز تكلفة، أبعاد تحليلية، إدارة البنوك والشيكات، مطابقة بنكية، ضرائب، وميزانيات وقوائم مالية وفق `IFRS`.
- **المبيعات والمشتريات وإدارة الطلبات (`Order Management`):** عروض أسعار، أوامر بيع وشراء، فواتير، إدارة ائتمان العملاء، مقارنة الموردين، وتكاليف الاستيراد (`Landed Cost`).
- **التصنيع والتصنيع لدى الغير (`Manufacturing`):** قوائم مواد متعددة المستويات (`BOM`)، محطات عمل وعمليات (`Workstations & Operations`)، تخطيط الإنتاج (`MRP`)، أوامر تشغيل (`Work Orders`)، بطاقات عمل (`Job Cards`)، وتتبع الهالك (`Scrap`).
- **المخازن واللوجستيات (`Stock & Inventory`):** مستودعات متعددة، جرد مستمر (`Perpetual Inventory`)، تتبع الأرقام التسلسلية (`Serial No`) وتواريخ الصلاحية (`Batch`).
- **الجودة والصيانة وخدمة العملاء (`Quality & Support`):** فحص جودة الوارد وأثناء التشغيل، حالات عدم المطابقة، تذاكر الدعم، ومطالبات الضمان (`Warranty Claim`).
- **الأصول الثابتة والمشاريع (`Assets & Projects`):** سجل الأصول والإهلاك التلقائي، وإدارة المشاريع والمهام وساعات العمل والربحية.

---

## هيكل المشروع ومحتويات المستودع

### أولاً: تجهيزات وأدوات شركة Digitbox

| الملف / المجلد | الوصف |
| :--- | :--- |
| [`start-erpnext.sh`](./start-erpnext.sh) | سكريبت التشغيل التلقائي لـ **Linux / macOS / سيرفرات Ubuntu** (يدعم `--port` و`--seed-demo` و`--seed-factory` و`--seed-all`). |
| [`start-erpnext.ps1`](./start-erpnext.ps1) | سكريبت التشغيل التلقائي لـ **Windows PowerShell** (يدعم `-Port` و`-SeedDemo` و`-SeedFactory` و`-SeedAll`). |
| [`run-erpnext-window.cmd`](./run-erpnext-window.cmd) | مشغّل بنقرة واحدة على **Windows** يعتمد على المسار النسبي `%~dp0` (يعمل من أي مجلد بعد `git clone`). |
| [`.gitattributes`](./.gitattributes) | يضمن الحفاظ على نهايات الأسطر الصحيحة (`LF` لملفات Linux/Python/YAML و`CRLF` لملفات Windows) عند النقل بين الأنظمة. |
| [`frappe_docker/pwd.yml`](./frappe_docker/pwd.yml) | ملف **Docker Compose** لتشغيل كافة خدمات النظام محلياً أو على سيرفر تجريبي مع دعم `${ERPNEXT_PORT:-8080}`. |
| [`seed_demo_data.py`](./seed_demo_data.py) | سكريبت إنشاء بيانات تجريبية عامة (شركة/موردون/عملاء/أصناف/فواتير/مدفوعات/CRM/مشروع ومهام). |
| [`seed_appliance_factory.py`](./seed_appliance_factory.py) | سكريبت محاكاة دورة تصنيع كاملة لمصنع بوتاجازات وثلاجات (مخازن، `BOM`، أوامر تشغيل، جودة، هالك، تسليم بالسيريال، وضمان). |
| [`seed_factory_users_and_extras.py`](./seed_factory_users_and_extras.py) | سكريبت إنشاء 5 مستخدمين بصلاحيات أدوار المصنع (`Role/Module Profiles`) + موظفين + مطالبة ضمان + `Landed Cost Voucher`. |
| [`SYSTEM_OVERVIEW.md`](./SYSTEM_OVERVIEW.md) | الدليل التعريفي الشامل لأقسام ووحدات النظام الـ 12 ورحلات العمل المتكاملة باللغة العربية. |
| [`FACTORY_DISCOVERY_CHECKLIST.md`](./FACTORY_DISCOVERY_CHECKLIST.md) | دليل التحليل (`Discovery Checklist`) ومصفوفة التعديلات وخطة التنفيذ المرحلية لمصنع البوتاجازات والثلاجات. |

### ثانياً: النواة مفتوحة المصدر

| المجلد | الوصف |
| :--- | :--- |
| `erpnext/` | الكود المصدري الكامل لنظام **ERPNext v16** مفتوح المصدر. |
| `frappe_docker/` | ملفات Docker الرسمية لتشغيل ونشر بيئات Frappe/ERPNext (سريعة أو إنتاجية مع SSL). |
| `banking/` و`islands/` | مكونات التكامل البنكي وواجهات المشاريع الحديثة المضمنة في الحزمة. |

---

## روابط التحميل والمتطلبات الأساسية

### مواصفات الجهاز أو السيرفر الموصى بها

| المكون | الحد الأدنى للتشغيل | الموصى به (خاصة للسيرفر) |
| :--- | :--- | :--- |
| **المعالج (`CPU`)** | `2 vCPU` | `2–4 vCPU` |
| **الذاكرة (`RAM`)** | `4 GB` (+ Swap 2–4 GB) | `8 GB` |
| **المساحة (`Disk`)** | `20 GB SSD` | `40 GB+ SSD` |
| **نظام التشغيل** | Windows 10/11 أو Ubuntu 22.04/24.04 | Ubuntu 24.04 LTS / Debian 12 |

### روابط التحميل الرسمية للأدوات المطلوبة

| الأداة | المنصة | رابط التحميل / التثبيت الرسمي |
| :--- | :--- | :--- |
| **Docker Desktop** (يتضمن Compose v2) | Windows / macOS | https://www.docker.com/products/docker-desktop/ |
| **Docker Engine & Compose v2** | Linux / Ubuntu Server | https://docs.docker.com/engine/install/ubuntu/ |
| **Git** | Windows / macOS / Linux | https://git-scm.com/downloads |
| **GitHub CLI (`gh`)** *(اختياري للاستنساخ السهل)* | جميع الأنظمة | https://cli.github.com/ |
| **صورة ERPNext الرسمية على Docker Hub** | Docker (`v16.60.0`) | https://hub.docker.com/r/frappe/erpnext |

---

## دليل التشغيل خطوة بخطوة على أي جهاز أو سيرفر

### الخطوة 1: استنساخ المستودع (`git clone`) على الجهاز أو السيرفر الجديد

بما أن هذا المستودع **خاص (`Private`)** على GitHub، عند استنساخه على جهاز جديد أو سيرفر خارجي ستحتاج إلى المصادقة بإحدى الطرق التالية:

```bash
# الطريقة أ: عبر رابط HTTPS مع Personal Access Token (PAT) أو إدخال بيانات GitHub
git clone https://github.com/fares-ma/erp.git
cd erp

# الطريقة ب: إذا كان لديك GitHub CLI (gh) مثبّتاً على الجهاز/السيرفر
gh auth login
gh repo clone fares-ma/erp
cd erp
```

> **للمصادقة بـ PAT مباشرة في رابط HTTPS (مفيد على السيرفرات):**
> أنشئ Token من GitHub عبر `Settings -> Developer settings -> Personal access tokens` بصلاحية `repo`، ثم استخدم:
> `git clone https://<YOUR_GITHUB_TOKEN>@github.com/fares-ma/erp.git`

---

### الخطوة 2: التشغيل حسب نظام التشغيل

#### أ) على سيرفر خارجي (`Linux / Ubuntu Server VPS`)

1. **تثبيت Git وDocker على سيرفر Ubuntu جديد (إذا لم يكونا مثبتين):**

```bash
sudo apt update && sudo apt install -y git curl
curl -fsSL https://get.docker.com | sudo sh
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

2. **فتح البورت في الجدار الناري (إذا كان `ufw` مفعّلاً على السيرفر):**

```bash
sudo ufw allow 8080/tcp
```

3. **تشغيل النظام (ومعه تعبئة بيانات المصنع تلقائياً إن أردت):**

```bash
chmod +x start-erpnext.sh

# تشغيل النظام فقط (موقع نظيف جاهز):
./start-erpnext.sh

# أو تشغيل النظام + تعبئة بيانات مصنع الأجهزة المنزلية + المستخدمين تلقائياً:
./start-erpnext.sh --seed-factory

# أو تشغيل النظام + تعبئة جميع البيانات (التجارية العامة + المصنع + المستخدمين):
./start-erpnext.sh --seed-all

# لتشغيله على بورت مختلف (مثلاً 8090 بدلاً من 8080):
./start-erpnext.sh --port 8090 --seed-factory
```

4. **فتح النظام من المتصفح:**
   - إذا كنت على السيرفر مباشرة: `http://localhost:8080`
   - من جهازك إلى السيرفر الخارجي: `http://<SERVER_IP>:8080`

> **ملاحظة لإنتاج السيرفرات بـ Domain وHTTPS:** ملف `frappe_docker/pwd.yml` مخصص للتشغيل السريع والتجربة والـ Staging على بورت `8080`. للنشر الإنتاجي الدائم بدومين وشهادة SSL (`HTTPS`) استخدم ملفات الإنتاج الرسمية في [`frappe_docker/`](./frappe_docker) أو راجع [توثيق Frappe Docker الرسمي](https://github.com/frappe/frappe_docker).

---

#### ب) على نظام `Windows`

1. تأكد من تثبيت **Docker Desktop** وتشغيله.
2. من داخل مجلد المشروع، افتح **PowerShell** ونفّذ أحد الأوامر التالية:

```powershell
# تشغيل النظام فقط:
.\start-erpnext.ps1

# تشغيل النظام + تعبئة بيانات المصنع والمستخدمين تلقائياً:
.\start-erpnext.ps1 -SeedFactory

# تشغيل النظام + تعبئة جميع البيانات التجريبية:
.\start-erpnext.ps1 -SeedAll

# تشغيل على بورت مخصص (مثلاً 8090):
.\start-erpnext.ps1 -Port 8090 -SeedFactory
```

> يمكنك أيضاً تشغيل الملف [`run-erpnext-window.cmd`](./run-erpnext-window.cmd) بالنقر المزدوج (أو تمرير المعاملات له مثل `run-erpnext-window.cmd -SeedFactory`).

---

#### ج) التشغيل اليدوي المباشر عبر Docker Compose (جميع الأنظمة)

```bash
cd frappe_docker
docker compose -f pwd.yml up -d
docker compose -f pwd.yml logs -f create-site
```

*(لتغيير البورت يدوياً: `ERPNEXT_PORT=8090 docker compose -f pwd.yml up -d`)*

> تستغرق عملية إنشاء الموقع في المرة الأولى (`create-site`) عادةً من **2 إلى 5 دقائق** حتى تكتمل الجداول.

---

## بيانات الدخول وحسابات المستخدمين الجاهزة للتجربة

### 1. حساب مدير النظام الافتراضي (`Administrator`)

| البند | القيمة |
| :--- | :--- |
| **الرابط المحلي** | `http://localhost:8080` |
| **الرابط على السيرفر** | `http://<SERVER_IP>:8080` |
| **اسم الموقع (`Site`)** | `frontend` |
| **اسم المستخدم** | `Administrator` |
| **كلمة المرور** | `admin` |
| **صور Docker المستخدمة** | `frappe/erpnext:v16.60.0` · `mariadb:11.8` · `redis:6.2-alpine` |

### 2. حسابات أدوار المصنع (تُنشأ عند تشغيل `--seed-factory` أو `seed_factory_users_and_extras.py`)

كلمة المرور الموحدة لجميع حسابات التجربة التالية هي: **`Factory@2026`**

| البريد الإلكتروني (اسم الدخول) | الدور الوظيفي (`Role Profile`) | نطاق الصلاحيات (`Module Profile`) |
| :--- | :--- | :--- |
| `gm@factory.local` | `Factory General Manager` | جميع الوحدات وصلاحيات الإدارة الكاملة |
| `stock@factory.local` | `Factory Stock Keeper` | المخازن فقط + مقيّد بمخزن `Raw Materials` |
| `production@factory.local` | `Factory Production Engineer` | التصنيع والمخازن |
| `qc@factory.local` | `Factory QC Inspector` | إدارة الجودة والتصنيع والمخازن |
| `accounts@factory.local` | `Factory Accountant` | الحسابات والمبيعات والمشتريات |

---

## تشغيل سكريبتات البيانات التجريبية (Seed Data)

يمكنك تشغيل السكريبتات تلقائياً أثناء البدء باستخدام `--seed-factory` / `-SeedFactory` أو `--seed-all` / `-SeedAll`، أو تشغيلها يدوياً في أي وقت بعد إقلاع الحاويات.

> **ذكي ومستقل تلقائياً (`Self-Bootstrapping`):**
> - إذا شغّلت أي سكريبت على موقع **جديد تماماً** قبل فتح المتصفح، يقوم السكريبت تلقائياً بإكمال معالج الإعداد الأولي (`Setup Wizard`) وإنشاء شركة افتراضية (`Fares-Test-company` بعملة `EGP` واختصار `test`) دون أي أخطاء.
> - إذا كنت قد أنشأت شركتك مسبقاً من المتصفح بأي اسم أو عملة أخرى، يكتشف السكريبت شركتك واختصارها وعملتها تلقائياً.
> - يمكنك أيضاً تخصيص القيم قبل التشغيل عبر متغيرات البيئة: `ERPNEXT_COMPANY`، `ERPNEXT_ABBR`، `ERPNEXT_CURRENCY`.

### أوامر التشغيل اليدوي للسكريبتات (من جذر المشروع)

```bash
# 1) البيانات التجارية العامة (شراء، بيع، مخزون، مدفوعات، CRM، ومشاريع):
docker compose -f frappe_docker/pwd.yml cp seed_demo_data.py backend:/tmp/seed_demo_data.py
docker compose -f frappe_docker/pwd.yml exec -T backend /home/frappe/frappe-bench/env/bin/python /tmp/seed_demo_data.py

# 2) دورة تصنيع مصنع الأجهزة المنزلية (بوتاجازات وثلاجات + BOM + أوامر تشغيل + سيريال):
docker compose -f frappe_docker/pwd.yml cp seed_appliance_factory.py backend:/tmp/seed_appliance_factory.py
docker compose -f frappe_docker/pwd.yml exec -T backend /home/frappe/frappe-bench/env/bin/python /tmp/seed_appliance_factory.py

# 3) مستخدمو المصنع وصلاحياتهم + الموظفون + مطالبة الضمان + Landed Cost Voucher:
docker compose -f frappe_docker/pwd.yml cp seed_factory_users_and_extras.py backend:/tmp/seed_factory_users_and_extras.py
docker compose -f frappe_docker/pwd.yml exec -T backend /home/frappe/frappe-bench/env/bin/python /tmp/seed_factory_users_and_extras.py
```

---

## إدارة السيرفر والنسخ الاحتياطي وحل المشاكل الشائعة

### أوامر Docker اليومية (تُنفّذ من جذر المشروع)

```bash
# عرض حالة جميع الحاويات
docker compose -f frappe_docker/pwd.yml ps

# متابعة السجلات الحية للخدمة الخلفية أو إنشاء الموقع
docker compose -f frappe_docker/pwd.yml logs -f backend
docker compose -f frappe_docker/pwd.yml logs -f create-site

# إعادة تشغيل الواجهة أو الخادم
docker compose -f frappe_docker/pwd.yml restart frontend backend

# إيقاف مؤقت مع حفظ جميع البيانات
docker compose -f frappe_docker/pwd.yml stop

# إزالة الحاويات مع الإبقاء على قاعدة البيانات والملفات
docker compose -f frappe_docker/pwd.yml down
```

> ⚠️ **تحذير مهم:** الأمر `docker compose -f frappe_docker/pwd.yml down -v` يحذف الـ Volumes نهائياً (قاعدة بيانات MariaDB وملفات الموقع). لا تستخدم `-v` إلا إذا أردت مسح كل البيانات والبدء من الصفر.

### أخذ نسخة احتياطية كاملة (`Backup`)

```bash
docker compose -f frappe_docker/pwd.yml exec -T backend bench --site frontend backup --with-files
```

*(تُحفظ ملفات النسخة الاحتياطية داخل حجم `sites` في المسار `/home/frappe/frappe-bench/sites/frontend/private/backups/`).*

### حل المشاكل الشائعة عند النشر على جهاز أو سيرفر جديد

| المشكلة | السبب والحل |
| :--- | :--- |
| **البورت `8080` مستخدم بالفعل** | مرّر بورتاً آخر عند التشغيل: `./start-erpnext.sh --port 8090` (أو `-Port 8090` على Windows). |
| **خطأ `permission denied` عند تشغيل Docker على Linux** | أضف المستخدم لمجموعة docker ثم أعد تسجيل الدخول: `sudo usermod -aG docker "$USER" && newgrp docker` (أو شغّل `./start-erpnext.sh` وسيستخدم `sudo` تلقائياً). |
| **السيرفر يستهلك الذاكرة بسرعة (VPS 2–4 GB RAM)** | أنشئ ملف Swap بحجم 4 GB على السيرفر قبل التشغيل:<br>`sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile` |
| **الموقع يفتح بصفحة 502 أو لا يستجيب فور التشغيل** | غالباً لا يزال `create-site` ينشئ الجداول (يستغرق 2–5 دقائق). راقب التقدم بـ:<br>`docker compose -f frappe_docker/pwd.yml logs -f create-site` |
| **عدم القدرة على الوصول عبر IP السيرفر من المتصفح** | تأكد من فتح المنفذ في `ufw` (`sudo ufw allow 8080/tcp`) وفي **Security Group / Firewall** الخاص بمزوّد السيرفر السحابي. |

---

## بيئة التطوير المحلية بدون Docker (`Frappe Bench`)

لمطوّري بايثون وجافاسكريبت الراغبين في تشغيل الكود مباشرة عبر `bench` بدون Docker:

1. ثبّت `frappe-bench` والمتطلبات الأساسية وفق [دليل تثبيت Frappe Framework الرسمي](https://frappeframework.com/docs/user/en/installation) (وانظر مستودع [frappe/bench](https://github.com/frappe/bench)).
2. أنشئ بيئة Bench وشغّل الخادم:
   ```bash
   bench init frappe-bench
   cd frappe-bench
   bench start
   ```
3. في نافذة طرفية ثانية، أنشئ الموقع وثبّت التطبيق من مستودعك أو من المجلد المحلي:
   ```bash
   bench new-site erpnext.localhost
   bench get-app erpnext https://github.com/fares-ma/erp.git
   bench --site erpnext.localhost install-app erpnext
   ```
4. افتح الرابط `http://erpnext.localhost:8000/app` في المتصفح.

---

## الوثائق والمراجع الرسمية الأصلية

### أولاً: أدلة المشروع الداخلية (من Digitbox باللغة العربية)

| الدليل | المحتوى |
| :--- | :--- |
| **[SYSTEM_OVERVIEW.md](./SYSTEM_OVERVIEW.md)** | الدليل التعريفي الشامل لنظام ERP؛ خريطة ترابط الأقسام الـ 12، العمليات، التقارير، ومؤشرات الأداء. |
| **[FACTORY_DISCOVERY_CHECKLIST.md](./FACTORY_DISCOVERY_CHECKLIST.md)** | خارطة التحليل والتنفيذ لمصنع بوتاجازات وثلاجات؛ أسئلة الـ Discovery، مصفوفة التعديلات، وخطة الـ 4 مراحل. |

### ثانياً: التوثيق والروابط الأصلية لمنظومة ERPNext وFrappe

| المرجع | الرابط الرسمي |
| :--- | :--- |
| **التوثيق الرسمي لـ ERPNext (Documentation)** | https://docs.erpnext.com/ · https://docs.frappe.io/erpnext/ |
| **الموقع الرسمي لـ ERPNext** | https://frappe.io/erpnext |
| **العرض التفاعلي الرسمي (Live Demo)** | https://erpnext-demo.frappe.cloud/api/method/erpnext_demo.erpnext_demo.auth.login_demo |
| **توثيق Frappe Docker الرسمي (الإنتاج وSSL)** | https://github.com/frappe/frappe_docker |
| **تشغيل Docker على معالجات ARM64** | https://github.com/frappe/frappe_docker/blob/main/docs/01-getting-started/03-arm64.md |
| **إطار العمل Frappe Framework** | https://github.com/frappe/frappe |
| **أداة Bench وإعداد التطوير** | https://github.com/frappe/bench · https://frappeframework.com/docs/user/en/installation |
| **مكتبة الواجهات Frappe UI** | https://github.com/frappe/frappe-ui |
| **الاستضافة المُدارة Frappe Cloud** | https://frappecloud.com |
| **أكاديمية التعلم Frappe School** | https://school.frappe.io |
| **منتدى المجتمع (Discussion Forum)** | https://discuss.frappe.io/c/erpnext/6 |
| **مجموعة تيليجرام الرسمية** | https://erpnext_public.t.me |
| **إرشادات الأخطاء والمساهمة والأمان** | [Issue Guidelines](https://github.com/frappe/erpnext/wiki/Issue-Guidelines) · [Contribution Guidelines](https://github.com/frappe/erpnext/wiki/Contribution-Guidelines) · [Security](https://erpnext.com/security) · [Translations](https://crowdin.com/project/frappe) |

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
