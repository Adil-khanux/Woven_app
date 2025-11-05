frappe.ui.form.on('Sales Invoice', {
    customer: function(frm) {
        if (frm.doc.customer) {

            // Get the first item_code from the child table (Sales Invoice Item)
            let item_code = null;

            if (frm.doc.items && frm.doc.items.length > 0) {
                item_code = frm.doc.items[0].item_code;
            }

            if (!item_code) {
                frappe.msgprint("Please add an Item before linking Price List.");
                return;
            }

            frappe.call({
                method: "woven_app.api.item_price.link_customer_with_price",
                args: {
                    customer: frm.doc.customer,
                    item_code: item_code
                },
                callback: function(r) {
                    console.log("Server response:", r.message);
                    if (r.message && r.message.price_list) {
                        frappe.msgprint(`✅ Price List Linked: ${r.message.price_list}`);
                    }
                }
            });
        }
    }
});
