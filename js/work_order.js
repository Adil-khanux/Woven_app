frappe.ui.form.on("Work Order", {
    onload: function(frm) {
        trigger_additional_cost_and_specs(frm);
    },
    production_item: function(frm) {
        trigger_additional_cost_and_specs(frm);
    },
    qty: function(frm) {
        update_additional_cost_amounts(frm);
    },
    sales_order: function(frm){
        sales_order_qty(frm)
    }
    
});

function trigger_additional_cost_and_specs(frm) {
    if (frm.doc.bom_no) {
        frappe.model.with_doc("BOM", frm.doc.bom_no, function() {
            let bom_doc = frappe.model.get_doc("BOM", frm.doc.bom_no);

            // Clear existing tables
            frm.clear_table("custom_additional_cost");
            frm.clear_table("custom_specifications");

            // === Additional Cost Table ===
            if (bom_doc.custom_additional_cost && bom_doc.custom_additional_cost.length > 0) {
                let bom_qty = bom_doc.quantity || 1; // BOM quantity

                bom_doc.custom_additional_cost.forEach(row => {
                    let d = frm.add_child("custom_additional_cost");

                    d.workstation = row.workstation;
                    d.expense_account = row.expense_account;
                    d.description = row.description;

                    // store per-unit amount
                    d.per_unit_amount = (row.amount || 0) / bom_qty;
                    d.amount = d.per_unit_amount * (frm.doc.qty || 1);
                    
                });

                frm.refresh_field("custom_additional_cost");
                
            }
           
            
        });
    }
}

function update_additional_cost_amounts(frm) {
    let wo_qty = frm.doc.qty || 1;

    frm.doc.custom_additional_cost.forEach(row => {
        if (row.per_unit_amount) {
            row.amount = row.per_unit_amount * wo_qty;
        }
    });

    frm.refresh_field("custom_additional_cost");
}

// Calculate Quantity to manufacturing from sales order on select sales order
frappe.ui.form.on("Work Order", {
    sales_order: function(frm) {
        fetch_qty_from_sales_order(frm);
    },
    production_item: function(frm) {
        fetch_qty_from_sales_order(frm);
    }
});

function sales_order_qty(frm) {
    if (frm.doc.sales_order && frm.doc.production_item) {
        frappe.model.with_doc("Sales Order", frm.doc.sales_order, function() {
            let so_doc = frappe.model.get_doc("Sales Order", frm.doc.sales_order);

            let matched_row = so_doc.items.find(row => row.item_code === frm.doc.production_item);

            if (matched_row) {
                frm.set_value("qty", matched_row.qty);
                // frappe.msgprint(__("Quantity fetched from Sales Order for item: {0} → {1}", [matched_row.item_code, matched_row.qty]));
            } else {
                frappe.msgprint(__("No matching item found in Sales Order for {0}", [frm.doc.production_item]));
            }
        });
    }
}




