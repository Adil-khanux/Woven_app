import frappe
from frappe import _
from frappe.utils import now_datetime
import hashlib
import re

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

# ------------------------ Copy Expexted Start Date into Schedule Date on Work Order Submit ------------------------------

def copy_expected_start_date(doc, method):

    # Fetch all job cards linked with this work order
    job_cards = frappe.get_all( "Job Card", filters={"work_order": doc.name}, fields=["name", "expected_start_date"] )

    # If no job card found
    if not job_cards:
        return

    for jc in job_cards:
        frappe.db.set_value("Job Card",jc.name,"custom_schedule_date",jc.expected_start_date )


#------------------------- JOB CARD ADD SCRAP ITEMS --------------------
def add_scrap_items(doc, method):
    """
    Copy scrap items from the linked BOM to the Job Card,
    but only for scrap rows that match the Job Card's operation.
    """
    # Step 1: Check required fields
    if not doc.bom_no or not doc.operation:
        return

    try:
        # Step 2: Get BOM document
        bom = frappe.get_doc("BOM", doc.bom_no)

        # # Debugging info — show how many scrap items found in BOM
        # frappe.msgprint(f"🧾 BOM Scrap Items Count: {len(bom.scrap_items)}")
        # for s in bom.scrap_items:
        #     frappe.msgprint(f"➡️ BOM Scrap Operation: {s.operation}, Item: {s.item_code}")

        # Step 3: Clear existing scrap items
        doc.scrap_items = []

        # Step 4: Filter scrap items by matching operation
        matched_scraps = [row for row in bom.scrap_items if row.operation == doc.operation]

        if not matched_scraps:
            return

        # Step 5: Append matched scraps to Job Card
        for scrap in matched_scraps:
            doc.append("scrap_items", {
                "item_code": scrap.item_code,
                "item_name": scrap.item_name,
                "expected_qty": scrap.stock_qty,
                "stock_uom": scrap.stock_uom,
            })

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in add_scrap_items for Job Card")


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
        <tr heigh>
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

#################GENERARE HASH ID FOR JOB CARD#####################
def generate_parameter_hash(doc, method=None):
    # 1. Validation: Ensure child table exists and isn't empty
    if not doc.get("custom_job_card_parameters"):
        doc.custom_group_hash = ""
        return

    # 2. Collect and Sort Parameters for deterministic hashing
    param_list = []
    param_display = [] # For the Remarks field
    
    for row in doc.custom_job_card_parameters:
        if row.parameters and row.parameters_value:
            p_name = str(row.parameters).strip().lower() 
            p_val = str(row.parameters_value).strip().lower()
            
            param_list.append(f"{p_name}:{p_val}")
            # Format for Remarks: "Parameter: Value"
            param_display.append(f"{row.parameters}: {row.parameters_value}")

    if not param_list:
        return

    # Sort to ensure "Width:10|Denier:1000" always matches "Denier:1000|Width:10"
    param_list.sort()
    param_display.sort()

    # 3. Add Workstation (Must match fieldname 'workstation')
    # Use doc.workstation because jobs on different machines cannot be "common"
    base_string = f"WS:{doc.workstation}|" + "|".join(param_list)

    # 4. Generate & Assign Hash
    hash_object = hashlib.md5(base_string.encode())
    doc.custom_group_hash = hash_object.hexdigest()[:12]

    # Build key: value block
    param_block = "\n".join(param_display)


    # Replace existing key:value block if present
    pattern = r"(^|\n)([A-Za-z0-9 _/.-]+:\s.*\n?)+"


    if re.search(pattern, doc.remarks or ""):
        doc.remarks = re.sub(
        pattern,
        "\n" + param_block + "\n",
        doc.remarks,
        flags=re.MULTILINE
        ).strip()
    else:
    # Prepend if not present
        doc.remarks = param_block + "\n\n" + (doc.remarks or "").strip()

#############ADD PARAMETERS FROM BOM#################
def add_bom_param(doc, method=None):
    # Check BOM is linked
    if not doc.bom_no:
        return

    # Fetch linked BOM
    bom = frappe.get_doc("BOM", doc.bom_no)

    # Clear Job Card parameters to avoid duplicates
    doc.custom_job_card_parameters = []

    # Append Bom parameters into Job Card
    for row in bom.custom_job_card_parameters:
        doc.append("custom_job_card_parameters", {
            "operation": row.operation,
            "parameters": row.parameters,
            "parameters_value": row.parameters_value
        })

############## Work Order Auto Complete when Last Job Card will complete #################################
def work_order_complete(doc, method=None):
    frappe.msgprint("Function Call")

    if not doc.work_order:
        return
    work_order_id = doc.work_order
    work_ord = frappe.get_doc("Work Order", work_order_id)
    frappe.msgprint("Work order Access")
    # Get all sequence_ids from Work Order operations
    sequence_ids = [op.sequence_id for op in work_ord.operations]
    frappe.msgprint("get all sequence id ")
    if not sequence_ids:
        return
    
    max_sequence_id = max(sequence_ids)
    frappe.msgprint("Get Max Seq Id")
      # Only when last operation job card is submitted
    if doc.sequence_id != max_sequence_id:
        return

    # --- AUTO FINISH WORK ORDER ---
    if work_ord.status != "Completed":
        work_ord.db_set("status", "Completed")
        frappe.db.commit()
    frappe.msgprint("Work Order Finish Successfully")
    
    # ---- Call Stock AUTO STOCK ENTRY ----
    create_and_submit_stock_entry(work_order_id)

################ Create and zSubmit Auto Stock Entry ###########################
def create_and_submit_stock_entry(work_order_id):
   
    if frappe.db.exists(
        "Stock Entry",
        {
            "work_order": work_order_id,
            "docstatus": 1,
            "purpose": "Manufacture"
        }
    ):
        return

    se_dict = frappe.call(
        "erpnext.manufacturing.doctype.work_order.work_order.make_stock_entry",
        work_order_id=work_order_id,
        purpose="Manufacture"
    )

    se = frappe.get_doc(se_dict)
    se.insert(ignore_permissions=True)
    se.submit()
    frappe.msgprint("STock Entry Create Succesfully")
