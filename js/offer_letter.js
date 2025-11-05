frappe.ui.form.on("Job Offer", {
    refresh(frm) {
        // Add button only for saved (not new) docs
        if (!frm.is_new()) {
            // Show verified badge if already verified
            if (frm.doc.status === "Accepted") {
                // frm.add_custom_button("OTP Verified", null, "green");
            }
            if (frm.doc.status === "Awaiting Response" && frm.doc.docstatus === 1) {
                let btn_green = frm.add_custom_button("Verify by OTP", () => {
                    sendOTP(frm);
                });
                let btn_red = frm.add_custom_button("Reject", () => {
                    reject_btn(frm);
                });
                btn_green.addClass("btn-primary");
                btn_red.addClass("btn-danger");
            }
        }
    },
});

function sendOTP(frm) {
    frappe.call({
        method: "woven_app.api.job_offer.send_offer_otp",
        args: { docname: frm.doc.name },
        freeze: true,
        freeze_message: "Sending OTP...",
        callback: function (r) {
            if (!r.exc) {
                frappe.show_alert({ message: r.message, indicator: "green" });
                showOTPDialog(frm);
            }
        },
    });
}

function showOTPDialog(frm) {
    let seconds = 60;
    let timerInterval;

    const dialog = new frappe.ui.Dialog({
        title: "Enter OTP for Verification,",
        fields: [
            { label: "OTP", fieldname: "otp", fieldtype: "Data", reqd: 1 },
            { fieldtype: "HTML", fieldname: "timer_html" },
        ],
        primary_action_label: "Verify OTP",
        primary_action(values) {
            frappe.call({
                method: "woven_app.api.job_offer.verify_offer_otp",
                args: { docname: frm.doc.name, otp: values.otp },
                freeze: true,
                freeze_message: "Verifying OTP...",
                callback: function (r) {
                    if (!r.exc) {
                        frappe.show_alert({ message: r.message, indicator: "green" });
                        dialog.hide();
                        frm.reload_doc();
                    }
                },
            });
        },
    });

    // Timer section
    const updateTimer = () => {
        if (seconds > 0) {
            dialog
                .get_field("timer_html")
                .$wrapper.html(`<p style="color: gray;"><b>Resend OTP available in ${seconds}s</b></p>`);
            seconds--;
        } else {
            clearInterval(timerInterval);
            dialog
                .get_field("timer_html")
                .$wrapper.html(`<a href="#" class="resend-otp">Resend OTP</a>`);
            dialog
                .get_field("timer_html")
                .$wrapper.find(".resend-otp")
                .on("click", () => {
                    resendOTP(frm, dialog);
                });
        }
    };

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);

    dialog.show();
}

function resendOTP(frm, dialog) {
    frappe.call({
        method: "woven_app.api.job_offer.send_offer_otp",
        args: { docname: frm.doc.name },
        freeze: true,
        freeze_message: "Resending OTP...",
        callback: function (r) {
            if (!r.exc) {
                frappe.show_alert({ message: "OTP resent successfully!", indicator: "blue" });
                dialog.hide();
                showOTPDialog(frm);
            }
        },
    });
}

function reject_btn(frm, dialog) {
    frappe.call({
        method: "woven_app.api.job_offer.reject_btn",
        args: { docname: frm.doc.name },
        callback: function (r) {
            if (!r.exc) {
                frappe.show_alert({ message: "Job Offer Rejected", indicator: "red" });
                frm.reload_doc();
            }
        },
    });
}
