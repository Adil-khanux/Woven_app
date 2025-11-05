# Copyright (c) 2025, hitc technologies and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class ArtworkVersion(Document):
    def validate(self):
        self.add_row()

    def add_row(self):
        # Append a new row to the 'version' child table
        new_row = self.append("version", {})

       
        new_row.changed_by = frappe.session.user
        new_row.version_no = len(self.get("version"))
        new_row.source_snapshot = self.source_file
        new_row.preview_snapshot = getattr(self, "preview_image", None)
        new_row.pdf_snapshot = self.print_ready_pdf
        new_row.changed_on = now_datetime()

        # ✅ Required field: Change Summary
        new_row.change_summary = "version Entry Change."  

        frappe.msgprint(" New version row added successfully.")

