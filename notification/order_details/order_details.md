Hi {{ doc.customer_name }},

Please review your Sales Order {{ doc.name }} and approve it online.

<a href="{{ doc.get_url() }}">Click here to view your Sales Order</a>

Regards,  
{{ frappe.db.get_value("Company", doc.company, "company_name") }}
