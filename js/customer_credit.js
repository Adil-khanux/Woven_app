frappe.ui.form.on("Sales Order", {
    customer: function(frm) {
        fetch_customer_credit(frm);
    },
    company: function(frm) {
        fetch_customer_credit(frm);
    },
   validate: function(frm) {
        // --- 1. GM Approval Logic (Auto Repeat) ---
        let gm_approval = false;
        if (frm.doc.auto_repeat) {
            gm_approval = true;
            // Set the custom GM Approval field to 1 (True) or 0 (False)
            frm.set_value("custom_gm_approval", gm_approval ? 1 : 0); 
        }
        // --- 2. Credit Limit Validation Check ---
        // If the flag is set (True or 1), block the save/submit.
        if (frm.doc.custom_limit_crossed) {
            // Use frappe.throw to immediately stop the validation process and show an error message.
            frappe.throw(__("Cannot save or submit: The customer's **Credit Limit has been crossed**."));
        }
    },
});

function fetch_customer_credit(frm) {
   
    if (!frm.doc.customer || !frm.doc.company) return;

    frappe.call({
        method: "woven_app.api.customer_credit.get_customer_credit_info",
        args: { 
            customer: frm.doc.customer, 
            company: frm.doc.company 
        },
        callback: function(r) {
            if (r.message) {
                const info = r.message;

                // 1. Set Credit Limit and Balance (Existing Fields)
                frm.set_value("custom_credit_limit", info.custom_credit_limit || 0);
                frm.set_value("custom_credit_balance", info.custom_credit_balance || 0);
                
                // 2. Set Total Unpaid (New Field)
                frm.set_value("custom_total_unpaid", info.custom_total_unpaid || 0);
                
                // 3. Set Limit Crossed Checkbox (New Field)
                // The Python function returns a boolean (True/False), which is directly set to the checkbox.
                frm.set_value("custom_limit_crossed", info.custom_limit_crossed || 0); 
            } else {
                // Clear all fields on error or missing data
                frm.set_value("custom_credit_limit", 0);
                frm.set_value("custom_credit_balance", 0);
                frm.set_value("custom_total_unpaid", 0);
                frm.set_value("custom_limit_crossed", false);
            }
        }
    });
}