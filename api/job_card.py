import frappe
from frappe import _
from frappe.utils import now_datetime

@frappe.whitelist()
def create_timesheets_from_jobcard(job_card):
    job_card_doc = frappe.get_doc("Job Card", job_card)
    #Get related company
    company = job_card_doc.company
    # ✅ Check if 'auto_create_timesheet' is enabled for this company
    auto_create = frappe.db.get_value("Company", company, "custom_production_timesheet")
    if not auto_create:
        return {"status": "skipped"}

    # Collect employees from Time Log table
    for row in job_card_doc.time_logs:
        if not row.employee:
            continue  # Skip if no employee assigned

        ts = frappe.new_doc("Timesheet")
        ts.job_card = job_card_doc.name
        ts.employee = row.employee
        ts.custom_manufactured_quantity = row.completed_qty
        ts.custom_item = job_card_doc.production_item
        ts.custom_job_card_reference = job_card_doc.name
        ts.append("time_logs", {
            "employee": row.employee,
            "from_time": row.from_time,
            "to_time": row.to_time,
            "hours": (row.to_time - row.from_time).total_seconds() / 3600,
            "activity_type": "Production"  # optional: set an activity type
        })
        ts.insert(ignore_permissions=True)
        ts.submit()

    frappe.db.commit()
    return {"status": "success"}

#------------------------- JOB CARD ADD SCRAP ITEMS --------------------
def add_scrap_items(doc, method):
    frappe.msgprint("✅ Function called: add_scrap_items")

    """
    Copy scrap items from the linked BOM to the Job Card,
    but only for scrap rows that match the Job Card's operation.
    """

    # Step 1: Check required fields
    if not doc.bom_no or not doc.operation:
        frappe.msgprint("⚠️ Missing BOM or Operation — skipping function.")
        return

    try:
        # Step 2: Get BOM document
        bom = frappe.get_doc("BOM", doc.bom_no)
        frappe.msgprint(f"📘 BOM fetched: {bom.name}")

        # Debugging info — show how many scrap items found in BOM
        frappe.msgprint(f"🧾 BOM Scrap Items Count: {len(bom.scrap_items)}")
        for s in bom.scrap_items:
            frappe.msgprint(f"➡️ BOM Scrap Operation: {s.operation}, Item: {s.item_code}")

        frappe.msgprint(f"🧩 Job Card Operation: {doc.operation}")

        # Step 3: Clear existing scrap items
        doc.scrap_items = []

        # Step 4: Filter scrap items by matching operation
        matched_scraps = [row for row in bom.scrap_items if row.operation == doc.operation]

        if not matched_scraps:
            frappe.msgprint(f"⚠️ No scrap items found in BOM <b>{doc.bom_no}</b> for operation <b>{doc.operation}</b>")
            return

        frappe.msgprint(f"✅ Found {len(matched_scraps)} matching scrap items.")

        # Step 5: Append matched scraps to Job Card
        for scrap in matched_scraps:
            doc.append("scrap_items", {
                "item_code": scrap.item_code,
                "item_name": scrap.item_name,
                "stock_qty": scrap.stock_qty,
                "stock_uom": scrap.stock_uom,
            })
            frappe.msgprint(f"🟢 Added Scrap Item: {scrap.item_code} ({scrap.item_name})")

        frappe.msgprint(f"🎯 Scrap items added successfully from BOM <b>{doc.bom_no}</b> for operation <b>{doc.operation}</b>")

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in add_scrap_items for Job Card")
        frappe.msgprint(f"❌ Error occurred in add_scrap_items: {e}")



# -------------------------------------------------------------------------------------------------------------------
## woven_app/woven_app/api/job_card.py
def update_sales_order_progress(doc, method):
    """
    HOOK: Triggered after a Job Card is created, saved, submitted, or cancelled.
    Updates the HTML field 'custom_progress_status' in the linked Sales Order.
    """
    if not doc.work_order:
        frappe.msgprint("Work Order Not created")
        return

    # Fetch the linked Sales Order
    sales_order = frappe.db.get_value("Work Order", doc.work_order, "sales_order")
    if not sales_order:
        return

    # Generate full progress HTML using helper
    html = get_manufacturing_progress(sales_order)

    # Update Sales Order HTML field
    frappe.db.set_value("Sales Order", sales_order, "custom_progress", html)
    frappe.db.commit()


def get_manufacturing_progress(sales_order):
    """
    Generates an HTML table with progress bars for all Job Cards linked to a Sales Order.
    """

    job_cards = frappe.db.sql("""
        SELECT
            jc.name AS job_card,
            jc.operation,
            jc.status,
            jc.total_completed_qty,
            jc.for_quantity
        FROM `tabJob Card` as jc
        JOIN `tabWork Order` as wo ON wo.name = jc.work_order
        WHERE wo.sales_order = %s
        ORDER BY jc.operation, jc.name
    """, sales_order, as_dict=True)

    if not job_cards:
        return f"<p class='text-muted' style='margin-top:10px;'>{_('No manufacturing data found for this Sales Order.')}</p>"

    html = """
    <table class='table table-bordered' style='margin-top:1px; font-size:13px; table-layout: fixed; width: 100%;'>
        <thead>
            <tr>
                <th>Operation</th>
                <th>Job Card</th>
                <th>Status</th>
                <th>Completed Qty</th>
                <th>Total Qty</th>
                <th style="width:220px;">Completion</th>
            </tr>
        </thead>
        <tbody>
    """

    for jc in job_cards:
        completed_qty = jc.total_completed_qty or 0
        total_qty = jc.for_quantity or 1  # Avoid division by zero
        completion = round((completed_qty / total_qty) * 100, 2)

        # 🎨 Determine progress bar color
        if completion >= 100:
            color = "bg-success"
        elif completion > 0:
            color = "bg-warning"
        else:
            color = "bg-danger"

        html += f"""
        <tr>
            <td>{jc.operation}</td>
            <td><a href='/app/job-card/{jc.job_card}' target='_blank'>{jc.job_card}</a></td>
            <td>{jc.status}</td>
            <td>{completed_qty}</td>
            <td>{total_qty}</td>
            <td>
                <div class="progress" role="progressbar" aria-valuenow="{completion}" aria-valuemin="0" aria-valuemax="100" style="height:16px;">
                    <div class="progress-bar {color}" style="width: {completion}%; font-size:11px;" title="{completed_qty}/{total_qty} Completed">
                        {completion}%
                    </div>
                </div>
            </td>
        </tr>
        """

    html += "</tbody></table>"
    return html



