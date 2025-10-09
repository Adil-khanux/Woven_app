frappe.ui.form.on("BOM", {
    async item(frm) {
        if (!frm.doc.item) return;

        // Always check the checkbox
        frm.set_value("with_operations", 1);

        try {
            // Fetch Material Requirement linked to this item
            let r = await frappe.db.get_value("Material Requirement", { item_code: frm.doc.item }, "name");
            if (!(r.message && r.message.name)) {
                frappe.msgprint(`No Material Requirement found for item: ${frm.doc.item}`);
                return;
            }

            // Load the full Material Requirement document
            let mr_name = r.message.name;
            await frappe.model.with_doc("Material Requirement", mr_name);
            let mr = frappe.model.get_doc("Material Requirement", mr_name);

            // Clear and refill BOM items from MR specifications
            frm.clear_table("items");
            (mr.specifications || []).forEach(row => {
                if(!row.material) return
                let child = frm.add_child("items", {
                    operation: frm.doc.with_operations ? row.operation : null,
                    workstation : frm.doc.with_operations ? row.workstation : null ,
                    item_code: row.material,
                   
                });
            });
            frm.refresh_field("items");

            // Add Operations in Operation Table  
            let unique_ops = new Set();
            (mr.specifications || []).forEach(row => {
                if (frm.doc.with_operations && row.operation) {
                    unique_ops.add(row.operation);
                }
            });
            // Now add only unique operations
            unique_ops.forEach(op => {
                frm.add_child("operations", { operation: op ,});
               
            });

            let unique_stn = new Set();
            (mr.specifications || []).forEach(row => {
                if (frm.doc.with_operations && row.workstation){
                    unique_stn.add(row.workstation);
                }
            });

            unique_stn.forEach(st => {
                frm.add_child("operations" , {workstation : st})
            })

            frm.refresh_field("operations");

        } catch (err) {
            console.error(err);
            frappe.msgprint("Error fetching Material Requirement");
        }
    },

    with_operations(frm) {
        // Just refresh items when checkbox is toggled
        frm.refresh_field("items");
    }
});
