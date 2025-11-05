frappe.ui.form.on("Purchase Order", {
    refresh (frm) {
        // frappe.msgprint("hello") ; 
        // frappe.msgprint("Check below rate ")
        let check_rate = false;
        for (let item of frm.doc.items) {
            if(item.rate < item.price_list_rate){
                check_rate = true 
            }
        }

        frm.set_value("custom_price_below", check_rate ? 1: 0);
    }
});