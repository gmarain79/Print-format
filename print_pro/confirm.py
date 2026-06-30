import frappe

def confirm():
    name = frappe.db.get_value("Terms and Conditions", {"title": "Standard Quotation Terms"}, "name")
    print(f"Template Name: {name}")

if __name__ == "__main__":
    confirm()
