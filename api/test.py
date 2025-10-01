import frappe
from frappe.model.document import Document
from erpnext.manufacturing.doctype.bom.bom import get_bom_items_as_dict


def get_default_warehouse(item_code, company, fallback=None):
    """Fetch default warehouse for an item or return fallback."""
    return frappe.db.get_value("Item Default", {
        "parent": item_code,
        "company": company
    }, "default_warehouse") or fallback


def after_submit(doc, method):
    if not (doc.is_return and doc.update_stock):
        return

    default_wastage_acc = frappe.db.get_value(
        "Company", {"name": doc.company}, "custom_default_wastage_account")

    for si_item in doc.items:
        if not frappe.db.get_value("Item", si_item.item_code, "is_stock_item"):
            continue

        # Get default BOM
        bom = frappe.db.get_value("BOM", {
            "item": si_item.item_code,
            "is_default": 1,
            "is_active": 1
        })
        if not bom:
            frappe.msgprint(f"No BOM found for item {si_item.item_code}")
            continue

        # Get BOM quantity (important for ratio calculations)
        bom_qty = frappe.db.get_value("BOM", bom, "quantity") or 1
        if bom_qty == 0:
            frappe.throw(
                f"BOM quantity is 0 for BOM {bom}. Cannot create Stock Entry.")

        # Create Stock Entry (Repack)
        se = frappe.new_doc("Stock Entry")
        se.update({
            "purpose": "Disassemble",
            "stock_entry_type": "Disassemble",
            "company": doc.company,
            "set_posting_time": 1,
            "posting_date": doc.posting_date,
            "posting_time": doc.posting_time,
            "from_bom": 1,
            "bom_no": bom,
            "use_multi_level_bom": 1,
            "fg_completed_qty": abs(si_item.qty),
            "remark": f"De-assembled from Sales Invoice Return {doc.name}"
        })

        # Add FG item (returned item)
        se.append("items", {
            "item_code": si_item.item_code,
            "qty": abs(si_item.qty),
            "s_warehouse": si_item.warehouse,
            "is_finished_item": 1,
            "expense_account": default_wastage_acc
        })

        # Add Scrap Items if any
        scrap_items = frappe.get_all("BOM Scrap Item", filters={"parent": bom}, fields=[
                                     "item_code", "stock_qty", "rate"])
        for scrap in scrap_items:
            rate = scrap.rate
            s_warehouse = get_default_warehouse(
                scrap.item_code, doc.company, fallback=si_item.warehouse)

            # Calculate the required qty for this scrap item
            required_qty = (scrap.stock_qty / bom_qty) * abs(si_item.qty)

            se.append("items", {
                "item_code": scrap.item_code,
                "qty": required_qty,
                "s_warehouse": s_warehouse,
                "basic_rate": rate,
                "valuation_rate": rate,
                "is_scrap_item": 1,
                "expense_account": default_wastage_acc
            })

        # Add BOM raw materials
        bom_items = get_bom_items_as_dict(
            bom, company=doc.company, qty=abs(si_item.qty), fetch_exploded=1
        )

        for item_code, bom_item in bom_items.items():
            # Skip if Item Group is Consumables
            item_group = frappe.db.get_value("Item", item_code, "item_group")
            if item_group == "Consumables":
                continue

            se.append("items", {
                "item_code": item_code,
                "qty": bom_item["qty"],
                "basic_rate": bom_item["rate"],
                "t_warehouse": get_default_warehouse(item_code, doc.company, fallback=si_item.warehouse),
                "is_finished_item": 0,
                "expense_account": default_wastage_acc
            })

        se.insert(ignore_permissions=True)
        se.custom_sales_invoice_reference = doc.name
        for i in se.items:
            if not i.is_scrap_item:
                if not i.is_finished_item:
                    rate = i.basic_rate
        for i in se.items:
            if i.is_scrap_item:
                i.valuation_rate = rate
                i.basic_rate = rate
        se.submit()

        for item in se.items:
            if item.is_scrap_item and item.item_code:
                scrap_items = frappe.get_all("BOM Scrap Item", filters={"parent": bom}, fields=[
                                             "item_code", "stock_qty", "rate"])
                for scrap in scrap_items:
                    custom_rate = scrap.rate or 0
                    frappe.db.set_value("Stock Entry Detail", item.name, {
                        "basic_rate": custom_rate,
                        "valuation_rate": custom_rate
                    })

    frappe.msgprint(f"Disassemble Stock Entries Created Successfully.")


def on_cancel(doc, method):
    # Cancel and unlink stock entries when Sales Invoice is cancelled.
    stock_entries = frappe.get_all(
        "Stock Entry",
        filters={"custom_sales_invoice_reference": doc.name},
        fields=["name", "docstatus"]
    )

    for se in stock_entries:
        try:
            se_doc = frappe.get_doc("Stock Entry", se.name)

            if se.docstatus == 1:  # Submitted
                se_doc.cancel()

            elif se.docstatus in (0, 2):  # Draft or Cancelled
                se_doc.delete()

            # unlink reference
            frappe.db.set_value("Stock Entry", se.name,
                                "custom_sales_invoice_reference", None)

        except Exception as e:
            frappe.log_error(frappe.get_traceback(),
                             f"Failed to cancel Stock Entry {se.name}")

    frappe.msgprint(
        f"Unlinked and cancelled {len(stock_entries)} Stock Entry(ies) for {doc.name}")


def before_submit(doc, method):
    if doc.is_return:
        # Fetch Sales Return Account from the Company doctype
        sales_return_account = frappe.db.get_value(
            'Company',
            doc.company,
            'custom_sales_return_account'
        )

        if sales_return_account:
            for item in doc.items:
                item.income_account = sales_return_account