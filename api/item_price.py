import frappe

@frappe.whitelist()
def link_customer_with_price(customer, item_code):

    data  = frappe.db.get_doc("Item Price",  # doctype
           {"item_code":item_code}, # filters
           [ " Standard Selling ",  "customer"  ]  # field name
            ) 
    if not data :
        frappe.new_doc()
    
    #  Check if Price List exists
    if not frappe.db.exists("Price List", price_list):
        frappe.throw(f"Price List '{price_list}' does not exist.")

    #  Get current linked price list for this customer
    current_price_list = frappe.db.get_value("Customer", customer, "default_price_list")

    #  If not linked OR different price list is linked → update it
    if current_price_list != price_list:
        frappe.db.set_value("Customer", customer, "default_price_list", price_list)
        frappe.msgprint(f" Linked Price List '{price_list}' with Customer '{customer}'")
    else:
        frappe.msgprint(f" Customer '{customer}' is already linked with Price List '{price_list}'")

    # Return response (optional)
    return {
        "customer": customer,
        "price_list": price_list,
      
    }
