import frappe
from frappe.utils import flt

########################TAPE PLANT OUTPUT CALCULATION FUNCTION########################
def tape_plant_output_calculation(doc, method=None):
    if doc.custom_rpm:
        weaving_output_calculation(doc)
    # 1. Calculate Number of Tapes
    # Use .get() or default to 0 to prevent NoneType errors in math
    spacer = doc.custom_spacer or 0
    film_width = doc.custom_film_width or 0
    lost_tapes = doc.custom_no_of_tape_lost or 0

    if spacer > 0 and film_width > 0:
        # Using integer division // as per your original logic
        doc.custom_no_of_tapes = (film_width // spacer) - lost_tapes
    else:
        doc.custom_no_of_tapes = 0

    # 2. Calculate Tape Width
    # Ensure no_of_tapes is not zero to avoid ZeroDivisionError
    no_of_tapes = doc.custom_no_of_tapes or 0
    
    if no_of_tapes > 0 and film_width > 0:
        doc.custom_tape_width = film_width / no_of_tapes
    else:
        doc.custom_tape_width = 0

    # 3. Calculate Output (kg/hr)
    denier = doc.custom_denier or 0
    line_speed = doc.custom_line_speed or 0
    divisor = doc.custom_divisor or 0

    if all([denier, no_of_tapes, line_speed, divisor > 0]):
        # Formula: (Denier * Tapes * Speed * 60) / Divisor
        # Pre-calculating (Speed * 60) can be slightly faster but less readable
        doc.custom_output_kghr = (denier * no_of_tapes * line_speed * 60) / divisor
    else:
        doc.custom_output_kghr = 0

    if doc.custom_weight_per_bag_in_grams > 0 and doc.custom_output_kghr > 0:
        # 1. Pre-calculate values outside the loop to save CPU cycles
        multiplier = (doc.custom_weight_per_bag_in_grams / 1000) / (doc.custom_output_kghr / 60)
        for op in doc.operations:
            if op.workstation_type == "Tape Plant":
                op.time_in_mins = multiplier * doc.quantity

    ## Add Raw Material Table Data Into Job Card Parameters Table ##
    if doc.items:
        # 1. Clear target child table first (MOST IMPORTANT)
        doc.custom_job_card_parameters = []
        for row in doc.items:
            # 2. Append fresh rows from items
            doc.append("custom_job_card_parameters", {
                "operation" :row.operation,
                "parameters": row.item_code,
                "parameters_value": row.qty,
        })
            
    ## 1.Add Tape Plant Field        
    if doc.custom_denier > 0 :
        tape_plant_fields = {
            "Denier": doc.custom_denier,
            "Film Width": doc.custom_film_width,
            "Spacer": doc.custom_spacer,
            "No of Tape Lost": doc.custom_no_of_tape_lost,
            "Line Speed": doc.custom_line_speed,
            "Divisor" : doc.custom_divisor,
            "Tape Width": doc.custom_tape_width,
            "No of Tapes": doc.custom_no_of_tapes,
            "Weight Per Bag (In Grams)": doc.custom_weight_per_bag_in_grams,
            "Output kg/hr": doc.custom_output_kghr,
        }

        for parameter, value in tape_plant_fields.items():
                doc.append("custom_job_card_parameters", {
                    "operation": "Extrusion",
                    "parameters": parameter,
                    "parameters_value": value 
                })
    
    ## 2.Add Weaving Field
    if doc.custom_rpm is not None and doc.custom_rpm > 0 :
        weaving_field = {
            "PPM" : doc.custom_rpm,
            "Output mtr/hr" : doc.custom_output_in_looms_hrs,
            "Output kg/hr" : doc.custom_output_kg, 
        }

        for parameter, value in weaving_field.items():
            doc.append("custom_job_card_parameters",{
                "operation": "Weaving",
                "parameters": parameter,
                "parameters_value" : value
            })

   



########################WEAVE PLANT OUTPUT CALCULATION FUNCTION########################
def weaving_output_calculation(doc):
    if not doc.custom_rpm or flt(doc.custom_rpm) <= 0:
        return

    # Use get_value (singular) with as_dict=True to get a dictionary for a single record
    item_data = frappe.db.get_value(
        "Item", 
        doc.item, 
        ["custom_mesh_warp__weft_denier", "custom_no_of_tapes_to_crush"], 
        as_dict=True
    )

    # Safety check if item doesn't exist
    if not item_data:
        return

    # Now .get() will work perfectly
    mesh_value = item_data.get("custom_mesh_warp__weft_denier")
    no_of_tape_crushed = flt(item_data.get("custom_no_of_tapes_to_crush"))

    mesh_map = {
        "Mesh Variation Fabrics 8x8": 8,
        "Mesh Variation Fabrics 10x10": 10,
        "Mesh Variation Fabrics 12x12": 12
    }   
    
    mesh_calc = mesh_map.get(mesh_value, 0) + no_of_tape_crushed

    if mesh_calc > 0:
        doc.custom_output_in_looms_hrs = (flt(doc.custom_rpm) * 1.524) / mesh_calc
    else:
        doc.custom_output_in_looms_hrs = 0

    if doc.custom_output_in_looms_hrs > 0:
        for op in doc.operations:
            if op.workstation_type == "Weaving":
                op.time_in_mins = flt(doc.quantity/doc.custom_output_in_looms_hrs * 60)
  

#######################PRINTING CALCULATION#############################################
# def printing_calculation(doc):
    # if doc.custom_printing_speed > 0:
    #     doc.custom_output_mt = (doc.custom_printing_speed * 60)
    #     length = frappe.get_value("Item", doc.item, "custom_lengths") or 0 
    #     top_fold_type = frappe.get_value("Item", doc.item, "custom_fold_") or 0 
    #     bottom_fold_type = frappe.get_value("Item", doc.item, "custom_fold_type") or 0 
    #     if length > 0 and top_fold_type == " Single-Fold":
            # pass
######################### New Item Create #############################################################
def create_item(doc, method=None):
   
    ######################### 1.check in bom denier & Item is exist or not ############################
    if not doc.item or not doc.custom_denier > 0 :
        frappe.msgprint("Not Found")
        return
    
    ########################## 2.Fetch parameters from linked Item ################################
    parent_item = frappe.get_doc("Item", doc.item)
    
    # ####################################🔹3. Build Item Name Parts ##########################
    name_parts = [
            parent_item.name,
            f"{flt(parent_item.custom_transparency)}T" if parent_item.custom_transparency else None,
            f"{flt(doc.custom_tape_width)}W" if doc.custom_tape_width else None,
            f"{parent_item.custom_panton_shade}" if parent_item.custom_panton_shade else None,
            f"{parent_item.custom_color}C" if parent_item.custom_color else None,
            f"{int(parent_item.custom_no_of_colors)}C" if parent_item.custom_no_of_colors else None,
        ]

    ############################## 🔹4 Join only valid values  ######################################
    new_item_name = " | ".join(filter(None, name_parts))

    # ####################### 5.set Item Name  ###############################
    new_item_code = new_item_name.replace(" ", "-").upper()
    frappe.msgprint(f"Perfectly Set Name for Item: {new_item_name}")


    ############################## 7.check new item exist or not ##################################
    
   # 4. Check Existence to prevent duplicate creation
    if frappe.db.exists("Item", new_item_code):
        if doc.custom_item_names != new_item_code:
            doc.custom_item_names = new_item_code
        return
    frappe.msgprint("Create New Item Name")
    
    ############## 8. now create new item #########################
    new_item = frappe.copy_doc(parent_item)
    
    new_item.item_code = new_item_code
    new_item.item_group = "Tape"
    new_item.is_sales_item = 0

    # ######################## Set parameters ###############################
    # new_item.custom_deniers = doc.custom_denier
    # new_item.custom_panton_shade = parent_item.custom_panton_shade
    # new_item.custom_color = parent_item.custom_color
    # new_item.custom_transparency = parent_item.custom_transparency
    # new_item.custom_no_of_colors = parent_item.custom_no_of_colors
    # instead create new item and copy field one by one we use copy_doc to copy parent doc as it##########################

    new_item.insert(ignore_permissions=True)

    doc.custom_item_names = new_item.item_code

    frappe.msgprint(f"Item Create Successfully : {new_item}" )


def execute_bom_automation(doc, method=None):

    target_operations = ["Printing", "Weaving", "Lamination", "Extrusion"]
    
    # 2. Grouping Logic
    op_groups = {}
    for row in doc.items:
        if row.operation in target_operations:
            op_groups.setdefault(row.operation, []).append(row)
                
    if not op_groups:
        return 

    processed_ops = []
    for operation_name, rm_rows in op_groups.items():
        sb = create_bom(doc, operation_name, rm_rows)

        if sb:
            add_sub_assembly_to_parent(doc, operation_name, sb)
            processed_ops.append(operation_name)

        if processed_ops:
            finalize_parent_bom(doc, processed_ops)

def create_bom(doc, operation_name, rm_rows):
    # Create new BOM document
    sub_bom = frappe.new_doc("BOM")
    
    # SFG item from your custom field
    sub_bom.item = doc.custom_item_names 
    sub_bom.quantity = doc.quantity
    sub_bom.with_operations = 1
    
    # Copy Custom Fields
    fields_to_copy = [
        "custom_denier", "custom_film_width", "custom_spacer", "custom_no_of_tape_lost",
        "custom_line_speed", "custom_divisor", "custom_tape_width", "custom_no_of_tapes",
        "custom_weight_per_bag_in_grams", "custom_output_kghr", "custom_rpm", 
        "custom_output_in_looms_hrs", "custom_output_kg", "custom_bsc_bag_per_minute",
        "custom_lamination_meter_per_hour", "custom_stitching_bag_per_hour", 
        "custom_printing_meter_per_minute"
    ]
    for field in fields_to_copy:
        sub_bom.set(field, doc.get(field))

    # Operations
    source_op = next((o for o in doc.operations if o.operation == operation_name), None)
    sub_bom.append("operations", {
        "operation": operation_name,
        "workstation": source_op.workstation if source_op else None,
        "time_in_mins": source_op.time_in_mins if source_op else 1, 
        "operating_cost": source_op.operating_cost if source_op else 0
    })

    # Items
    for rm in rm_rows:
        sub_bom.append("items", {
            "item_code": rm.item_code,
            "qty": rm.qty,
            "stock_qty": rm.stock_qty,
            "operation": operation_name, 
            "rate": rm.rate,
            "uom": rm.uom,
            "stock_uom": rm.stock_uom,
            "conversion_factor": rm.conversion_factor or 1
        })
            
    sub_bom.insert(ignore_permissions=True)
    # sub_bom.submit()
    return sub_bom

def add_sub_assembly_to_parent(doc, operation_name, sb):
   
    new_row = doc.append("items", {
        "item_code": doc.custom_item_names,
        "qty": 1, # Usually SFG is 1 per assembly
        "bom_no": sb.name,
        "operation": operation_name,
        "uom": doc.uom,
        "stock_uom": doc.uom,
        "rate": flt(sb.total_cost),
        "amount": flt(sb.total_cost)
    })     
    new_row.set("is_new_assembly", True)
    new_row.save(ignore_permissions=True)
   
def finalize_parent_bom(doc, processed_ops):
    frappe.msgprint("Function Call")
    # Keep only the new assemblies and items that weren't in the processed operations
    doc.items = [
        row for row in doc.items 
        if row.get("is_new_assembly") or row.operation not in processed_ops
    ]
    
    doc.operations = [
        op for op in doc.operations 
        if op.operation not in processed_ops
    ]

    doc.flags.ignore_validate_update_after_submit = True
    doc.calculate_cost()
    doc.save(ignore_permissions=True)
