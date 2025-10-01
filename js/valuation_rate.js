frappe.ui.form.on('Blanket Order Item', {
    // Added Child table trigger item_code field pe change hone par valuation rate fetch ho jayega.
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];  // selected row ka reference cdn:child row k unique name, cdt:parent k ander konsa child doctype name 

        if (!row.item_code) return;

        frappe.call({
            method: "woven_app.api.valuation_rate.get_valuation_rate",
            args: {
                item_code: row.item_code
            },
            callback: function(r) {
                if (r.message) {

                //  Used frappe.model.set_value() to set custom_valuation_rate for the same row (instead of adding new row).
                    // Step 1: set valuation rate
                    frappe.model.set_value(cdt, cdn, "custom_valuation_rate", r.message);

                    // Step 2: calculate selling price with profit margin (from parent doctype)
                    let profit_margin = frm.doc.custom_profit_margin || 0; // parent profit margin
                    let calculated_rate = r.message + (r.message * profit_margin / 100);

                    // Step 3: set calculated rate in child row
                    frappe.model.set_value(cdt, cdn, "rate", calculated_rate);

                } else {
                    frappe.msgprint(__("No Valuation Rate found for Item " + row.item_code));
                    frappe.model.set_value(cdt, cdn, "custom_valuation_rate", 0);
                    frappe.model.set_value(cdt, cdn, "rate", 0);
                }
            }
        });
    }
});




