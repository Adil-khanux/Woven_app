import frappe

def create_matrix_requirement(doc, method):
    # Hooked on Item Doctype
    if doc.item_group != "Products":
        return
    fields_value = []
    matrix_doc = frappe.get_single("Matrix Settings")
    doc_meta = frappe.get_meta(doc.doctype)
  

    # 🔍 Extract values from fields listed in Matrix Settings
    for row in matrix_doc.data_qynq:
        fieldname = row.field_name
        df = doc_meta.get_field(fieldname)

        if not df:
            continue

        # Case 1️⃣: Normal field
        if df.fieldtype != "Table":
            val = getattr(doc, fieldname, None)
            if val:
                fields_value.append(str(val))
           

        # Case 2️⃣: Child table
        else:
            child_doctype = df.options
            child_meta = frappe.get_meta(child_doctype)
            child_rows = doc.get(fieldname) or []

            for child_row in child_rows:
                for child_df in child_meta.fields:
                    # Skip hidden/system fields
                    if child_df.fieldtype in ["Section Break", "Column Break", "HTML", "Button"]:
                        continue
                    if child_df.fieldname in [
                        "name", "owner", "creation", "modified", "modified_by",
                        "parent", "parentfield", "parenttype", "doctype"
                    ]:
                        continue

                    val = getattr(child_row, child_df.fieldname, None)
                    if val:
                        fields_value.append(str(val))

    # 🔄 Fetch or create Material Requirement
    existing_mr = frappe.get_all("Material Requirement", {"item_code": doc.item_code}, limit=1)
    if existing_mr:
        mr = frappe.get_doc("Material Requirement", existing_mr[0].name)
        mr.specifications = []
    else:
        mr = frappe.new_doc("Material Requirement")
        mr.item_code = doc.item_code
        mr.item_name = doc.item_name

    # 📦 Fetch Technical Specs only if fields_value is not empty
    rows = []
    if fields_value:
        rows = frappe.db.sql("""
            SELECT name1, material, operation, workstation
            FROM `tabTechnical Specs`
            WHERE parenttype = "Matrix Settings"
            AND name1 IN %s
        """, (tuple(fields_value),), as_dict=1)

    # ➕ Append specs to Material Requirement
    for row in rows:
        mr.append("specifications", {
            "name1": row["name1"],
            "material": row["material"],
            "operation": row["operation"],
            "workstation": row["workstation"]
        })

    # 💾 Save or insert the document
    if existing_mr:
        mr.save(ignore_permissions=True)
    else:
        mr.insert(ignore_permissions=True)
