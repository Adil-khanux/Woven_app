frappe.ui.form.on("BOM", {
    item(frm) {
        if (!frm.doc.item) return;

        frappe.msgprint("Fetching Material Requirement for: " + frm.doc.item);
        //  check box check 
         frm.set_value("with_operations", 1);

        // Material Requirement ka document fetch karna
        frappe.db.get_value("Material Requirement", { item_code: frm.doc.item }, "name")
            .then(r => {
                if (r.message && r.message.name) {
                    let mr_name = r.message.name;

                    frappe.model.with_doc("Material Requirement", mr_name, function () {
                        let mr = frappe.model.get_doc("Material Requirement", mr_name);
                        
                        // BOM items clear kar do
                        frm.clear_table("items");

                        // Specifications se data copy karo
                        (mr.specifications || []).forEach(row => {
                            let child = frm.add_child("items");
                            child.item_code = mr.item_code;
                            child.item_name = mr.item_name;

                            // Agar with_operations checkbox checked hai tabhi operation set karna
                            if (frm.doc.with_operations) {
                                child.operation = row.operation;
                            }
                        });

                        frm.refresh_field("items");
                    });
                } 
                
                else {
                    frappe.msgprint("No Material Requirement found for item: " + frm.doc.item);
                }
            });
    },

    // Jab bhi checkbox change ho → child table refresh hoga
    with_operations(frm) {
        frm.refresh_field("items");
    }
});
