import frappe

def check_pe_fields():
    meta = frappe.get_meta('Payment Entry')
    fields = [f.fieldname for f in meta.fields if f.fieldname]
    print("Payment Entry fields:", fields)
    
    # Check if 'currency' is in fields
    print("Is 'currency' in fields?", 'currency' in fields)

if __name__ == "__main__":
    check_pe_fields()
