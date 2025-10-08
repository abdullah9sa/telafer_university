import frappe
from frappe.utils.pdf import get_pdf
import re
import base64
import requests
from urllib.parse import quote

def generate_qr_base64(qr_data):
    try:
        encoded_data = quote(str(qr_data))
        response = requests.get(f'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_data}', timeout=10)
        response.raise_for_status()
        img_base64 = base64.b64encode(response.content).decode('utf-8')
        return f'data:image/png;base64,{img_base64}'
    except Exception as e:
        frappe.log_error(f"QR generation failed: {e}")
        return ''

@frappe.whitelist(allow_guest=True)
def student_pdf(doctype: str = "Student", name: str = "", format: str = "Student Print", no_letterhead: int = 1):
    frappe.local.lang = "ar"
    # unset lang and jenv to load new language
    frappe.local.lang_full_dict = None
    frappe.local.jenv = None
    
    if doctype != "Student":
        frappe.throw("Only Student doctype is allowed for guests.")
        
    name="rev4emnq65"
    if not name:
        frappe.throw("Missing document name.")

    html = frappe.get_print(doctype, name, format, no_letterhead=int(no_letterhead))
    
    # Remove empty/None image fields
    html = re.sub(r'<img[^>]*src=["\'](?:|None|null|/files/)["\'][^>]*>', '', html)
    
    # Get student document to extract QR data
    # Add Arabic language support to HTML
    if '<html' in html:
        html = re.sub(r'<html([^>]*?)>', r'<html\1 lang="ar" dir="rtl">', html)
    else:
        html = f'<html lang="ar" dir="rtl"><head><meta charset="UTF-8"></head><body>{html}</body></html>'

    pdf = get_pdf(html, options={"page-size": "A4", "encoding": "UTF-8"})

    frappe.local.response.filename = f"{doctype}-{name}.pdf"
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"
