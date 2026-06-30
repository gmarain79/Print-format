import frappe

def check_lh():
    lh_list = frappe.get_all('Letter Head', fields=['name', 'image', 'content'])
    for lh in lh_list:
        print(f"Name: {lh.name}, Image: {lh.image}, Content Length: {len(lh.content) if lh.content else 0}")

if __name__ == "__main__":
    check_lh()
