import frappe

@frappe.whitelist()
def get_customer_credit_info(customer, company):
    # Fetch Customer doc
    customer_doc = frappe.get_doc("Customer", customer)
    
    # Initialize credit limit
    credit_limit = 0
    # Get credit limit for the specific company
    for limit in customer_doc.credit_limits:
        if limit.company == company:
            credit_limit = limit.credit_limit
            break

    # Total unpaid = Sum of all submitted Sales Invoices for this customer and company
    total_unpaid = frappe.db.sql("""
        SELECT SUM(outstanding_amount)
        FROM `tabSales Invoice`
        WHERE customer=%s AND company=%s AND docstatus=1
    """, (customer, company))[0][0] or 0

    # Credit balance
    credit_balance = credit_limit - total_unpaid
    return {
        "custom_credit_limit": credit_limit,
        "custom_total_unpaid": total_unpaid,
        "custom_credit_balance": credit_balance,
    }