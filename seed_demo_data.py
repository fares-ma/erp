import json
import os
import sys

os.chdir("/home/frappe/frappe-bench/sites")

import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
from erpnext.selling.doctype.quotation.quotation import make_sales_order
from erpnext.selling.doctype.sales_order.sales_order import (
    make_delivery_note,
    make_sales_invoice as make_si_from_so,
)
from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice as make_si_from_dn
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice

SITE = os.environ.get("ERPNEXT_SITE", "frontend")


def ensure_master_prereqs(company, currency):
    if not frappe.db.exists("UOM", "Nos"):
        frappe.get_doc({"doctype": "UOM", "uom_name": "Nos"}).insert(ignore_permissions=True)

    root_territory = frappe.db.get_value("Territory", {"is_group": 1}, "name") or "All Territories"
    if not frappe.db.exists("Territory", "Egypt"):
        frappe.get_doc(
            {"doctype": "Territory", "territory_name": "Egypt", "parent_territory": root_territory, "is_group": 0}
        ).insert(ignore_permissions=True)

    root_sup_group = frappe.db.get_value("Supplier Group", {"is_group": 1}, "name") or "All Supplier Groups"
    for sg in ("Distributor", "Hardware", "Local"):
        if not frappe.db.exists("Supplier Group", sg):
            frappe.get_doc(
                {"doctype": "Supplier Group", "supplier_group_name": sg, "parent_supplier_group": root_sup_group}
            ).insert(ignore_permissions=True)

    root_cust_group = frappe.db.get_value("Customer Group", {"is_group": 1}, "name") or "All Customer Groups"
    for cg in ("Commercial", "Individual"):
        if not frappe.db.exists("Customer Group", cg):
            frappe.get_doc(
                {"doctype": "Customer Group", "customer_group_name": cg, "parent_customer_group": root_cust_group}
            ).insert(ignore_permissions=True)

    root_item_group = frappe.db.get_value("Item Group", {"is_group": 1}, "name") or "All Item Groups"
    for ig in ("Products", "Consumable", "Services"):
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

    if not frappe.db.exists("Mode of Payment", "Cash"):
        frappe.get_doc({"doctype": "Mode of Payment", "mode_of_payment": "Cash", "type": "Cash"}).insert(
            ignore_permissions=True
        )

    fy_exists = frappe.db.sql(
        """
        SELECT name FROM `tabFiscal Year`
        WHERE disabled = 0 AND year_start_date <= '2026-10-01' AND year_end_date >= '2026-12-31'
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

    root_wh = (
        frappe.db.get_value(
            "Warehouse", {"company": company, "is_group": 1, "parent_warehouse": ["in", ["", None]]}, "name"
        )
        or frappe.db.get_value("Warehouse", {"company": company, "is_group": 1}, "name")
        or f"All Warehouses - {abbr}"
    )

    def _ensure_wh(wh_name):
        existing = frappe.db.get_value("Warehouse", {"warehouse_name": wh_name, "company": company}, "name")
        if existing:
            return existing
        doc = frappe.get_doc(
            {
                "doctype": "Warehouse",
                "warehouse_name": wh_name,
                "parent_warehouse": root_wh,
                "company": company,
                "is_group": 0,
            }
        )
        doc.insert(ignore_permissions=True)
        return doc.name

    wh_stores = _ensure_wh("Stores")
    wh_fg = _ensure_wh("Finished Goods")
    cost_center = (
        frappe.db.get_value("Company", company, "cost_center")
        or frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")
        or f"Main - {abbr}"
    )
    cash_account = (
        frappe.db.get_value("Account", {"company": company, "account_type": "Cash", "is_group": 0}, "name")
        or frappe.db.get_value("Account", {"company": company, "account_type": "Bank", "is_group": 0}, "name")
        or f"Cash - {abbr}"
    )
    return {
        "company": company,
        "abbr": abbr,
        "currency": currency,
        "cost_center": cost_center,
        "wh_stores": wh_stores,
        "wh_fg": wh_fg,
        "cash_account": cash_account,
    }


COMPANY = None
CURRENCY = None
COST_CENTER = None
WH_STORES = None
WH_FG = None
CASH_ACCOUNT = None


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


def ensure_customer(name, customer_group, customer_type="Company", territory="Egypt"):
    if frappe.db.exists("Customer", name):
        return name
    doc = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": name,
            "customer_group": customer_group,
            "customer_type": customer_type,
            "territory": territory,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def ensure_item(code, item_name, item_group, is_stock_item, buy_rate=None, sell_rate=None):
    if not frappe.db.exists("Item", code):
        uom = "Nos" if frappe.db.exists("UOM", "Nos") else frappe.get_all("UOM", limit=1, pluck="name")[0]
        doc = frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": code,
                "item_name": item_name,
                "item_group": item_group,
                "stock_uom": uom,
                "is_stock_item": is_stock_item,
                "include_item_in_manufacturing": 0,
                "standard_rate": sell_rate or 0,
                "item_defaults": [
                    {
                        "company": COMPANY,
                        "default_warehouse": WH_STORES if is_stock_item else None,
                    }
                ],
            }
        )
        doc.insert(ignore_permissions=True)

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


def run_seed():
    global COMPANY, CURRENCY, COST_CENTER, WH_STORES, WH_FG, CASH_ACCOUNT
    frappe.init(site=SITE)
    frappe.connect()
    frappe.set_user("Administrator")

    try:
        ctx = bootstrap_and_resolve_context()
        COMPANY = ctx["company"]
        CURRENCY = ctx["currency"]
        COST_CENTER = ctx["cost_center"]
        WH_STORES = ctx["wh_stores"]
        WH_FG = ctx["wh_fg"]
        CASH_ACCOUNT = ctx["cash_account"]

        if frappe.db.exists("Item", "DEMO-LAPTOP-01"):
            print("ALREADY_SEEDED")
            return

        summary = {"company": COMPANY, "currency": CURRENCY}

        # 1. Opening Cash Capital (Journal Entry, 2026-10-01)
        equity_accounts = frappe.get_all(
            "Account",
            filters={"company": COMPANY, "root_type": "Equity", "is_group": 0},
            pluck="name",
        )
        equity_acc = None
        for acc in equity_accounts:
            if any(k in acc for k in ("Capital", "Share", "Owner", "Opening")):
                equity_acc = acc
                break
        if not equity_acc and equity_accounts:
            equity_acc = equity_accounts[0]

        if equity_acc:
            je = frappe.get_doc(
                {
                    "doctype": "Journal Entry",
                    "voucher_type": "Opening Entry",
                    "company": COMPANY,
                    "posting_date": "2026-10-01",
                    "user_remark": "Demo opening capital in Cash",
                    "accounts": [
                        {
                            "account": CASH_ACCOUNT,
                            "debit_in_account_currency": 500000,
                            "cost_center": COST_CENTER,
                        },
                        {
                            "account": equity_acc,
                            "credit_in_account_currency": 500000,
                            "cost_center": COST_CENTER,
                        },
                    ],
                }
            )
            je.insert(ignore_permissions=True)
            je.submit()
            summary["opening_journal_entry"] = je.name

        # 2. Masters: Suppliers, Customers, Items
        suppliers = [
            ensure_supplier("Egypt Electronics Distributor", "Distributor"),
            ensure_supplier("Smart Hardware Imports", "Hardware"),
            ensure_supplier("Al-Amal Tech Supplies", "Local"),
        ]
        customers = [
            ensure_customer("Nile Tech Solutions", "Commercial", "Company"),
            ensure_customer("Cairo Modern Trading", "Commercial", "Company"),
            ensure_customer("Delta Retail Group", "Commercial", "Company"),
            ensure_customer("Ahmed Hassan", "Individual", "Individual"),
        ]
        items_spec = [
            ("DEMO-LAPTOP-01", "Dell Latitude 5540 Laptop", "Products", 1, 28000, 35000),
            ("DEMO-MON-27", 'Dell 27" IPS Monitor', "Products", 1, 8500, 11000),
            ("DEMO-KB-MECH", "Mechanical Keyboard", "Products", 1, 1400, 2100),
            ("DEMO-MOUSE-WL", "Wireless Ergonomic Mouse", "Products", 1, 650, 950),
            ("DEMO-HUB-USBC", "USB-C Multiport Hub", "Consumable", 1, 900, 1400),
            ("DEMO-SVC-SETUP", "IT Workstation Setup & Support", "Services", 0, None, 2500),
        ]
        for row in items_spec:
            ensure_item(*row)

        summary["suppliers"] = suppliers
        summary["customers"] = customers
        summary["items"] = [r[0] for r in items_spec]

        # 3. Opening Stock (Stock Entry - Material Receipt, 2026-10-02)
        se_open = frappe.get_doc(
            {
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Receipt",
                "company": COMPANY,
                "set_posting_time": 1,
                "posting_date": "2026-10-02",
                "posting_time": "09:00:00",
                "to_warehouse": WH_STORES,
                "items": [
                    {"item_code": "DEMO-LAPTOP-01", "qty": 5, "t_warehouse": WH_STORES, "basic_rate": 28000},
                    {"item_code": "DEMO-MON-27", "qty": 8, "t_warehouse": WH_STORES, "basic_rate": 8500},
                    {"item_code": "DEMO-KB-MECH", "qty": 15, "t_warehouse": WH_STORES, "basic_rate": 1400},
                    {"item_code": "DEMO-MOUSE-WL", "qty": 20, "t_warehouse": WH_STORES, "basic_rate": 650},
                    {"item_code": "DEMO-HUB-USBC", "qty": 15, "t_warehouse": WH_STORES, "basic_rate": 900},
                ],
            }
        )
        se_open.insert(ignore_permissions=True)
        se_open.submit()
        summary["opening_stock_entry"] = se_open.name

        # 4. Buying Flow #1 (MR -> PO -> PR -> PI -> Payment Entry [Paid])
        mr1 = frappe.get_doc(
            {
                "doctype": "Material Request",
                "material_request_type": "Purchase",
                "company": COMPANY,
                "transaction_date": "2026-10-05",
                "schedule_date": "2026-10-12",
                "items": [
                    {"item_code": "DEMO-LAPTOP-01", "qty": 10, "schedule_date": "2026-10-12", "warehouse": WH_STORES},
                    {"item_code": "DEMO-MON-27", "qty": 10, "schedule_date": "2026-10-12", "warehouse": WH_STORES},
                ],
            }
        )
        mr1.insert(ignore_permissions=True)
        mr1.submit()

        po1 = frappe.get_doc(
            {
                "doctype": "Purchase Order",
                "company": COMPANY,
                "supplier": "Egypt Electronics Distributor",
                "transaction_date": "2026-10-06",
                "schedule_date": "2026-10-12",
                "currency": CURRENCY,
                "items": [
                    {
                        "item_code": "DEMO-LAPTOP-01",
                        "qty": 10,
                        "rate": 28000,
                        "schedule_date": "2026-10-12",
                        "warehouse": WH_STORES,
                        "material_request": mr1.name,
                        "material_request_item": mr1.items[0].name,
                    },
                    {
                        "item_code": "DEMO-MON-27",
                        "qty": 10,
                        "rate": 8500,
                        "schedule_date": "2026-10-12",
                        "warehouse": WH_STORES,
                        "material_request": mr1.name,
                        "material_request_item": mr1.items[1].name,
                    },
                ],
            }
        )
        po1.insert(ignore_permissions=True)
        po1.submit()

        pr1 = make_purchase_receipt(po1.name)
        pr1.set_posting_time = 1
        pr1.posting_date = "2026-10-10"
        pr1.posting_time = "11:00:00"
        pr1.insert(ignore_permissions=True)
        pr1.submit()

        pi1 = make_purchase_invoice(pr1.name)
        pi1.set_posting_time = 1
        pi1.posting_date = "2026-10-11"
        pi1.due_date = "2026-10-26"
        pi1.bill_no = "SUP-INV-1001"
        pi1.bill_date = "2026-10-11"
        pi1.insert(ignore_permissions=True)
        pi1.submit()

        pe_buy1 = get_payment_entry("Purchase Invoice", pi1.name, bank_account=CASH_ACCOUNT)
        pe_buy1.posting_date = "2026-10-14"
        pe_buy1.mode_of_payment = "Cash"
        pe_buy1.reference_no = "PAY-SUP-001"
        pe_buy1.reference_date = "2026-10-14"
        pe_buy1.insert(ignore_permissions=True)
        pe_buy1.submit()

        summary["buying_flow_1_paid"] = {
            "material_request": mr1.name,
            "purchase_order": po1.name,
            "purchase_receipt": pr1.name,
            "purchase_invoice": pi1.name,
            "payment_entry": pe_buy1.name,
            "grand_total": pi1.grand_total,
        }

        # 5. Buying Flow #2 (PO -> PR -> PI [Unpaid])
        po2 = frappe.get_doc(
            {
                "doctype": "Purchase Order",
                "company": COMPANY,
                "supplier": "Smart Hardware Imports",
                "transaction_date": "2026-11-02",
                "schedule_date": "2026-11-06",
                "currency": CURRENCY,
                "items": [
                    {"item_code": "DEMO-KB-MECH", "qty": 20, "rate": 1400, "schedule_date": "2026-11-06", "warehouse": WH_STORES},
                    {"item_code": "DEMO-MOUSE-WL", "qty": 30, "rate": 650, "schedule_date": "2026-11-06", "warehouse": WH_STORES},
                    {"item_code": "DEMO-HUB-USBC", "qty": 20, "rate": 900, "schedule_date": "2026-11-06", "warehouse": WH_STORES},
                ],
            }
        )
        po2.insert(ignore_permissions=True)
        po2.submit()

        pr2 = make_purchase_receipt(po2.name)
        pr2.set_posting_time = 1
        pr2.posting_date = "2026-11-05"
        pr2.posting_time = "10:00:00"
        pr2.insert(ignore_permissions=True)
        pr2.submit()

        pi2 = make_purchase_invoice(pr2.name)
        pi2.set_posting_time = 1
        pi2.posting_date = "2026-11-06"
        pi2.due_date = "2026-12-06"
        pi2.bill_no = "SH-2026-88"
        pi2.bill_date = "2026-11-06"
        pi2.insert(ignore_permissions=True)
        pi2.submit()

        summary["buying_flow_2_unpaid"] = {
            "purchase_order": po2.name,
            "purchase_receipt": pr2.name,
            "purchase_invoice": pi2.name,
            "grand_total": pi2.grand_total,
        }

        # 6. Buying Flow #3 (Open PO - To Receive and Bill)
        po3 = frappe.get_doc(
            {
                "doctype": "Purchase Order",
                "company": COMPANY,
                "supplier": "Al-Amal Tech Supplies",
                "transaction_date": "2026-11-22",
                "schedule_date": "2026-11-30",
                "currency": CURRENCY,
                "items": [
                    {"item_code": "DEMO-LAPTOP-01", "qty": 4, "rate": 28000, "schedule_date": "2026-11-30", "warehouse": WH_STORES},
                ],
            }
        )
        po3.insert(ignore_permissions=True)
        po3.submit()
        summary["buying_flow_3_open_po"] = po3.name

        # 7. Internal Stock Transfer (Stores -> Finished Goods, 2026-11-08)
        se_transfer = frappe.get_doc(
            {
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Transfer",
                "company": COMPANY,
                "set_posting_time": 1,
                "posting_date": "2026-11-08",
                "posting_time": "12:00:00",
                "from_warehouse": WH_STORES,
                "to_warehouse": WH_FG,
                "items": [
                    {"item_code": "DEMO-LAPTOP-01", "qty": 2, "s_warehouse": WH_STORES, "t_warehouse": WH_FG},
                    {"item_code": "DEMO-MON-27", "qty": 2, "s_warehouse": WH_STORES, "t_warehouse": WH_FG},
                ],
            }
        )
        se_transfer.insert(ignore_permissions=True)
        se_transfer.submit()
        summary["stock_transfer_entry"] = se_transfer.name

        # 8. Selling Flow #1 (Quotation -> SO -> DN -> SI -> Payment Entry [Paid])
        qtn1 = frappe.get_doc(
            {
                "doctype": "Quotation",
                "quotation_to": "Customer",
                "party_name": "Nile Tech Solutions",
                "company": COMPANY,
                "transaction_date": "2026-10-15",
                "valid_till": "2026-12-30",
                "currency": CURRENCY,
                "items": [
                    {"item_code": "DEMO-LAPTOP-01", "qty": 4, "rate": 35000, "warehouse": WH_STORES},
                    {"item_code": "DEMO-MON-27", "qty": 4, "rate": 11000, "warehouse": WH_STORES},
                    {"item_code": "DEMO-SVC-SETUP", "qty": 2, "rate": 2500},
                ],
            }
        )
        qtn1.insert(ignore_permissions=True)
        qtn1.submit()

        so1 = make_sales_order(qtn1.name)
        so1.transaction_date = "2026-10-17"
        so1.delivery_date = "2026-10-22"
        for it in so1.items:
            if it.item_code != "DEMO-SVC-SETUP":
                it.warehouse = WH_STORES
            it.delivery_date = "2026-10-22"
        so1.insert(ignore_permissions=True)
        so1.submit()

        dn1 = make_delivery_note(so1.name)
        dn1.set_posting_time = 1
        dn1.posting_date = "2026-10-20"
        dn1.posting_time = "14:00:00"
        dn1.insert(ignore_permissions=True)
        dn1.submit()

        si1 = make_si_from_so(so1.name)
        si1.set_posting_time = 1
        si1.posting_date = "2026-10-21"
        si1.due_date = "2026-11-05"
        si1.update_stock = 0
        dn_item_map = {d.so_detail: d.name for d in dn1.items if d.so_detail}
        for it in si1.items:
            if it.so_detail and it.so_detail in dn_item_map:
                it.delivery_note = dn1.name
                it.dn_detail = dn_item_map[it.so_detail]
        si1.insert(ignore_permissions=True)
        si1.submit()

        pe_sell1 = get_payment_entry("Sales Invoice", si1.name, bank_account=CASH_ACCOUNT)
        pe_sell1.posting_date = "2026-10-25"
        pe_sell1.mode_of_payment = "Cash"
        pe_sell1.reference_no = "REC-CUS-001"
        pe_sell1.reference_date = "2026-10-25"
        pe_sell1.insert(ignore_permissions=True)
        pe_sell1.submit()

        summary["selling_flow_1_paid"] = {
            "quotation": qtn1.name,
            "sales_order": so1.name,
            "delivery_note": dn1.name,
            "sales_invoice": si1.name,
            "payment_entry": pe_sell1.name,
            "grand_total": si1.grand_total,
        }

        # 9. Selling Flow #2 (SO -> DN -> SI [Unpaid])
        so2 = frappe.get_doc(
            {
                "doctype": "Sales Order",
                "customer": "Cairo Modern Trading",
                "company": COMPANY,
                "transaction_date": "2026-11-10",
                "delivery_date": "2026-11-15",
                "currency": CURRENCY,
                "items": [
                    {"item_code": "DEMO-LAPTOP-01", "qty": 3, "rate": 35000, "delivery_date": "2026-11-15", "warehouse": WH_STORES},
                    {"item_code": "DEMO-KB-MECH", "qty": 10, "rate": 2100, "delivery_date": "2026-11-15", "warehouse": WH_STORES},
                    {"item_code": "DEMO-MOUSE-WL", "qty": 10, "rate": 950, "delivery_date": "2026-11-15", "warehouse": WH_STORES},
                ],
            }
        )
        so2.insert(ignore_permissions=True)
        so2.submit()

        dn2 = make_delivery_note(so2.name)
        dn2.set_posting_time = 1
        dn2.posting_date = "2026-11-14"
        dn2.posting_time = "13:00:00"
        dn2.insert(ignore_permissions=True)
        dn2.submit()

        si2 = make_si_from_dn(dn2.name)
        si2.set_posting_time = 1
        si2.posting_date = "2026-11-15"
        si2.due_date = "2026-12-15"
        si2.insert(ignore_permissions=True)
        si2.submit()

        summary["selling_flow_2_unpaid"] = {
            "sales_order": so2.name,
            "delivery_note": dn2.name,
            "sales_invoice": si2.name,
            "grand_total": si2.grand_total,
        }

        # 10. Selling Flow #3 (Open SO - To Deliver and Bill) + Draft Sales Invoice
        so3 = frappe.get_doc(
            {
                "doctype": "Sales Order",
                "customer": "Delta Retail Group",
                "company": COMPANY,
                "transaction_date": "2026-11-23",
                "delivery_date": "2026-12-01",
                "currency": CURRENCY,
                "items": [
                    {"item_code": "DEMO-MON-27", "qty": 3, "rate": 11000, "delivery_date": "2026-12-01", "warehouse": WH_STORES},
                    {"item_code": "DEMO-HUB-USBC", "qty": 10, "rate": 1400, "delivery_date": "2026-12-01", "warehouse": WH_STORES},
                ],
            }
        )
        so3.insert(ignore_permissions=True)
        so3.submit()

        si_draft = frappe.get_doc(
            {
                "doctype": "Sales Invoice",
                "customer": "Ahmed Hassan",
                "company": COMPANY,
                "set_posting_time": 1,
                "posting_date": "2026-11-24",
                "due_date": "2026-11-30",
                "currency": CURRENCY,
                "update_stock": 1,
                "items": [
                    {"item_code": "DEMO-MOUSE-WL", "qty": 2, "rate": 950, "warehouse": WH_STORES},
                ],
            }
        )
        si_draft.insert(ignore_permissions=True)

        summary["selling_flow_3_open_so"] = so3.name
        summary["draft_sales_invoice"] = si_draft.name

        # 11. CRM Leads & Project/Tasks
        lead1 = frappe.get_doc(
            {
                "doctype": "Lead",
                "first_name": "Omar",
                "last_name": "Khaled",
                "company_name": "Future Systems",
                "email_id": "omar.khaled@example.com",
                "status": "Open",
            }
        )
        lead1.insert(ignore_permissions=True)

        lead2 = frappe.get_doc(
            {
                "doctype": "Lead",
                "first_name": "Sara",
                "last_name": "Mahmoud",
                "company_name": "Horizon Media",
                "email_id": "sara.mahmoud@example.com",
                "status": "Interested",
            }
        )
        lead2.insert(ignore_permissions=True)

        proj = frappe.get_doc(
            {
                "doctype": "Project",
                "project_name": "Office IT Rollout - Nile Tech",
                "company": COMPANY,
                "customer": "Nile Tech Solutions",
                "sales_order": so1.name,
                "status": "Open",
                "expected_start_date": "2026-10-18",
                "expected_end_date": "2026-12-10",
            }
        )
        proj.insert(ignore_permissions=True)

        tasks_spec = [
            ("Hardware Procurement", "Completed", "2026-10-18", "2026-10-20"),
            ("Workstation Installation", "Working", "2026-10-21", "2026-11-30"),
            ("User Training & Handover", "Open", "2026-12-01", "2026-12-10"),
        ]
        task_names = []
        for subj, status, start_d, end_d in tasks_spec:
            t = frappe.get_doc(
                {
                    "doctype": "Task",
                    "subject": subj,
                    "project": proj.name,
                    "company": COMPANY,
                    "status": status,
                    "exp_start_date": start_d,
                    "exp_end_date": end_d,
                }
            )
            t.insert(ignore_permissions=True)
            task_names.append(t.name)

        summary["leads"] = [lead1.name, lead2.name]
        summary["project"] = proj.name
        summary["tasks"] = task_names

        frappe.db.commit()
        print(json.dumps(summary, indent=2, default=str))
    except Exception:
        frappe.db.rollback()
        raise
    finally:
        frappe.destroy()


if __name__ == "__main__":
    run_seed()
