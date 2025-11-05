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
                if (!row.material) return;

                frm.add_child("items", {
                    uom : frm.doc.uom,
                    item_code: row.material,
                    operation: frm.doc.with_operations ? row.operation : null,
                    workstation: frm.doc.with_operations ? row.workstation : null
                });
            });
            frm.refresh_field("items");

            // Clear and refill BOM operations with unique operation–workstation pairs
            frm.clear_table("operations");
            let unique_pairs = new Set();

            (mr.specifications || []).forEach(row => {
                if (frm.doc.with_operations && row.operation) {
                    let key = `${row.operation}||${row.workstation || ""}`;
                    unique_pairs.add(key);
                }
            });

            unique_pairs.forEach(pair => {
                let [operation, workstation] = pair.split("||");
                frm.add_child("operations", {
                    operation: operation,
                    workstation: workstation || null
                });
            });

            frm.refresh_field("operations");

        } catch (err) {
            console.error(err);
            frappe.msgprint("Error fetching Material Requirement");
        }
    },

    with_operations(frm) {
        frm.refresh_field("items");
    }
});
