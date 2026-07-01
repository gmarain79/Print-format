import frappe

def check_all():
    print("--- Letter Heads ---")
    all_lh = frappe.db.get_list('Letter Head', fields=['name', 'disabled', 'image', 'content'])
    for lh in all_lh:
        print(f"Name: {lh.name}, Disabled: {lh.disabled}, Image: {lh.image}, Content: {lh.content[:50] if lh.content else 'None'}")
    
    print("\n--- Companies ---")
    all_co = frappe.db.get_list('Company', fields=['name', 'default_letter_head'])
    for co in all_co:
        print(f"Company: {co.name}, Default LH: {co.default_letter_head}")

if __name__ == "__main__":
    check_all()
