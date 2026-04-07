import frappe


_ALL_FIELDS = [
	# current fields
	"is_petty_expense",
	"petty_expense_section",
	"petty_expense_items",
	"petty_expense_col_break",
	"petty_expense_cost_center",
	"petty_expense_description",
	# legacy fields (removed in v0.0.2, may still exist on older installs)
	"petty_expense_account",
	"petty_expense_amount",
]


def before_uninstall():
	print("ne_customization: Removing Payment Entry custom fields...")
	for fieldname in _ALL_FIELDS:
		name = frappe.db.get_value(
			"Custom Field", {"dt": "Payment Entry", "fieldname": fieldname}
		)
		if name:
			frappe.delete_doc("Custom Field", name, ignore_permissions=True)
	frappe.db.commit()
	frappe.clear_cache(doctype="Payment Entry")
	print("ne_customization: Custom fields removed.")
