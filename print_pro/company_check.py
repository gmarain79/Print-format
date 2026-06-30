import frappe

def check_company():
    companies = frappe.get_all('Company', fields=['name', 'default_letter_head'])
    for c in companies:
        print(f"Company: {c.name}, Default LH: {c.default_letter_head}")
    
    # Also check the specific invoice in the screenshot if possible
    # Invoice No was ACC-SINV-2026-00009
    inv_name = "ACC-SINV-2026-00009"
    if frappe.db.exists("Sales Invoice", inv_name):
        inv = frappe.get_doc("Sales Invoice", inv_name)
        print(f"Invoice {inv_name}: Letter Head: {inv.letter_head}, Company: {inv.company}")

if __name__ == "__main__":
    check_company()
