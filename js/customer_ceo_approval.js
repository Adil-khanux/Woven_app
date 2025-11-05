frappe.ui.form.on("Customer", {
    // validate(frm){
    //     frm.set_value("custom_ceo_approval",0)
    // }
});

frappe.ui.form.on("Sales Team", {
    // Case 1: Row Added
    sales_team_add(frm) {
        check_sales_team(frm);
    },

    // Case 2: Sales Person Added/Changed
    sales_person(frm, cdt, cdn) {
        check_sales_team(frm);
    },

    // Case 3: Row Removed
    sales_team_remove(frm) {
        check_sales_team(frm);
    }
});
function check_sales_team(frm) {
    let has_sales_person = false;

    // Check if Sales Team table has any row with sales_person filled
    (frm.doc.sales_team || []).forEach(row => {
        if (row.sales_person) {
            has_sales_person = true;
        }
    });

    if (has_sales_person) {
        // Now set the final value to 1. This ensures a change from the previous    
        frm.set_value("custom_ceo_approval", has_sales_person ? 1 : 0);
        
    } else {
        // If condition is not met, set to 0
        frm.set_value("custom_ceo_approval",  0);
    }
}
