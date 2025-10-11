import re
import os
import frappe
from frappe.utils.pdf import get_pdf

def get_rtl_style():
    """Generate RTL style with safe font loading"""
    font_css = ""
    # Only include fonts if they exist
    regular_font = frappe.get_site_path('public', 'assets', 'fonts', 'NotoNaskhArabic-Regular.ttf')
    bold_font = frappe.get_site_path('public', 'assets', 'fonts', 'NotoNaskhArabic-Bold.ttf')
    
    if os.path.exists(regular_font):
        font_css += '@font-face { font-family: "NotoNaskh"; src: url("file://' + regular_font + '") format("truetype"); }\n'
    if os.path.exists(bold_font):
        font_css += '@font-face { font-family: "NotoNaskh"; src: url("file://' + bold_font + '") format("truetype"); font-weight:700; }\n'
    
    return f"""
<style>
  {font_css}
  html, body {{ direction: rtl; unicode-bidi: plaintext; }}
  body {{ font-family: "NotoNaskh","Amiri","DejaVu Sans","Arial",sans-serif; font-size:12pt; }}

  .print-format, table {{ direction: rtl; }}
  table {{ width:100%; border-collapse:collapse; table-layout:fixed; }}
  th, td {{ text-align:right; vertical-align:top; }}
  .label {{ background:#f9f9f9; font-weight:700; }}
  .ltr {{ direction:ltr; text-align:left; unicode-bidi: plaintext; }}
  img {{ display:inline-block; max-width:100%; height:auto; }}
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

    # Clean broken images to prevent PDF generation errors
    html = clean_broken_images(html)

    # Enforce RTL shell + fonts
    rtl_style = get_rtl_style()
    shell_start = '<html lang="ar" dir="rtl"><head><meta charset="UTF-8">'
    shell_end = "</head><body>{BODY}</body></html>"
    if "<html" in html:
        html = re.sub(r"<html([^>]*?)>", r'<html\1 lang="ar" dir="rtl">', html)
        html = html.replace("<head>", f"<head>{rtl_style}")
    else:
        html = shell_start + rtl_style + shell_end.replace("{BODY}", html)

    # Use failsafe PDF generation with additional options
    pdf_options = {
        "page-size": "A4",
        "encoding": "UTF-8",
        "no-stop-slow-scripts": True,
        "enable-local-file-access": True,
        "load-error-handling": "ignore",
        "load-media-error-handling": "ignore",
        "disable-external-links": True,
        "disable-javascript": True,
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


def clean_broken_images(html):
    """Remove broken or non-existent images from HTML to prevent PDF generation issues"""
    def check_image(match):
        img_tag = match.group(0)
        src_match = re.search(r'src=["\']([^"\'][^>]*?)["\']', img_tag, re.IGNORECASE)
        
        if not src_match:
            return ""  # Remove img without src
        
        src = src_match.group(1).strip()
        
        # Remove empty, None, null sources
        if not src or src.lower() in ['none', 'null', 'undefined']:
            return ""
        
        # Remove external URLs (they cause network errors)
        if src.startswith(('http://', 'https://')):
            return ""
        
        # Keep valid data URIs
        if src.startswith('data:image/'):
            return img_tag
        
        # Check local file paths
        if src.startswith('/files/') or src.startswith('/assets/'):
            try:
                file_path = frappe.get_site_path('public', src.lstrip('/'))
                if os.path.exists(file_path):
                    # Convert to absolute file:// URL for wkhtmltopdf
                    abs_path = os.path.abspath(file_path)
                    return img_tag.replace(src, f'file://{abs_path}')
            except:
                pass
            return ""  # Remove non-existent file
        
        # Remove other invalid sources
        return ""
    
    # Apply check to all img tags
    html = re.sub(r'<img[^>]*/?>', check_image, html, flags=re.IGNORECASE)
    return html