import frappe

def generate_batch_barcode(doc, method):
    if doc.batch_id and not doc.custom_batch_barcode:
        doc.custom_batch_barcode = doc.batch_id
        frappe.db.commit()
