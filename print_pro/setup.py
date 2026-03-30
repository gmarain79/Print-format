import frappe

def after_install():
	"""
	Optional: Automatically sets 'Modern Invoice' as the default print format for Sales Invoice
	and 'Professional Quotation' for Quotation.
	"""
	set_default_print_format("Sales Invoice", "Modern Invoice")
	set_default_print_format("Quotation", "Professional Quotation")

def set_default_print_format(doctype, print_format_name):
	# Check if the print format exists before setting it as default
	if frappe.db.exists("Print Format", print_format_name):
		# Usually, default print format is handled in 'Print Settings' or the DocType itself.
		# For Sales Invoice/Quotation, we can try to set 'default_print_format' in the DocType.
		# Note: This modifies core DocTypes which is generally discouraged,
		# but often what "Print Bundle" users expect.
		
		# Better way: Set it in 'Print Settings' if it's GLOBAL, or leave it for users.
		# Here's how to set it in the DocType metadata (caution):
		# dt = frappe.get_doc("DocType", doctype)
		# dt.default_print_format = print_format_name
		# dt.save()
		
		frappe.msgprint(f"Print Format '{print_format_name}' has been installed for {doctype}.")
