import json
import os

os.chdir("/home/frappe/frappe-bench/sites")

import frappe

SITE = os.environ.get("ERPNEXT_SITE", "frontend")
PASSWORD = os.environ.get("ERPNEXT_DEMO_USER_PASSWORD", "Factory@2026")
COMPANY = None
ABBR = None


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
            frappe.db.rollback()

        if not frappe.db.exists("Company", company_name) and not frappe.get_all("Company", limit=1):
            try:
                from frappe.desk.page.setup_wizard.install_fixtures import install as install_frappe_fixtures

                install_frappe_fixtures(country)
            except Exception:
                pass
            from erpnext.setup.setup_wizard.setup_wizard import setup_complete as erpnext_setup_complete

            erpnext_setup_complete(frappe._dict(setup_args))
            frappe.db.set_single_value("System Settings", "setup_complete", 1)
            frappe.db.commit()
        company = frappe.db.get_value("Company", {"company_name": company_name}, "name") or company_name

    abbr = frappe.db.get_value("Company", company, "abbr") or "test"
    valuation_account = (
        frappe.db.get_value(
            "Account", {"company": company, "account_type": "Expenses Included In Valuation", "is_group": 0}, "name"
        )
        or f"Expenses Included In Valuation - {abbr}"
    )
    wh_rm = (
        frappe.db.get_value("Warehouse", {"warehouse_name": "Raw Materials", "company": company}, "name")
        or f"Raw Materials - {abbr}"
    )
    return {"company": company, "abbr": abbr, "valuation_account": valuation_account, "wh_rm": wh_rm}


def ensure_role_profile(name, roles):
    if frappe.db.exists("Role Profile", name):
        return name
    valid_roles = [r for r in roles if frappe.db.exists("Role", r)]
    doc = frappe.get_doc(
        {
            "doctype": "Role Profile",
            "role_profile": name,
            "roles": [{"role": r} for r in valid_roles],
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def ensure_module_profile(name, allowed_modules):
    if frappe.db.exists("Module Profile", name):
        return name
    all_modules = frappe.get_all("Module Def", pluck="name")
    blocked = [m for m in all_modules if m not in allowed_modules]
    doc = frappe.get_doc(
        {
            "doctype": "Module Profile",
            "module_profile_name": name,
            "block_modules": [{"module": m} for m in blocked],
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def ensure_user(email, first_name, last_name, role_profile, module_profile=None):
    if frappe.db.exists("User", email):
        return email
    user_dict = {
        "doctype": "User",
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "enabled": 1,
        "user_type": "System User",
        "send_welcome_email": 0,
        "new_password": PASSWORD,
        "role_profile_name": role_profile,
    }
    if module_profile:
        user_dict["module_profile"] = module_profile
    doc = frappe.get_doc(user_dict)
    doc.insert(ignore_permissions=True)
    return doc.name


def ensure_user_permission(user, allow, for_value):
    if frappe.db.exists("User Permission", {"user": user, "allow": allow, "for_value": for_value}):
        return
    frappe.get_doc(
        {
            "doctype": "User Permission",
            "user": user,
            "allow": allow,
            "for_value": for_value,
            "apply_to_all_doctypes": 1,
        }
    ).insert(ignore_permissions=True)


def ensure_department(dept_name):
    existing = frappe.db.get_value("Department", {"department_name": dept_name, "company": COMPANY}, "name")
    if existing:
        return existing
    parent_dept = (
        frappe.db.get_value("Department", {"is_group": 1, "parent_department": ["in", ["", None]]}, "name")
        or frappe.db.get_value("Department", {"is_group": 1}, "name")
        or "All Departments"
    )
    doc = frappe.get_doc(
        {
            "doctype": "Department",
            "department_name": dept_name,
            "parent_department": parent_dept,
            "company": COMPANY,
            "is_group": 0,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def ensure_employee(first_name, last_name, user_id, department, dob="1992-05-15", doj="2024-01-10"):
    existing = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
    if existing:
        return existing
    genders = frappe.get_all("Gender", pluck="name")
    gender = "Male" if "Male" in genders else (genders[0] if genders else "Prefer not to say")
    if not frappe.db.exists("Gender", gender):
        frappe.get_doc({"doctype": "Gender", "gender": gender}).insert(ignore_permissions=True)
    doc = frappe.get_doc(
        {
            "doctype": "Employee",
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "date_of_birth": dob,
            "date_of_joining": doj,
            "status": "Active",
            "company": COMPANY,
            "department": department,
            "user_id": user_id,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def run_seed():
    global COMPANY, ABBR
    frappe.init(site=SITE)
    frappe.connect()
    frappe.set_user("Administrator")

    try:
        ctx = bootstrap_and_resolve_context()
        COMPANY = ctx["company"]
        ABBR = ctx["abbr"]
        valuation_account = ctx["valuation_account"]
        wh_rm = ctx["wh_rm"]

        summary = {"company": COMPANY, "users": [], "extras": {}}

        # 1. Role Profiles
        rp_gm = ensure_role_profile(
            "Factory General Manager",
            [
                "System Manager",
                "Accounts Manager",
                "Manufacturing Manager",
                "Stock Manager",
                "Sales Manager",
                "Purchase Manager",
                "Quality Manager",
            ],
        )
        rp_stock = ensure_role_profile("Factory Stock Keeper", ["Stock User", "Item Manager"])
        rp_prod = ensure_role_profile(
            "Factory Production Engineer",
            ["Manufacturing User", "Manufacturing Manager", "Stock User"],
        )
        rp_qc = ensure_role_profile("Factory QC Inspector", ["Quality Manager", "Stock User"])
        rp_acc = ensure_role_profile(
            "Factory Accountant",
            ["Accounts User", "Accounts Manager", "Purchase User", "Sales User"],
        )

        # 2. Module Profiles
        mp_stock = ensure_module_profile("Factory Stock Only", ["Stock", "Core", "Desk", "Utilities"])
        mp_prod = ensure_module_profile(
            "Factory Production Only", ["Manufacturing", "Stock", "Core", "Desk", "Utilities"]
        )
        mp_qc = ensure_module_profile(
            "Factory Quality Only", ["Quality Management", "Stock", "Manufacturing", "Core", "Desk"]
        )
        mp_acc = ensure_module_profile(
            "Factory Accounts Only", ["Accounts", "Selling", "Buying", "Core", "Desk", "Utilities"]
        )

        # 3. Demo Users
        users_spec = [
            ("gm@factory.local", "General", "Manager", rp_gm, None),
            ("stock@factory.local", "Warehouse", "Keeper", rp_stock, mp_stock),
            ("production@factory.local", "Production", "Engineer", rp_prod, mp_prod),
            ("qc@factory.local", "Quality", "Inspector", rp_qc, mp_qc),
            ("accounts@factory.local", "Factory", "Accountant", rp_acc, mp_acc),
        ]
        for email, fn, ln, rp, mp in users_spec:
            u = ensure_user(email, fn, ln, rp, mp)
            summary["users"].append({"email": u, "role_profile": rp, "module_profile": mp or "All Modules"})

        # Row-level restriction: restrict stock@factory.local to Raw Materials warehouse if it exists
        if frappe.db.exists("Warehouse", wh_rm):
            ensure_user_permission("stock@factory.local", "Warehouse", wh_rm)
            summary["stock_user_warehouse_restriction"] = wh_rm
        else:
            summary["stock_user_warehouse_restriction"] = "skipped (run seed_appliance_factory.py first)"

        # 4. Departments & Employees
        dept_wh = ensure_department("Warehouse")
        dept_prod = ensure_department("Production")
        dept_qc = ensure_department("Quality Management")
        employees = [
            ensure_employee("Khaled", "Mansour", "stock@factory.local", dept_wh),
            ensure_employee("Tarek", "Nabil", "production@factory.local", dept_prod),
            ensure_employee("Nourhan", "Adel", "qc@factory.local", dept_qc),
        ]
        summary["extras"]["employees"] = employees

        # 5. Warranty Claim on first delivered Serial No of FG-FRIDGE-16FT (if seeded)
        fridge_serials = frappe.get_all(
            "Serial No",
            filters={"item_code": "FG-FRIDGE-16FT"},
            pluck="name",
            order_by="creation asc",
            limit=1,
        )
        if fridge_serials and frappe.db.exists("Customer", "El-Araby Home Appliances Dealers"):
            serial_no = fridge_serials[0]
            existing_wc = frappe.get_all("Warranty Claim", filters={"serial_no": serial_no}, pluck="name")
            if existing_wc:
                summary["extras"]["warranty_claim"] = existing_wc[0]
            else:
                wc = frappe.get_doc(
                    {
                        "doctype": "Warranty Claim",
                        "company": COMPANY,
                        "customer": "El-Araby Home Appliances Dealers",
                        "serial_no": serial_no,
                        "item_code": "FG-FRIDGE-16FT",
                        "complaint_date": "2026-11-25",
                        "status": "Open",
                        "complaint": "Thermostat cooling calibration check requested by dealer before display.",
                    }
                )
                wc.insert(ignore_permissions=True)
                summary["extras"]["warranty_claim"] = wc.name
        else:
            summary["extras"]["warranty_claim"] = "skipped (run seed_appliance_factory.py first)"

        # 6. Landed Cost Voucher on latest submitted Purchase Receipt for Misr Steel & Cooling Components
        factory_prs = frappe.get_all(
            "Purchase Receipt",
            filters={
                "company": COMPANY,
                "supplier": "Misr Steel & Cooling Components",
                "docstatus": 1,
            },
            fields=["name", "grand_total"],
            order_by="posting_date desc, creation desc",
            limit=1,
        )
        if factory_prs and frappe.db.exists("Account", valuation_account):
            pr_doc = factory_prs[0]
            existing_lcv = frappe.db.get_value(
                "Landed Cost Purchase Receipt",
                {"receipt_document": pr_doc.name, "docstatus": 1},
                "parent",
            )
            if existing_lcv:
                summary["extras"]["landed_cost_voucher"] = existing_lcv
            else:
                lcv = frappe.get_doc(
                    {
                        "doctype": "Landed Cost Voucher",
                        "company": COMPANY,
                        "posting_date": "2026-11-02",
                        "distribute_charges_based_on": "Amount",
                        "purchase_receipts": [
                            {
                                "receipt_document_type": "Purchase Receipt",
                                "receipt_document": pr_doc.name,
                                "supplier": "Misr Steel & Cooling Components",
                                "grand_total": pr_doc.grand_total,
                            }
                        ],
                        "taxes": [
                            {
                                "expense_account": valuation_account,
                                "description": "Import Customs Clearance",
                                "amount": 12000.0,
                            },
                            {
                                "expense_account": valuation_account,
                                "description": "Port Freight & Handling",
                                "amount": 4500.0,
                            },
                        ],
                    }
                )
                lcv.get_items_from_purchase_receipts()
                lcv.insert(ignore_permissions=True)
                lcv.submit()
                summary["extras"]["landed_cost_voucher"] = lcv.name
        else:
            summary["extras"]["landed_cost_voucher"] = "skipped (run seed_appliance_factory.py first)"

        frappe.db.commit()
        print(json.dumps(summary, indent=2, default=str))
    except Exception:
        frappe.db.rollback()
        raise
    finally:
        frappe.destroy()


if __name__ == "__main__":
    run_seed()
