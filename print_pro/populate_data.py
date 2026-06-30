import frappe

def fill_missing_data():
    print("Filling missing data for Quotation print format refinement...")
    
    # 1. Update Company: Friends Stone Crusher
    co = frappe.get_doc("Company", "Friends Stone Crusher")
    co.email = "info@friendsstone.com"
    co.phone_no = "+92 300 1234567"
    co.tax_id = "NTN-7654321-0"
    co.save(ignore_permissions=True)
    print(f"Updated Company: {co.name}")
    
    # 2. Update Customer: ABC Construction Co.
    cust = frappe.get_doc("Customer", "ABC Construction Co.")
    cust.tax_id = "NTN-1234567-8"
    cust.custom_cr_number = "CR-99887766"
    cust.save(ignore_permissions=True)
    print(f"Updated Customer: {cust.name}")
    
    # 3. Create Address for Customer
    addr_name = "ABC Construction - Office"
    if not frappe.db.exists("Address", addr_name):
        addr = frappe.new_doc("Address")
        addr.address_title = "ABC Construction Co."
        addr.address_type = "Office"
        addr.address_line1 = "123 Business Avenue, Block 5"
        addr.city = "Karachi"
        addr.email_id = "procurement@abcconstruction.com"
        addr.phone = "+92 21 34567890"
        # Link to Customer
        addr.append("links", {
            "link_doctype": "Customer",
            "link_name": "ABC Construction Co."
        })
        addr.insert(ignore_permissions=True)
        print(f"Created Address: {addr.name}")
    else:
        addr_name = frappe.db.get_value("Address", {"address_title": "ABC Construction Co."}, "name")
        print(f"Address already exists: {addr_name}")

    # 4. Link Address to Quotation SAL-QTN-2026-00001
    qtn = frappe.get_doc("Quotation", "SAL-QTN-2026-00001")
    qtn.customer_address = addr_name
    qtn.save(ignore_permissions=True)
    print(f"Linked address to Quotation: {qtn.name}")
    
    frappe.db.commit()
    print("All data filled successfully.")

if __name__ == "__main__":
    fill_missing_data()
