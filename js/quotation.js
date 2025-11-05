frappe.ui.form.on('Quotation', {
    validate: function(frm) {
        let any_below_price = false;
        
                // Loop through each child table row
        for (let item of frm.doc.items) {
            if (item.rate < item.price_list_rate) {
                any_below_price = true;
                 // loop stop kar sakte ho (forEach me nahi hota)
            }
        }
        
        // Set the parent checkbox field (assuming fieldname is 'check_box')
        frm.set_value('custom_all_rows', any_below_price ? 1 : 0);
    }
});

// // Optional: also trigger when a rate in child table changes
// frappe.ui.form.on('Quotation Item', {
//     rate: function(frm, cdt, cdn) {
//         let any_below_price = false;
//         frm.doc.items.forEach(function(item) {
//             if(item.rate < item.price_list_rate) {
//                 any_below_price = true;
//             }
//         });
//         frm.set_value('custom_all_rows', any_below_price ? 1 : 0);
//     }
// });
