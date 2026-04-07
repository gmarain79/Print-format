"""
v0.0.2 — Replace single petty_expense_account / petty_expense_amount fields
with a child table (Petty Expense Item) and reposition the section break to
after mode_of_payment so the standard top-section fields stay intact.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from ne_customization.install import CUSTOM_FIELDS, _OLD_FIELDS


def execute():
	# 1. Create the Petty Expense Item child DocType (and its DB table)
	_create_petty_expense_item_doctype()

	# 2. Delete old single-value fields that were replaced by the child table
	for fieldname in _OLD_FIELDS:
		name = frappe.db.get_value(
			"Custom Field", {"dt": "Payment Entry", "fieldname": fieldname}
		)
		if name:
			frappe.delete_doc("Custom Field", name, ignore_permissions=True)
			print(f"ne_customization patch: deleted old field Payment Entry.{fieldname}")

	# 3. Re-apply all current custom fields (creates missing, updates existing)
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)

	# 4. Ensure petty_expense_section is positioned after mode_of_payment
	section_cf = frappe.db.get_value(
		"Custom Field",
		{"dt": "Payment Entry", "fieldname": "petty_expense_section"},
		"name",
	)
	if section_cf:
		frappe.db.set_value("Custom Field", section_cf, "insert_after", "mode_of_payment")

	frappe.clear_cache(doctype="Payment Entry")
	print("ne_customization patch v0.0.2: complete.")


def _create_petty_expense_item_doctype():
	"""
	Create the Petty Expense Item child DocType programmatically so that
	Frappe also creates the backing database table (tabPetty Expense Item).
	Skipped if the DocType already exists.
	"""
	if frappe.db.exists("DocType", "Petty Expense Item"):
		print("ne_customization patch: Petty Expense Item DocType already exists — skipping.")
		return

	frappe.get_doc({
		"doctype":      "DocType",
		"name":         "Petty Expense Item",
		"module":       "NE Customization",
		"custom":       1,
		"istable":      1,
		"editable_grid": 1,
		"fields": [
			{
				"fieldname":    "expense_account",
				"fieldtype":    "Link",
				"label":        "Expense Account",
				"options":      "Account",
				"in_list_view": 1,
				"reqd":         1,
				"columns":      8,
			},
			{
				"fieldname":    "expense_amount",
				"fieldtype":    "Currency",
				"label":        "Amount",
				"in_list_view": 1,
				"reqd":         1,
				"columns":      4,
			},
		],
		"permissions": [
			{"role": "System Manager",    "read": 1, "write": 1, "create": 1, "delete": 1},
			{"role": "Accounts Manager",  "read": 1, "write": 1, "create": 1, "delete": 1},
			{"role": "Accounts User",     "read": 1, "write": 1, "create": 1, "delete": 1},
		],
	}).insert(ignore_permissions=True)

	frappe.db.commit()
	print("ne_customization patch: Petty Expense Item DocType created.")
