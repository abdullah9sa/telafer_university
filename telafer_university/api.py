import re
import frappe
from frappe.utils.pdf import get_pdf

RTL_STYLE = """
<style>
  @font-face { font-family: "NotoNaskh"; src: url("/assets/fonts/NotoNaskhArabic-Regular.ttf") format("truetype"); }
  @font-face { font-family: "NotoNaskh"; src: url("/assets/fonts/NotoNaskhArabic-Bold.ttf") format("truetype"); font-weight:700; }

  html, body { direction: rtl; unicode-bidi: plaintext; }
  body { font-family: "NotoNaskh","Amiri","DejaVu Sans","Arial",sans-serif; font-size:12pt; }

  .print-format, table { direction: rtl; }
  table { width:100%; border-collapse:collapse; table-layout:fixed; }
  th, td { text-align:right; vertical-align:top; }
  .label { background:#f9f9f9; font-weight:700; }
  .ltr { direction:ltr; text-align:left; unicode-bidi: plaintext; }
  img { display:inline-block; max-width:100%; height:auto; }
</style>
"""

@frappe.whitelist(allow_guest=True)
def student_pdf(
    doctype: str = "Student",
    exam_number: str = "",
    format: str = "Student Print Format",
    no_letterhead: int = 1,
):
    doctype = "Student"

    if not doctype:
        frappe.throw("Missing doctype.")
    exam_number = (exam_number or "").strip()
    if not exam_number:
        frappe.throw("Missing exam_number.")

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

    frappe.local.lang = "ar"
    frappe.local.lang_full_dict = None
    frappe.local.jenv = None

    html = frappe.get_print(doctype, name, format, no_letterhead=int(no_letterhead))

    # Clean up broken/invalid images more aggressively
    # Remove images with empty, None, null, or relative-only paths
    html = re.sub(r'<img[^>]*src=["\'](?:|None|null|/files/)["\'][^>]*/?>', "", html, flags=re.IGNORECASE)
    
    # Remove images with data URIs that might be malformed
    html = re.sub(r'<img[^>]*src=["\']data:(?!image/)[^"\']*["\'][^>]*/?>', "", html, flags=re.IGNORECASE)
    
    # Remove any remaining img tags without valid src
    html = re.sub(r'<img(?![^>]*src=["\']https?://)[^>]*/?>', "", html, flags=re.IGNORECASE)

    # Enforce RTL shell + fonts
    shell_start = '<html lang="ar" dir="rtl"><head><meta charset="UTF-8">'
    shell_end = "</head><body>{BODY}</body></html>"
    if "<html" in html:
        html = re.sub(r"<html([^>]*?)>", r'<html\1 lang="ar" dir="rtl">', html)
        html = html.replace("<head>", f"<head>{RTL_STYLE}")
    else:
        html = shell_start + RTL_STYLE + shell_end.replace("{BODY}", html)

    # Use failsafe PDF generation with additional options
    pdf_options = {
        "page-size": "A4",
        "encoding": "UTF-8",
        "no-stop-slow-scripts": True,
        "enable-local-file-access": True,
        "load-error-handling": "ignore",
        "load-media-error-handling": "ignore",
    }
    
    try:
        pdf = get_pdf(html, options=pdf_options)
    except Exception as e:
        # If PDF generation fails due to images, strip ALL images and retry
        frappe.log_error(f"PDF generation failed, retrying without images: {str(e)}", "student_pdf")
        html_no_img = re.sub(r'<img[^>]*/?>', "", html, flags=re.IGNORECASE)
        pdf = get_pdf(html_no_img, options=pdf_options)
    
    frappe.local.response.filename = f"{doctype}-{name}.pdf"
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"