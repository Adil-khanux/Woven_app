# Copyright (c) 2025, hitc technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TechnicalSpecsType(Document):
	pass


@frappe.whitelist()
def create_technical_specs():
    """
    Create Technical Specs Type docs for each selected field in Matrix Settings.

    Features:
    - Main Item Select and Link fields
    - Child table Select and Link fields
    - Tracks source field labels
    - Skips blank/None options
    - Prevents duplicates
    - Logs empty or missing options for debugging
    """    
    matrix_doc = frappe.get_single("Matrix Settings")
    created = []

    if not matrix_doc.data_qynq:
        return "No fields selected in Matrix Settings."

    item_meta = frappe.get_meta("Item")

    # Track existing options to prevent duplicates
    existing_options = set()
    for doc in frappe.get_all("Technical Specs Type", fields=["name1", "source_field"]):
        existing_options.add((doc.name1, doc.source_field))

    def process_options(options_list, source_label):
        """Insert options into Technical Specs Type, skip blanks and duplicates"""
        if not options_list:
            return
        for opt in options_list:
            opt = (opt or "").strip()
            if opt:
                key = (opt, source_label)
                if key not in existing_options:
                    doc = frappe.get_doc({
                        "doctype": "Technical Specs Type",
                        "name1": opt,
                        "source_field": source_label
                    })
                    doc.insert(ignore_permissions=True)
                    created.append(doc.name)
                    existing_options.add(key)

    for row in matrix_doc.data_qynq:
        field_to_process = row.field_name

        # 1️⃣ Main Item field
        main_field = item_meta.get_field(field_to_process)
        if main_field:
            source_label = main_field.label
            if main_field.fieldtype == "Select" and main_field.options:
                options_list = [o.strip() for o in main_field.options.split("\n") if o.strip()]
                if options_list:
                    process_options(options_list, source_label)
                else:
                    frappe.log_error(f"Main field '{field_to_process}' has no valid options.")
            elif main_field.fieldtype == "Link" and main_field.options:
                linked_values = [d.name for d in frappe.get_all(main_field.options)]
                if linked_values:
                    process_options(linked_values, source_label)
                else:
                    frappe.log_error(f"Main Link field '{field_to_process}' has no records.")

        # 2️⃣ Child table field
        elif "." in field_to_process:
            parent_fieldname, child_fieldname = field_to_process.split(".", 1)
            parent_df = item_meta.get_field(parent_fieldname)

            if not parent_df or parent_df.fieldtype != "Table" or not parent_df.options:
                frappe.log_error(f"Skipping {field_to_process}: Parent field not found or not a Table.")
                continue

            child_doctype = parent_df.options
            child_meta = frappe.get_meta(child_doctype)

            # Find the child field from child table fields
            child_df = None
            for df in child_meta.fields:
                if df.fieldname == child_fieldname:
                    child_df = df
                    break

            if not child_df:
                frappe.log_error(f"Skipping {field_to_process}: Child field not found in {child_doctype}.")
                continue

            source_label = f"{parent_df.label} → {child_df.label}"

            # Child table Select field
            if child_df.fieldtype == "Select":
                if child_df.options:
                    options_list = [o.strip() for o in child_df.options.split("\n") if o.strip()]
                    if options_list:
                        process_options(options_list, source_label)
                    else:
                        frappe.log_error(f"Child Select field '{child_fieldname}' in '{child_doctype}' has no valid options.")
                else:
                    frappe.log_error(f"Child Select field '{child_fieldname}' in '{child_doctype}' has no options defined.")

            # Child table Link field
            elif child_df.fieldtype == "Link" and child_df.options:
                linked_values = [d.name for d in frappe.get_all(child_df.options)]
                if linked_values:
                    process_options(linked_values, source_label)
                else:
                    frappe.log_error(f"Child Link field '{child_fieldname}' in '{child_doctype}' has no records.")

    frappe.db.commit()
    frappe.msgprint(f"Created {len(created)} Technical Specs Type records.")
    return created






