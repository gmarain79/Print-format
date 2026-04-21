import frappe
import base64
import mimetypes
import re
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.core.doctype.file.utils import find_file_by_url
from frappe.utils.print_utils import get_print

def create_customer_cr_field():
    print("Creating custom field 'custom_cr_number' for Customer...")
    custom_fields = {
        "Customer": [
            {
                "fieldname": "custom_cr_number",
                "label": "CR Number",
                "fieldtype": "Data",
                "insert_after": "tax_id",
                "print_hide": 0
            }
        ]
    }
    create_custom_fields(custom_fields, ignore_validate=True)
    frappe.db.commit()
    print("Done!")


def get_file_data_url(file_url):
    """Return a full-size data URL for a public/private file URL when available."""
    if not file_url:
        return None

    try:
        file_doc = find_file_by_url(file_url)
        if not file_doc:
            return None

        mime_type = mimetypes.guess_type(file_url)[0] or "application/octet-stream"
        content = file_doc.get_content()
        encoded = base64.b64encode(content).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"
    except Exception:
        frappe.log_error(title="Print Pro Letterhead Embed Failed", message=frappe.get_traceback())
        return None


def debug_print_render(doctype, name, print_format, letterhead=None):
    """Return rendered print HTML diagnostics for local debugging."""
    html = get_print(
        doctype,
        name,
        print_format,
        as_pdf=False,
        no_letterhead=0,
        letterhead=letterhead,
    )

    urls = sorted(
        set(re.findall(r'https?://[^"\'\s>]+|/assets/[^"\'\s>]+|/files/[^"\'\s>]+', html))
    )

    snippets = {}
    for needle in ("Print Get PDF", "Get PDF", "download_pdf", "http://", "https://"):
        idx = html.find(needle)
        snippets[needle] = html[max(0, idx - 160) : min(len(html), idx + 320)] if idx >= 0 else None

    return {
        "url_count": len(urls),
        "urls": urls,
        "snippets": snippets,
    }
