import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


# ─── Custom Field Definitions ─────────────────────────────────────────────────
#
# Layout intent on the Payment Entry form:
#
#   [Type of Payment section]                      ← standard section
#     naming_series | payment_type                 ← LEFT column
#     column_break_5                               ← RIGHT column starts
#     posting_date | company | cost_center         ← RIGHT — untouched
#     mode_of_payment                              ← RIGHT — untouched
#     is_petty_expense ← inserted here (LEFT, after payment_type, before col break)
#
#   [Petty Expense Details section] ← our section, AFTER mode_of_payment
#     petty_expense_items (child table)
#     petty_expense_cost_center | petty_expense_description
#
# The section is hidden (depends_on) when is_petty_expense = 0, so the form
# looks exactly like standard Payment Entry for normal flows.

CUSTOM_FIELDS = {
	"Payment Entry": [
		# ── Checkbox (LEFT column, after payment_type, before the column break) ──
		{
			"fieldname": "is_petty_expense",
			"label": "Is Petty Expense",
			"fieldtype": "Check",
			"insert_after": "payment_type",
			"depends_on": "eval:doc.payment_type == 'Pay'",
			"default": "0",
			"description": "Enable to record a direct expense without a supplier/party.",
		},

		# ── Section Break (after mode_of_payment so the top section stays intact) ──
		{
			"fieldname": "petty_expense_section",
			"label": "Petty Expense Details",
			"fieldtype": "Section Break",
			"insert_after": "mode_of_payment",
			"depends_on": "eval:doc.is_petty_expense == 1",
			"collapsible": 0,
		},

		# ── Child Table (one row per expense line) ──────────────────────────────
		{
			"fieldname": "petty_expense_items",
			"label": "Expense Items",
			"fieldtype": "Table",
			"options": "Petty Expense Item",
			"insert_after": "petty_expense_section",
			"depends_on": "eval:doc.is_petty_expense == 1",
			"mandatory_depends_on": "eval:doc.is_petty_expense == 1",
		},

		# ── Column Break ────────────────────────────────────────────────────────
		{
			"fieldname": "petty_expense_col_break",
			"fieldtype": "Column Break",
			"insert_after": "petty_expense_items",
			"depends_on": "eval:doc.is_petty_expense == 1",
		},

		# ── Cost Center (optional, applies to all rows) ─────────────────────────
		{
			"fieldname": "petty_expense_cost_center",
			"label": "Cost Center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"insert_after": "petty_expense_col_break",
			"depends_on": "eval:doc.is_petty_expense == 1",
		},

		# ── Narration ───────────────────────────────────────────────────────────
		{
			"fieldname": "petty_expense_description",
			"label": "Expense Description",
			"fieldtype": "Small Text",
			"insert_after": "petty_expense_cost_center",
			"depends_on": "eval:doc.is_petty_expense == 1",
		},

		# ── Beneficiary Details Section ─────────────────────────────────────────
		{
			"fieldname": "beneficiary_details_section",
			"label": "Beneficiary Details",
			"fieldtype": "Section Break",
			"insert_after": "petty_expense_description",
			"depends_on": "eval:doc.is_petty_expense == 1",
			"collapsible": 0,
		},

		# ── Bank Account (Link) ─────────────────────────────────────────────────
		{
			"fieldname": "beneficiary_bank_account",
			"label": "Bank Account",
			"fieldtype": "Link",
			"options": "Bank Account",
			"insert_after": "beneficiary_details_section",
			"depends_on": "eval:doc.is_petty_expense == 1",
		},

		# ── Account Title ───────────────────────────────────────────────────────
		{
			"fieldname": "beneficiary_account_title",
			"label": "Account Title",
			"fieldtype": "Data",
			"insert_after": "beneficiary_bank_account",
			"depends_on": "eval:doc.is_petty_expense == 1",
			"read_only": 1,
		},

		# ── Column Break ────────────────────────────────────────────────────────
		{
			"fieldname": "beneficiary_col_break",
			"fieldtype": "Column Break",
			"insert_after": "beneficiary_account_title",
			"depends_on": "eval:doc.is_petty_expense == 1",
		},

		# ── Bank Code ───────────────────────────────────────────────────────────
		{
			"fieldname": "beneficiary_bank_code",
			"label": "Bank Code",
			"fieldtype": "Data",
			"insert_after": "beneficiary_col_break",
			"depends_on": "eval:doc.is_petty_expense == 1",
			"read_only": 1,
		},

		# ── IBAN ────────────────────────────────────────────────────────────────
		{
			"fieldname": "beneficiary_iban",
			"label": "IBAN Number",
			"fieldtype": "Data",
			"insert_after": "beneficiary_bank_code",
			"depends_on": "eval:doc.is_petty_expense == 1",
			"read_only": 1,
		},

		# ── Beneficiary Name ────────────────────────────────────────────────────
		{
			"fieldname": "beneficiary_name",
			"label": "Beneficiary Name",
			"fieldtype": "Data",
			"insert_after": "beneficiary_iban",
			"depends_on": "eval:doc.is_petty_expense == 1",
			"read_only": 1,
		},
	]
}

# Old single-field names that were replaced by the child table in v0.0.2.
# Kept here so the migration patch can delete them.
_OLD_FIELDS = [
	"petty_expense_account",
	"petty_expense_amount",
]


# ─── Installer ────────────────────────────────────────────────────────────────

def after_install():
	_check_install_order()
	_make_custom_fields()


def _check_install_order():
	"""Warn if ne_customization is installed before hrms (override chain breaks)."""
	installed = frappe.get_installed_apps()
	if "hrms" in installed and "ne_customization" in installed:
		if installed.index("ne_customization") < installed.index("hrms"):
			frappe.msgprint(
				msg=(
					"<b>Warning:</b> <code>ne_customization</code> is installed before "
					"<code>hrms</code>. The Payment Entry override chain may be broken.<br>"
					"Re-install <code>ne_customization</code> after <code>hrms</code> to fix this."
				),
				title="Install Order Warning",
				indicator="orange",
			)


def _make_custom_fields():
	print("ne_customization: Creating custom fields on Payment Entry...")
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	frappe.clear_cache(doctype="Payment Entry")
	print("ne_customization: Custom fields created successfully.")
