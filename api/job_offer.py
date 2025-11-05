import random
import frappe
from frappe.utils import now_datetime, add_to_date

@frappe.whitelist()
def send_offer_otp(docname):
    offer = frappe.get_doc("Job Offer", docname)
    
    otp = str(random.randint(100000, 999999))
    offer.custom_otp = otp
    offer.custom_otp_expiry_datetime = add_to_date(now_datetime(), minutes=10)
    offer.save(ignore_permissions=True)
    
    if not offer.applicant_email:
        frappe.throw("Please set the Applicant Email Address.")

    # Send email
    frappe.sendmail(
        recipients=offer.applicant_email,
        subject="Job Offer OTP Verification",
        message=f"""
            Dear {offer.applicant_name or 'Candidate'},<br>

            Your OTP for verification is <b>{otp}</b>. It will expire in 10 minutes.
        """, # <-- This comma ends the 'message' argument
        delayed=False

    )

    # Create communication record
    frappe.get_doc({
        "doctype": "Communication",
        "communication_type": "Communication",
        "subject": "Job Offer OTP Verification",
        "content": f"OTP sent to {offer.applicant_email}: OTP is <b>******</b>. Expiry: 10 minutes.",
        "sent_or_received": "Sent",
        "reference_doctype": "Job Offer",
        "reference_name": offer.name,
        "recipient": offer.applicant_email
    }).insert(ignore_permissions=True)

    return f"OTP sent successfully to {offer.applicant_email}."


@frappe.whitelist()
def verify_offer_otp(docname, otp):
    offer = frappe.get_doc("Job Offer", docname)

    if not offer.custom_otp or offer.custom_otp != otp:
        frappe.throw("Invalid OTP.")

    if offer.custom_otp_expiry_time and offer.custom_otp_expiry_time < now_datetime():
        frappe.throw("OTP has expired. Please request again.")

    offer.custom_otp_verified = 1
    offer.custom_verified_by = frappe.session.user
    offer.status = "Accepted"
    offer.save(ignore_permissions=True)
    
    return "OTP verified successfully."

@frappe.whitelist()
def reject_btn(docname):
    offer = frappe.get_doc("Job Offer", docname)
    offer.status = "Rejected"
    offer.save(ignore_permissions=True)

