# return PDF for the doc matching exam_number
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
  img { display:inline-block; }
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

    # strip empty/broken images

        # Remove images with empty src, None, null, or /files/
    html = re.sub(r'<img[^>]*src=["\'](?:|None|null|/files/)["\'][^>]*>', "", html)

    # Remove images with unreachable src (local or remote)
    def is_image_accessible(src):
        import os
        import requests
        if src.startswith("http://") or src.startswith("https://"):
            try:
                resp = requests.head(src, timeout=2)
                return resp.status_code == 200
            except Exception:
                return False
        # Local file path (relative to sites or public)
        local_path = src
        if src.startswith("/files/"):
            local_path = os.path.join(frappe.get_site_path("public"), src.lstrip("/"))
        elif src.startswith("/assets/"):
            local_path = os.path.join(frappe.get_site_path("public"), src.lstrip("/"))
        return os.path.exists(local_path)

    def remove_broken_images(html):
        def repl(match):
            src_match = re.search(r'src=["\']([^"\']+)["\']', match.group(0))
            src = src_match.group(1) if src_match else ""
            if not is_image_accessible(src):
                # Optionally, replace with a placeholder image or just remove
                return ""  # Remove broken image
            return match.group(0)
        return re.sub(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>', repl, html)

    html = remove_broken_images(html)

    # enforce RTL shell + fonts
    shell_start = '<html lang="ar" dir="rtl"><head><meta charset="UTF-8">'
    shell_end = "</head><body>{BODY}</body></html>"
    if "<html" in html:
        html = re.sub(r"<html([^>]*?)>", r'<html\1 lang="ar" dir="rtl">', html)
        html = html.replace("<head>", f"<head>{RTL_STYLE}")
    else:
        html = shell_start + RTL_STYLE + shell_end.replace("{BODY}", html)

    pdf = get_pdf(html, options={"page-size": "A4", "encoding": "UTF-8"})
    frappe.local.response.filename = f"{doctype}-{name}.pdf"
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"
