import frappe

@frappe.whitelist()  # Ye zaroori hai client side se call ke liye
def get_valuation_rate(item_code):
   
    valuation_rate = frappe.db.get_value("Bin", {"item_code": item_code}, "valuation_rate")
    if valuation_rate:
        # frappe.msgprint(f"Valuation Rate found: {valuation_rate}")
        return valuation_rate
    else:
        frappe.msgprint(f"No Valuation Rate found for Item: {item_code}")
        return None


# def get_valuation_rate(frm)
# payload_data = frappe.form_dict
# valuation_rate = frappe.db.get_value(
#     "Bin",
#     {"item_code": payload_data.item_code},
#     "valuation_rate"
# )

# #  Check if data is found
# if valuation_rate:
#     frappe.msgprint(f"Valuation Rate found: {valuation_rate}")
#     frappe.response["message"] = valuation_rate
# else:
#     frappe.msgprint(f"No Valuation Rate found for Item: {payload_data.item_code}")
#     frappe.response["message"] = None
