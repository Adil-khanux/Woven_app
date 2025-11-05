frappe.listview_settings['Technical Specs Type'] = {
    onload(listview) {
        listview.page.add_inner_button('Generate', function() {
            frappe.call({
                method: "woven_app.woven_app.doctype.technical_specs_type.technical_specs_type.create_technical_specs",
                // No need for 'args'
                callback: function(r) {
                    if (r.message && r.message.length) {
                        frappe.msgprint(`Created Specs: ${r.message.join(", ")}`);
                        listview.refresh(); // refresh the list
                    } else {
                        frappe.msgprint("No new specifications were created");
                    }
                }
            });
        });
    }
};