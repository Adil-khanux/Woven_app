frappe.ui.form.on("Sales Order", {
    customer: function(frm) {
        fetch_customer_credit(frm);
    },
    company: function(frm) {
        fetch_customer_credit(frm);
    }
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
                // Set custom field values in Sales Order
                frm.set_value("custom_credit_balance", r.message.custom_credit_balance || 0);
                frm.set_value("custom_credit_limit", r.message.custom_credit_limit || 0);
            } else {
                frm.set_value("custom_credit_balance", 0);
                frm.set_value("custom_credit_limit", 0);
            }
        }
    });
}
