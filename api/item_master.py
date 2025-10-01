import frappe

def on_update(doc, method):
    # Example: hooked on Item Doctype

    if doc.item_group != "Products":
        frappe.msgprint("Item Group is changed.")
    else:
        frappe.msgprint("Item Group is Finished Products.")

        # Create new Material Requirement
        mr = frappe.new_doc("Material Requirement")
        mr.item_code = doc.item_code
        mr.item_name = doc.item_name

        frappe.msgprint(f"New Material Requirement for {doc.item_code} created (not saved yet).")
        tup=("")

        # --- fetch Technical Specs rows via SQL ---
        rows = frappe.db.sql('''
            SELECT name1, material, operation
            FROM `tabTechnical Specs`
            WHERE parenttype = "Material Matrix"
              AND name1 IN ("Mesh Variation Fabrics 8x8", "Fortuner")
        ''', as_dict=1)

        frappe.msgprint("Fetched Technical Specs successfully")

        # --- append them into Material Requirement child table ---
        for row in rows:
            mr.append("specifications", {
                "name1": row["name1"],
                "material": row["material"],
                "operation": row["operation"]
            })

        frappe.msgprint("Child rows copied successfully")

        # finally save
        mr.insert(ignore_permissions=True)
        frappe.msgprint("✅ Material Requirement saved successfully")
