# telafer_university/api.py — return PDF for the doc matching exam_number
import re
import frappe
from frappe.utils.pdf import get_pdf

@frappe.whitelist(allow_guest=True)
def student_pdf(
    doctype: str = "Student",
    exam_number: str = "",
    format: str = "Student Print Format",
    no_letterhead: int = 1,
):
    doctype="Student"
    print("------------------------------------------------")
    print(exam_number)
    print(exam_number)

    if not doctype:
        frappe.throw("Missing doctype.")
    exam_number = (exam_number or "").strip()
    if not exam_number:
        frappe.throw("Missing exam_number.")

    # find most recent doc with this exam_number
    names = frappe.get_all(
        doctype,
        filters={"exam_number": exam_number},
        fields=["name"],
        order_by="creation desc",
        limit_page_length=1,
        pluck="name",
    )
    if not names:
        frappe.throw("No document found for the given exam_number.")
    name = names[0]

    # Render (force Arabic RTL shell if needed)
    frappe.local.lang = "ar"
    frappe.local.lang_full_dict = None
    frappe.local.jenv = None

    html = frappe.get_print(doctype, name, format, no_letterhead=int(no_letterhead))
    html = re.sub(r'<img[^>]*src=["\'](?:|None|null|/files/)["\'][^>]*>', '', html)
    if '<html' in html:
        html = re.sub(r'<html([^>]*?)>', r'<html\1 lang="ar" dir="rtl">', html)
    else:
        html = f'<html lang="ar" dir="rtl"><head><meta charset="UTF-8"></head><body>{html}</body></html>'

    pdf = get_pdf(html, options={"page-size": "A4", "encoding": "UTF-8"})
    frappe.local.response.filename = f"{doctype}-{name}.pdf"
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"
