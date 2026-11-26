import json
import os

os.chdir("/home/frappe/frappe-bench/sites")

import frappe
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry
from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice as make_si_from_dn
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice

SITE = os.environ.get("ERPNEXT_SITE", "frontend")
COMPANY = None
ABBR = None
CURRENCY = None
PARENT_WH = None
WH_RM = None
WH_WIP = None
WH_FG = None
WH_SCRAP = None
WH_GRADE_B = None
VALUATION_EXPENSE_ACCOUNT = None


def ensure_master_prereqs(company, currency):
    for uom_name in ("Nos", "Kg"):
        if not frappe.db.exists("UOM", uom_name):
            frappe.get_doc({"doctype": "UOM", "uom_name": uom_name}).insert(ignore_permissions=True)

    root_territory = frappe.db.get_value("Territory", {"is_group": 1}, "name") or "All Territories"
    if not frappe.db.exists("Territory", "Egypt"):
        frappe.get_doc(
            {"doctype": "Territory", "territory_name": "Egypt", "parent_territory": root_territory, "is_group": 0}
        ).insert(ignore_permissions=True)

    root_sup_group = frappe.db.get_value("Supplier Group", {"is_group": 1}, "name") or "All Supplier Groups"
    if not frappe.db.exists("Supplier Group", "Raw Material"):
        frappe.get_doc(
            {
                "doctype": "Supplier Group",
                "supplier_group_name": "Raw Material",
                "parent_supplier_group": root_sup_group,
            }
        ).insert(ignore_permissions=True)

    root_cust_group = frappe.db.get_value("Customer Group", {"is_group": 1}, "name") or "All Customer Groups"
    if not frappe.db.exists("Customer Group", "Commercial"):
        frappe.get_doc(
            {
                "doctype": "Customer Group",
                "customer_group_name": "Commercial",
                "parent_customer_group": root_cust_group,
            }
        ).insert(ignore_permissions=True)

    root_item_group = frappe.db.get_value("Item Group", {"is_group": 1}, "name") or "All Item Groups"
    for ig in ("Raw Material", "Sub Assemblies", "Products"):
        if not frappe.db.exists("Item Group", ig):
            frappe.get_doc(
                {"doctype": "Item Group", "item_group_name": ig, "parent_item_group": root_item_group}
            ).insert(ignore_permissions=True)

    for pl_name, buying, selling in (("Standard Buying", 1, 0), ("Standard Selling", 0, 1)):
        if not frappe.db.exists("Price List", pl_name):
            frappe.get_doc(
                {
                    "doctype": "Price List",
                    "price_list_name": pl_name,
                    "enabled": 1,
                    "buying": buying,
                    "selling": selling,
                    "currency": currency,
                }
            ).insert(ignore_permissions=True)

    fy_exists = frappe.db.sql(
        """
        SELECT name FROM `tabFiscal Year`
        WHERE disabled = 0 AND year_start_date <= '2026-11-01' AND year_end_date >= '2026-12-31'
        LIMIT 1
        """
    )
    if not fy_exists:
        fy_name = "2026"
        if frappe.db.exists("Fiscal Year", fy_name):
            fy_doc = frappe.get_doc("Fiscal Year", fy_name)
            fy_doc.disabled = 0
            fy_doc.save(ignore_permissions=True)
        else:
            frappe.get_doc(
                {
                    "doctype": "Fiscal Year",
                    "year": fy_name,
                    "year_start_date": "2026-01-01",
                    "year_end_date": "2026-12-31",
                    "companies": [{"company": company}],
                }
            ).insert(ignore_permissions=True)


def bootstrap_and_resolve_context():
    env_company = os.environ.get("ERPNEXT_COMPANY")
    company = None
    if env_company and frappe.db.exists("Company", env_company):
        company = env_company
    if not company:
        default_company = frappe.db.get_single_value("Global Defaults", "default_company")
        if default_company and frappe.db.exists("Company", default_company):
            company = default_company
    if not company:
        companies = frappe.get_all("Company", pluck="name", limit=1)
        if companies:
            company = companies[0]

    if not company:
        company_name = env_company or "Fares-Test-company"
        company_abbr = os.environ.get("ERPNEXT_ABBR", "test")
        currency = os.environ.get("ERPNEXT_CURRENCY", "EGP")
        country = "Egypt" if frappe.db.exists("Country", "Egypt") else (frappe.get_all("Country", pluck="name", limit=1)[0])
        setup_args = {
            "country": country,
            "timezone": "Africa/Cairo",
            "language": "English",
            "currency": currency,
            "company_name": company_name,
            "company_abbr": company_abbr,
            "chart_of_accounts": "Standard",
            "domain": "Manufacturing",
            "fy_start_date": "2026-01-01",
            "fy_end_date": "2026-12-31",
            "full_name": "Administrator",
            "email": "admin@example.com",
            "password": "admin",
        }
        try:
            from frappe.desk.page.setup_wizard.setup_wizard import setup_complete as desk_setup_complete

            desk_setup_complete(setup_args)
        except Exception:
            from erpnext.setup.setup_wizard.setup_wizard import setup_complete as erpnext_setup_complete

            erpnext_setup_complete(frappe._dict(setup_args))
            frappe.db.set_single_value("System Settings", "setup_complete", 1)
            frappe.db.commit()
        company = frappe.db.get_value("Company", {"company_name": company_name}, "name") or company_name

    abbr = frappe.db.get_value("Company", company, "abbr") or "test"
    currency = frappe.db.get_value("Company", company, "default_currency") or os.environ.get("ERPNEXT_CURRENCY", "EGP")
    ensure_master_prereqs(company, currency)

    parent_wh = (
        frappe.db.get_value(
            "Warehouse", {"company": company, "is_group": 1, "parent_warehouse": ["in", ["", None]]}, "name"
        )
        or frappe.db.get_value("Warehouse", {"company": company, "is_group": 1}, "name")
        or f"All Warehouses - {abbr}"
    )
    valuation_account = (
        frappe.db.get_value(
            "Account", {"company": company, "account_type": "Expenses Included In Valuation", "is_group": 0}, "name"
        )
        or f"Expenses Included In Valuation - {abbr}"
    )
    return {
        "company": company,
        "abbr": abbr,
        "currency": currency,
        "parent_wh": parent_wh,
        "valuation_account": valuation_account,
    }


def ensure_warehouse(wh_name):
    existing = frappe.db.get_value("Warehouse", {"warehouse_name": wh_name, "company": COMPANY}, "name")
    if existing:
        return existing
    doc = frappe.get_doc(
        {
            "doctype": "Warehouse",
            "warehouse_name": wh_name,
            "parent_warehouse": PARENT_WH,
            "company": COMPANY,
            "is_group": 0,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def ensure_supplier(name, supplier_group):
    if frappe.db.exists("Supplier", name):
        return name
    doc = frappe.get_doc(
        {
            "doctype": "Supplier",
            "supplier_name": name,
            "supplier_group": supplier_group,
            "supplier_type": "Company",
            "country": "Egypt",
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def ensure_customer(name, customer_group):
    if frappe.db.exists("Customer", name):
        return name
    doc = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": name,
            "customer_group": customer_group,
            "customer_type": "Company",
            "territory": "Egypt",
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def ensure_item(
    code,
    item_name,
    item_group,
    uom,
    default_wh,
    buy_rate=None,
    sell_rate=None,
    has_serial_no=0,
    serial_no_series=None,
    warranty_period=None,
    valuation_rate=None,
):
    if not frappe.db.exists("Item", code):
        item_dict = {
            "doctype": "Item",
            "item_code": code,
            "item_name": item_name,
            "item_group": item_group,
            "stock_uom": uom,
            "is_stock_item": 1,
            "has_serial_no": has_serial_no,
            "standard_rate": sell_rate or 0,
            "valuation_rate": valuation_rate or buy_rate or 0,
            "item_defaults": [{"company": COMPANY, "default_warehouse": default_wh}],
        }
        if serial_no_series:
            item_dict["serial_no_series"] = serial_no_series
        if warranty_period is not None:
            item_dict["warranty_period"] = str(warranty_period)
        frappe.get_doc(item_dict).insert(ignore_permissions=True)

    if buy_rate is not None and not frappe.db.exists(
        "Item Price", {"item_code": code, "price_list": "Standard Buying"}
    ):
        buying_currency = frappe.db.get_value("Price List", "Standard Buying", "currency") or CURRENCY
        frappe.get_doc(
            {
                "doctype": "Item Price",
                "item_code": code,
                "price_list": "Standard Buying",
                "buying": 1,
                "currency": buying_currency,
                "price_list_rate": buy_rate,
            }
        ).insert(ignore_permissions=True)

    if sell_rate is not None and not frappe.db.exists(
        "Item Price", {"item_code": code, "price_list": "Standard Selling"}
    ):
        selling_currency = frappe.db.get_value("Price List", "Standard Selling", "currency") or CURRENCY
        frappe.get_doc(
            {
                "doctype": "Item Price",
                "item_code": code,
                "price_list": "Standard Selling",
                "selling": 1,
                "currency": selling_currency,
                "price_list_rate": sell_rate,
            }
        ).insert(ignore_permissions=True)


def ensure_workstation(name, hour_rate):
    if frappe.db.exists("Workstation", name):
        return name
    doc = frappe.get_doc(
        {
            "doctype": "Workstation",
            "workstation_name": name,
            "production_capacity": 2,
            "hour_rate": hour_rate,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def ensure_operation(name, workstation):
    if frappe.db.exists("Operation", name):
        return name
    doc = frappe.get_doc(
        {
            "doctype": "Operation",
            "name": name,
            "workstation": workstation,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def ensure_qc_param(name):
    if frappe.db.exists("Quality Inspection Parameter", name):
        return name
    doc = frappe.get_doc(
        {
            "doctype": "Quality Inspection Parameter",
            "parameter": name,
            "description": name,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def execute_work_order(
    item_code,
    bom_no,
    qty,
    fg_warehouse,
    planned_date,
    transfer_date,
    finish_date,
    source_map=None,
    default_source=WH_RM,
    use_multi_level_bom=0,
    sales_order=None,
    production_plan=None,
    production_plan_item=None,
    complete=True,
    qc_item_code=None,
):
    wo_dict = {
        "doctype": "Work Order",
        "company": COMPANY,
        "production_item": item_code,
        "bom_no": bom_no,
        "qty": qty,
        "planned_start_date": f"{planned_date} 08:00:00",
        "wip_warehouse": WH_WIP,
        "fg_warehouse": fg_warehouse,
        "use_multi_level_bom": use_multi_level_bom,
    }
    if sales_order:
        wo_dict["sales_order"] = sales_order
    if production_plan:
        wo_dict["production_plan"] = production_plan
    if production_plan_item:
        wo_dict["production_plan_item"] = production_plan_item

    wo = frappe.get_doc(wo_dict)
    wo.set_work_order_operations()
    wo.insert(ignore_permissions=True)
    for req in wo.required_items:
        req.source_warehouse = (source_map or {}).get(req.item_code, default_source)
    wo.save(ignore_permissions=True)
    wo.submit()

    if not complete:
        job_cards = frappe.get_all("Job Card", filters={"work_order": wo.name}, pluck="name")
        return {"work_order": wo.name, "status": wo.status, "job_cards": job_cards}

    se_transfer = frappe.get_doc(make_stock_entry(wo.name, "Material Transfer for Manufacture"))
    se_transfer.set_posting_time = 1
    se_transfer.posting_date = transfer_date
    se_transfer.posting_time = "09:00:00"
    se_transfer.insert(ignore_permissions=True)
    se_transfer.submit()

    job_cards = frappe.get_all(
        "Job Card",
        filters={"work_order": wo.name},
        fields=["name", "operation", "time_required"],
        order_by="sequence_id asc, creation asc",
    )
    jc_names = []
    qc_name = None
    for idx, jc_row in enumerate(job_cards):
        jc = frappe.get_doc("Job Card", jc_row.name)
        mins = int(jc.time_required or 30)
        start_hr = 10 + idx
        end_hr = start_hr + max(1, (mins + 59) // 60)
        jc.append(
            "time_logs",
            {
                "from_time": f"{transfer_date} {start_hr:02d}:00:00",
                "to_time": f"{transfer_date} {end_hr:02d}:00:00",
                "completed_qty": qty,
            },
        )

        if qc_item_code and "QC" in (jc.operation or ""):
            p1 = ensure_qc_param("Cooling Temp Reach (-18C)")
            p2 = ensure_qc_param("Gas & Refrigerant Leak Check")
            p3 = ensure_qc_param("Body Paint & Finish Check")
            qi = frappe.get_doc(
                {
                    "doctype": "Quality Inspection",
                    "inspection_type": "In Process",
                    "reference_type": "Job Card",
                    "reference_name": jc.name,
                    "item_code": qc_item_code,
                    "sample_size": qty,
                    "report_date": finish_date,
                    "status": "Accepted",
                    "inspected_by": "Administrator",
                    "readings": [
                        {"specification": p1, "manual_inspection": 1, "numeric": 0, "status": "Accepted", "reading_value": "-18.5C OK"},
                        {"specification": p2, "manual_inspection": 1, "numeric": 0, "status": "Accepted", "reading_value": "Zero Leak"},
                        {"specification": p3, "manual_inspection": 1, "numeric": 0, "status": "Accepted", "reading_value": "Grade A Inox"},
                    ],
                }
            )
            qi.insert(ignore_permissions=True)
            qi.submit()
            qc_name = qi.name
            jc.quality_inspection = qi.name

        jc.save(ignore_permissions=True)
        jc.submit()
        jc_names.append(jc.name)

    se_mfg = frappe.get_doc(make_stock_entry(wo.name, "Manufacture"))
    se_mfg.set_posting_time = 1
    se_mfg.posting_date = finish_date
    se_mfg.posting_time = "16:00:00"
    for d in se_mfg.items:
        d.use_serial_batch_fields = 1
    se_mfg.insert(ignore_permissions=True)
    se_mfg.submit()

    wo.reload()
    res = {
        "work_order": wo.name,
        "status": wo.status,
        "transfer_entry": se_transfer.name,
        "manufacture_entry": se_mfg.name,
        "job_cards": jc_names,
    }
    if qc_name:
        res["quality_inspection"] = qc_name
    return res


def run_seed():
    global COMPANY, ABBR, CURRENCY, PARENT_WH, WH_RM, WH_WIP, WH_FG, WH_SCRAP, WH_GRADE_B, VALUATION_EXPENSE_ACCOUNT
    frappe.init(site=SITE)
    frappe.connect()
    frappe.set_user("Administrator")

    try:
        ctx = bootstrap_and_resolve_context()
        COMPANY = ctx["company"]
        ABBR = ctx["abbr"]
        CURRENCY = ctx["currency"]
        PARENT_WH = ctx["parent_wh"]
        VALUATION_EXPENSE_ACCOUNT = ctx["valuation_account"]

        if frappe.db.exists("Item", "FG-FRIDGE-16FT"):
            print("FACTORY_ALREADY_SEEDED")
            return

        # Enable serial/batch support & disable strict capacity conflicts
        frappe.db.set_single_value("Stock Settings", "enable_serial_and_batch_no_for_item", 1)
        frappe.db.set_single_value("Manufacturing Settings", "disable_capacity_planning", 1)
        if not frappe.db.get_value("Company", COMPANY, "default_operating_cost_account") and frappe.db.exists(
            "Account", VALUATION_EXPENSE_ACCOUNT
        ):
            frappe.db.set_value(
                "Company",
                COMPANY,
                "default_operating_cost_account",
                VALUATION_EXPENSE_ACCOUNT,
            )

        summary = {"company": COMPANY, "currency": CURRENCY}

        # 1. Warehouses
        WH_RM = ensure_warehouse("Raw Materials")
        WH_WIP = ensure_warehouse("Work In Progress")
        WH_FG = ensure_warehouse("Finished Goods")
        WH_SCRAP = ensure_warehouse("Scrap Warehouse")
        WH_GRADE_B = ensure_warehouse("Grade B Appliances")
        summary["warehouses"] = [WH_RM, WH_WIP, WH_FG, WH_SCRAP, WH_GRADE_B]

        # 2. Supplier & Customer
        sup = ensure_supplier("Misr Steel & Cooling Components", "Raw Material")
        cust = ensure_customer("El-Araby Home Appliances Dealers", "Commercial")
        summary["supplier"] = sup
        summary["customer"] = cust

        # 3. Items (Raw Materials, Scrap, Sub-Assembly, Finished Serialized Appliances)
        raw_items = [
            ("RM-STEEL-304", "Stainless Steel 304 Sheet", "Raw Material", "Kg", WH_RM, 95, None),
            ("RM-COMP-INV14", "Inverter Compressor 1/4 HP", "Raw Material", "Nos", WH_RM, 3200, None),
            ("RM-FOAM-PU", "Polyurethane Insulation Foam", "Raw Material", "Kg", WH_RM, 140, None),
            ("RM-THERMO-DIG", "Digital Fridge Thermostat & Display", "Raw Material", "Nos", WH_RM, 450, None),
            ("RM-BURNER-5S", "Italian 5-Burner Gas Set", "Raw Material", "Nos", WH_RM, 1150, None),
            ("RM-GLASS-TEMP", "Tempered Oven Door Glass 90cm", "Raw Material", "Nos", WH_RM, 680, None),
            ("RM-IGNITION-SAFE", "Full Safety Auto-Ignition Kit", "Raw Material", "Nos", WH_RM, 520, None),
            ("RM-CARTON-APPL", "Heavy-Duty Appliance Carton & Styrofoam", "Raw Material", "Nos", WH_RM, 180, None),
        ]
        for code, name, grp, uom, wh, buy_r, sell_r in raw_items:
            ensure_item(code, name, grp, uom, wh, buy_rate=buy_r, sell_rate=sell_r)

        ensure_item(
            "SCRAP-STEEL",
            "Sheet Metal Stamping Scrap",
            "Raw Material",
            "Kg",
            WH_SCRAP,
            sell_rate=18,
            valuation_rate=18,
        )
        ensure_item(
            "SA-FRIDGE-CAB-16",
            "Foamed Fridge Cabinet 16ft",
            "Sub Assemblies",
            "Nos",
            WH_WIP,
        )
        ensure_item(
            "FG-FRIDGE-16FT",
            "No-Frost Refrigerator 16ft Inox",
            "Products",
            "Nos",
            WH_FG,
            sell_rate=22500,
            has_serial_no=1,
            serial_no_series="FRG16-.#####",
            warranty_period=1825,
        )
        ensure_item(
            "FG-STOVE-5B-90",
            "Royal 5-Burner Full-Safety Stove 90cm",
            "Products",
            "Nos",
            WH_FG,
            sell_rate=14800,
            has_serial_no=1,
            serial_no_series="STV90-.#####",
            warranty_period=1825,
        )

        # 4. Purchase & Receive Raw Materials (2026-11-01)
        rm_qty_map = {
            "RM-STEEL-304": (500, 95),
            "RM-COMP-INV14": (20, 3200),
            "RM-FOAM-PU": (150, 140),
            "RM-THERMO-DIG": (20, 450),
            "RM-BURNER-5S": (20, 1150),
            "RM-GLASS-TEMP": (20, 680),
            "RM-IGNITION-SAFE": (20, 520),
            "RM-CARTON-APPL": (40, 180),
        }
        po = frappe.get_doc(
            {
                "doctype": "Purchase Order",
                "company": COMPANY,
                "supplier": sup,
                "transaction_date": "2026-11-01",
                "schedule_date": "2026-11-03",
                "currency": CURRENCY,
                "items": [
                    {
                        "item_code": code,
                        "qty": qty,
                        "rate": rate,
                        "schedule_date": "2026-11-03",
                        "warehouse": WH_RM,
                    }
                    for code, (qty, rate) in rm_qty_map.items()
                ],
            }
        )
        po.insert(ignore_permissions=True)
        po.submit()

        pr = make_purchase_receipt(po.name)
        pr.set_posting_time = 1
        pr.posting_date = "2026-11-01"
        pr.posting_time = "11:00:00"
        pr.insert(ignore_permissions=True)
        pr.submit()

        pi = make_purchase_invoice(pr.name)
        pi.set_posting_time = 1
        pi.posting_date = "2026-11-01"
        pi.due_date = "2026-12-01"
        pi.bill_no = "MISR-RM-2026-01"
        pi.bill_date = "2026-11-01"
        pi.insert(ignore_permissions=True)
        pi.submit()

        summary["raw_material_purchase"] = {
            "purchase_order": po.name,
            "purchase_receipt": pr.name,
            "purchase_invoice": pi.name,
            "grand_total": pi.grand_total,
        }

        # 5. Workstations & Operations
        ws_metal = ensure_workstation("Sheet Metal Cutting & Bending Line", 350)
        ws_foam = ensure_workstation("PU Foaming & Insulation Line", 400)
        ws_asm = ensure_workstation("Appliance Final Assembly Line", 300)
        ws_qc = ensure_workstation("Cooling & Gas Safety Testing Lab", 250)

        op_metal = ensure_operation("Sheet Metal Forming", ws_metal)
        op_foam = ensure_operation("Cabinet PU Foaming", ws_foam)
        op_asm = ensure_operation("Final Appliance Assembly", ws_asm)
        op_qc = ensure_operation("Final Safety & Performance QC", ws_qc)

        # 6. Multi-level BOMs
        bom_cab = frappe.get_doc(
            {
                "doctype": "BOM",
                "company": COMPANY,
                "item": "SA-FRIDGE-CAB-16",
                "quantity": 1,
                "currency": CURRENCY,
                "is_active": 1,
                "is_default": 1,
                "with_operations": 1,
                "items": [
                    {"item_code": "RM-STEEL-304", "qty": 18, "rate": 95},
                    {"item_code": "RM-FOAM-PU", "qty": 6, "rate": 140},
                ],
                "operations": [
                    {"operation": op_metal, "workstation": ws_metal, "time_in_mins": 25, "hour_rate": 350},
                    {"operation": op_foam, "workstation": ws_foam, "time_in_mins": 20, "hour_rate": 400},
                ],
            }
        )
        bom_cab.insert(ignore_permissions=True)
        bom_cab.submit()

        bom_fridge = frappe.get_doc(
            {
                "doctype": "BOM",
                "company": COMPANY,
                "item": "FG-FRIDGE-16FT",
                "quantity": 1,
                "currency": CURRENCY,
                "is_active": 1,
                "is_default": 1,
                "with_operations": 1,
                "items": [
                    {"item_code": "SA-FRIDGE-CAB-16", "qty": 1, "bom_no": bom_cab.name},
                    {"item_code": "RM-COMP-INV14", "qty": 1, "rate": 3200},
                    {"item_code": "RM-THERMO-DIG", "qty": 1, "rate": 450},
                    {"item_code": "RM-CARTON-APPL", "qty": 1, "rate": 180},
                ],
                "operations": [
                    {"operation": op_asm, "workstation": ws_asm, "time_in_mins": 35, "hour_rate": 300},
                    {"operation": op_qc, "workstation": ws_qc, "time_in_mins": 20, "hour_rate": 250},
                ],
            }
        )
        bom_fridge.insert(ignore_permissions=True)
        bom_fridge.submit()

        bom_stove = frappe.get_doc(
            {
                "doctype": "BOM",
                "company": COMPANY,
                "item": "FG-STOVE-5B-90",
                "quantity": 1,
                "currency": CURRENCY,
                "is_active": 1,
                "is_default": 1,
                "with_operations": 1,
                "items": [
                    {"item_code": "RM-STEEL-304", "qty": 22, "rate": 95},
                    {"item_code": "RM-BURNER-5S", "qty": 1, "rate": 1150},
                    {"item_code": "RM-GLASS-TEMP", "qty": 1, "rate": 680},
                    {"item_code": "RM-IGNITION-SAFE", "qty": 1, "rate": 520},
                    {"item_code": "RM-CARTON-APPL", "qty": 1, "rate": 180},
                ],
                "operations": [
                    {"operation": op_metal, "workstation": ws_metal, "time_in_mins": 30, "hour_rate": 350},
                    {"operation": op_asm, "workstation": ws_asm, "time_in_mins": 30, "hour_rate": 300},
                    {"operation": op_qc, "workstation": ws_qc, "time_in_mins": 15, "hour_rate": 250},
                ],
            }
        )
        bom_stove.insert(ignore_permissions=True)
        bom_stove.submit()

        summary["boms"] = {
            "sub_assembly_cabinet": {"name": bom_cab.name, "total_cost": bom_cab.total_cost},
            "refrigerator_16ft": {"name": bom_fridge.name, "total_cost": bom_fridge.total_cost},
            "stove_5_burner": {"name": bom_stove.name, "total_cost": bom_stove.total_cost},
        }

        # 7. Dealer Sales Order + Production Plan (MRP)
        so = frappe.get_doc(
            {
                "doctype": "Sales Order",
                "customer": cust,
                "company": COMPANY,
                "transaction_date": "2026-11-12",
                "delivery_date": "2026-11-28",
                "currency": CURRENCY,
                "items": [
                    {"item_code": "FG-FRIDGE-16FT", "qty": 3, "rate": 22500, "delivery_date": "2026-11-28", "warehouse": WH_FG},
                    {"item_code": "FG-STOVE-5B-90", "qty": 4, "rate": 14800, "delivery_date": "2026-11-28", "warehouse": WH_FG},
                ],
            }
        )
        so.insert(ignore_permissions=True)
        so.submit()

        pp = frappe.get_doc(
            {
                "doctype": "Production Plan",
                "company": COMPANY,
                "posting_date": "2026-11-12",
                "get_items_from": "Sales Order",
                "sales_orders": [
                    {
                        "sales_order": so.name,
                        "sales_order_date": so.transaction_date,
                        "customer": cust,
                        "grand_total": so.grand_total,
                    }
                ],
                "po_items": [
                    {
                        "item_code": "FG-FRIDGE-16FT",
                        "bom_no": bom_fridge.name,
                        "planned_qty": 3,
                        "warehouse": WH_FG,
                        "sales_order": so.name,
                        "sales_order_item": so.items[0].name,
                    },
                    {
                        "item_code": "FG-STOVE-5B-90",
                        "bom_no": bom_stove.name,
                        "planned_qty": 4,
                        "warehouse": WH_FG,
                        "sales_order": so.name,
                        "sales_order_item": so.items[1].name,
                    },
                ],
            }
        )
        pp.insert(ignore_permissions=True)
        pp.submit()
        summary["sales_order"] = so.name
        summary["production_plan"] = pp.name

        # 8. Work Orders (3 completed + 1 open for live demo)
        wo1_res = execute_work_order(
            item_code="SA-FRIDGE-CAB-16",
            bom_no=bom_cab.name,
            qty=3,
            fg_warehouse=WH_WIP,
            planned_date="2026-11-14",
            transfer_date="2026-11-14",
            finish_date="2026-11-14",
            default_source=WH_RM,
            use_multi_level_bom=0,
            complete=True,
        )
        wo2_res = execute_work_order(
            item_code="FG-FRIDGE-16FT",
            bom_no=bom_fridge.name,
            qty=3,
            fg_warehouse=WH_FG,
            planned_date="2026-11-16",
            transfer_date="2026-11-16",
            finish_date="2026-11-16",
            source_map={"SA-FRIDGE-CAB-16": WH_WIP},
            default_source=WH_RM,
            use_multi_level_bom=0,
            sales_order=so.name,
            production_plan=pp.name,
            production_plan_item=pp.po_items[0].name,
            complete=True,
            qc_item_code="FG-FRIDGE-16FT",
        )
        wo3_res = execute_work_order(
            item_code="FG-STOVE-5B-90",
            bom_no=bom_stove.name,
            qty=2,
            fg_warehouse=WH_FG,
            planned_date="2026-11-17",
            transfer_date="2026-11-17",
            finish_date="2026-11-17",
            default_source=WH_RM,
            use_multi_level_bom=0,
            sales_order=so.name,
            production_plan=pp.name,
            production_plan_item=pp.po_items[1].name,
            complete=True,
        )
        wo4_res = execute_work_order(
            item_code="FG-STOVE-5B-90",
            bom_no=bom_stove.name,
            qty=2,
            fg_warehouse=WH_FG,
            planned_date="2026-11-24",
            transfer_date="2026-11-24",
            finish_date="2026-11-24",
            default_source=WH_RM,
            use_multi_level_bom=0,
            sales_order=so.name,
            production_plan=pp.name,
            production_plan_item=pp.po_items[1].name,
            complete=False,
        )
        summary["work_orders"] = {
            "wo1_sub_assembly": wo1_res,
            "wo2_fridge_completed": wo2_res,
            "wo3_stove_completed": wo3_res,
            "wo4_stove_open": wo4_res,
        }

        # 9. Sheet Metal Scrap Entry (2026-11-18)
        se_scrap = frappe.get_doc(
            {
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Receipt",
                "company": COMPANY,
                "set_posting_time": 1,
                "posting_date": "2026-11-18",
                "posting_time": "14:00:00",
                "to_warehouse": WH_SCRAP,
                "items": [
                    {"item_code": "SCRAP-STEEL", "qty": 6.5, "t_warehouse": WH_SCRAP, "basic_rate": 18},
                ],
            }
        )
        se_scrap.insert(ignore_permissions=True)
        se_scrap.submit()
        summary["scrap_stock_entry"] = se_scrap.name

        # 10. Serialized Dealer Delivery (2 Fridges + 1 Stove) + Invoice (2026-11-20)
        dn = make_delivery_note(so.name)
        dn.set_posting_time = 1
        dn.posting_date = "2026-11-20"
        dn.posting_time = "15:00:00"
        for it in dn.items:
            if it.item_code == "FG-FRIDGE-16FT":
                it.qty = 2
            elif it.item_code == "FG-STOVE-5B-90":
                it.qty = 1
            it.warehouse = WH_FG
            it.use_serial_batch_fields = 1
        dn.insert(ignore_permissions=True)
        dn.submit()

        si = make_si_from_dn(dn.name)
        si.set_posting_time = 1
        si.posting_date = "2026-11-20"
        si.due_date = "2026-12-20"
        si.insert(ignore_permissions=True)
        si.submit()

        summary["dealer_delivery"] = {
            "delivery_note": dn.name,
            "sales_invoice": si.name,
            "grand_total": si.grand_total,
        }

        serials = frappe.get_all(
            "Serial No",
            filters={"item_code": ["in", ["FG-FRIDGE-16FT", "FG-STOVE-5B-90"]]},
            fields=["name", "item_code", "status", "warehouse", "warranty_expiry_date"],
            order_by="name asc",
        )
        summary["serial_numbers"] = serials

        frappe.db.commit()
        print(json.dumps(summary, indent=2, default=str))
    except Exception:
        frappe.db.rollback()
        raise
    finally:
        frappe.destroy()


if __name__ == "__main__":
    run_seed()
