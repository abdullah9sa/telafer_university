import re
import os
import frappe
from frappe.utils.pdf import get_pdf

def get_rtl_style():
    font_css = ""
    regular_font = frappe.get_site_path('public', 'assets', 'fonts', 'NotoNaskhArabic-Regular.ttf')
    bold_font = frappe.get_site_path('public', 'assets', 'fonts', 'NotoNaskhArabic-Bold.ttf')
    if os.path.exists(regular_font):
        font_css += f'@font-face{{font-family:"NotoNaskh";src:url("file://{regular_font}") format("truetype");}}\n'
    if os.path.exists(bold_font):
        font_css += f'@font-face{{font-family:"NotoNaskh";src:url("file://{bold_font}") format("truetype");font-weight:700;}}\n'

    return f"""
<style>
  {font_css}
  * {{ box-sizing: border-box; }}
  html, body {{ direction: rtl; margin: 0; padding: 0; }}
  body {{ font-family: "NotoNaskh", "Amiri", "DejaVu Sans", sans-serif; font-size: 12pt; line-height: 1.4; }}
  .print-format {{ direction: rtl; width: 100%; }}
  
  table {{ 
    width: 100%; 
    border-collapse: collapse; 
    table-layout: fixed;
    direction: rtl;
  }}
  
  .table-bordered td {{
    border: 1px solid #333;
    padding: 8px;
    vertical-align: middle;
    word-wrap: break-word;
    text-align: right;
  }}
  
  .table-bordered td.label {{
    background: #f5f5f5;
    font-weight: bold;
    width: 25%;
  }}
  
  .table-bordered td:not(.label) {{
    width: 25%;
  }}
  
  img {{ max-width: 100%; height: auto; display: block; }}
  .ltr {{ direction: ltr; text-align: left; }}
  h1, h2 {{ margin: 4px 0; }}
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
    html = clean_broken_images(html)
    
    rtl_style = get_rtl_style()
    if "<html" not in html:
        html = f'<html lang="ar" dir="rtl"><head><meta charset="UTF-8">{rtl_style}</head><body>{html}</body></html>'
    else:
        html = re.sub(r"<html([^>]*?)>", r'<html\1 lang="ar" dir="rtl">', html)
        if "<head>" in html:
            html = html.replace("<head>", f"<head>{rtl_style}")
        else:
            html = html.replace("<html", f"<html><head>{rtl_style}</head><html", 1)

    pdf_options = {
        "page-size": "A4",
        "encoding": "UTF-8",
        "enable-local-file-access": True,
        "no-stop-slow-scripts": True,
        "load-error-handling": "ignore",
        "load-media-error-handling": "ignore",
    }

    try:
        pdf = get_pdf(html, options=pdf_options)
    except Exception as e:
        frappe.log_error(f"PDF generation failed: {str(e)}", "student_pdf")
        html = re.sub(r'<img[^>]*/?>', "", html, flags=re.IGNORECASE)
        pdf = get_pdf(html, options=pdf_options)
    
    frappe.local.response.filename = f"{doctype}-{name}.pdf"
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"


def clean_broken_images(html):
    def check_image(match):
        img_tag = match.group(0)
        src_match = re.search(r'src=["\'](["\'"][^>]*?)["\']', img_tag, re.IGNORECASE)
        
        if not src_match:
            return ""
        
        src = src_match.group(1).strip()
        if not src or src.lower() in ['none', 'null', 'undefined']:
            return ""
        
        if src.startswith('data:image/'):
            return img_tag
        
        if src.startswith(('http://', 'https://')):
            return ""
        
        if src.startswith(('/files/', '/assets/')):
            try:
                file_path = frappe.get_site_path('public', src.lstrip('/'))
                if os.path.exists(file_path):
                    return img_tag.replace(src, f'file://{os.path.abspath(file_path)}')
            except:
                pass
            return ""
        
        return ""
    
    return re.sub(r'<img[^>]*/?>', check_image, html, flags=re.IGNORECASE)
