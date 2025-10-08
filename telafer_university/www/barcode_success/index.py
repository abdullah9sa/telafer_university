import frappe

def get_context(context):
    name = frappe.form_dict.get("name")
    print("name")
    print(name)
    doc = frappe.get_doc("Student", name)  # replace with your Doctype
    # Generate QR code for the document URL
    # Build the absolute URL to the Student document in the current system
    base_url = frappe.utils.get_url()  # Gets the system base URL
    doc_url = f"{base_url}/app/student/{doc.name}"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?data={doc_url}&size=320x320"
    context.barcode_url = qr_url
