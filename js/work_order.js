frappe.ui.form.on("Work Order", {
    onload: function(frm) {
        trigger_additional_cost_and_specs(frm);
    },
    production_item: function(frm) {
        trigger_additional_cost_and_specs(frm);
    },
    qty: function(frm) {
        update_additional_cost_amounts(frm);
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





