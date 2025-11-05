frappe.ui.form.on("Job Card", {
    async before_submit(frm) {
        // If quantities are already confirmed, allow submission
        if (frm.doc.custom_qty_confirmed_) return;
// we use async and await for execute code line by line bcz in js all code execute concurently 
        // Prepare employee data
        const emp_data = await Promise.all(
            (frm.doc.time_logs || []).map(async (row) => {
                let emp_name = "";
                if (row.employee) {
                    const r = await frappe.db.get_value("Employee", row.employee, "employee_name");
                    // this is better approach 
                    emp_name = r?.message?.employee_name || "";
                }
                return {
                    employee_code: row.employee,
                    employee_name: emp_name,
                    completed_quantity: row.completed_qty || 0
                };
            })
        );

        // Show confirmation dialog
        const d = new frappe.ui.Dialog({
            title: 'Total Qty to Manufacture: ' + frm.doc.for_quantity,
            size: "large",
            fields: [
                {
                    fieldname: "emp_qty",
                    fieldtype: "Table",
                // we use __ to translate our string into another language 
                    label: __("Employee wise Completed Quantity"),
                    cannot_add_rows: 1,
                    cannot_delete_rows: 1,
                    in_place_edit: 1,
                    data: emp_data,
                    fields: [
                        { label: __("Employee Code"), fieldname: "employee_code", fieldtype: "Link", options: "Employee", read_only: 1, in_list_view: 1 },
                        { label: __("Employee Name"), fieldname: "employee_name", fieldtype: "Data", read_only: 1, in_list_view: 1 },
                        { label: __("Completed Qty"), fieldname: "completed_quantity", fieldtype: "Float", reqd: 1, in_list_view: 1 }
                    ]
                }
            ],
            primary_action_label: __("Confirm"),
            primary_action: (values) => {
                if (!values?.emp_qty?.length) {
                    frappe.msgprint(__("No employee data to update."));
                    return;
                }

                // Update time_logs with confirmed quantities
                values.emp_qty.forEach((row) => {
                    const tl_row = frm.doc.time_logs.find(r => r.employee === row.employee_code);
                    if (tl_row) tl_row.completed_qty = row.completed_quantity;
                });

                // Mark your custom checkbox as confirmed
                frm.set_value("custom_qty_confirmed_", 1);
                frm.refresh_field("time_logs");

                d.hide();

                // Save and submit safely
                frappe.run_serially([
                    () => frm.save(),
                    () => { frappe.validated = true; frm.submit(); }
                ]);
            }
        });

        d.show();

        // Stop initial submission until dialog is confirmed
        frappe.validated = false;
    },
    on_submit(frm) {
        frappe.call({
            method: "woven_app.api.job_card.create_timesheets_from_jobcard",
            args: { job_card: frm.doc.name },
            callback: function (r) {
                if (r.message && r.message.status === "success") {
                    frappe.msgprint("Timesheets created successfully!");
                }
            }
        });
    }
});
