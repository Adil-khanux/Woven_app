frappe.ui.form.on('Sales Invoice', {
    customer: function(frm) {
       
        // frappe.msgprint("Customer field triggered");

        if (frm.doc.customer) {
            console.log("Calling server method for customer:", frm.doc.customer);

            frappe.call({
                method: "woven_app.api.customer.link_customer_with_price",
                // args send data in key value pair to bakcend
                args: {
                    customer: frm.doc.customer,
                    item_code:frm.doc.item_code  
                },
// now this call back function will run after server side method run and pass arguement from back end to front end 
                callback: function(r) {
                    console.log("Server response:", r.message);
//  print msg which come from server side and we use r.message for fetching response that come from backend method 
                    if (r.message) {
                        frappe.msgprint(`Price List Linked: ${r.message.price_list}`); 
                    }
                }
            });
        }
    }
});
