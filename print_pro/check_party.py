import frappe

def check_party_details():
    # Company
    co = frappe.get_doc("Company", "Friends Stone Crusher")
    print(f"Company: {co.name}")
    print(f"Email: {co.email}")
    print(f"Phone: {co.phone_no}")
    print(f"Tax ID: {co.tax_id}")
    
    # Customer ABC Construction Co.
    try:
        cust = frappe.get_doc("Customer", "ABC Construction Co.")
        print(f"\nCustomer: {cust.name}")
        print(f"Tax ID: {cust.tax_id}")
        print(f"Custom CR Number: {cust.get('custom_cr_number')}")
    except Exception as e:
        print(f"\nError fetching customer: {e}")

    # Quotation SAL-QTN-2026-00001
    try:
        doc = frappe.get_doc("Quotation", "SAL-QTN-2026-00001")
        print(f"\nQuotation: {doc.name}")
        print(f"Customer Address: {doc.customer_address}")
        if doc.customer_address:
            addr = frappe.get_doc("Address", doc.customer_address)
            print(f"Address Email: {addr.email_id}")
            print(f"Address Phone: {addr.phone}")
    except Exception as e:
        print(f"\nError fetching quotation: {e}")

if __name__ == "__main__":
    check_party_details()
