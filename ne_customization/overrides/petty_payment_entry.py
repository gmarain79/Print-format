# Copyright (c) 2024, ubaid and contributors
# License: MIT

import frappe
from frappe import _
from frappe.utils import flt

from hrms.overrides.employee_payment_entry import EmployeePaymentEntry
from erpnext.accounts.utils import get_account_currency


class PettyExpensePaymentEntry(EmployeePaymentEntry):
	"""
	Extends EmployeePaymentEntry (HRMS) → PaymentEntry (ERPNext).

	When is_petty_expense = 1 (Payment Type must be "Pay"):
	  - No party (Supplier / Customer / Employee) required.
	  - Each row in petty_expense_items is a separate expense line.
	  - GL entries:
	      DR  row.expense_account   row.expense_amount   (one entry per row)
	      CR  paid_from             total amount         (single credit)
	"""

	# ── validate ─────────────────────────────────────────────────────────────

	def validate(self):
		if not self.is_petty_expense:
			super().validate()
			return

		# Petty path — run only the subset of validations that are safe
		# without a party.  Methods that require party / references are skipped.
		self.setup_party_account_field()
		self._petty_set_missing_values()
		self.validate_payment_type()
		self.set_exchange_rate()
		self._petty_validate_mandatory()
		self._petty_validate_fields()       # validates rows, syncs paid_amount
		self.set_amounts()                  # calculates base_paid_amount etc.
		self.validate_amounts()
		self.apply_taxes()
		self.set_amounts_after_tax()
		self.clear_unallocated_reference_document_rows()
		# validate_transaction_reference() is intentionally skipped:
		# it throws when paid_from is a Bank account and reference_no is blank,
		# which is irrelevant for petty cash entries.
		self._petty_set_title()
		self.set_remarks()
		self.validate_duplicate_entry()     # no-op — references table is empty
		self.set_status()

	# ── on_submit ─────────────────────────────────────────────────────────────

	def on_submit(self):
		if not self.is_petty_expense:
			super().on_submit()
			return

		# difference_amount is forced to 0 by set_difference_amount() override.
		# Party-related post-submit methods (outstanding, schedule, advance) are
		# skipped because there is no party.
		self.make_gl_entries()
		self.set_status()

	# ── on_cancel ─────────────────────────────────────────────────────────────

	def on_cancel(self):
		if not self.is_petty_expense:
			super().on_cancel()
			return

		self.ignore_linked_doctypes = (
			"GL Entry",
			"Stock Ledger Entry",
			"Payment Ledger Entry",
			"Repost Payment Ledger",
			"Repost Payment Ledger Items",
			"Repost Accounting Ledger",
			"Repost Accounting Ledger Items",
			"Unreconcile Payment",
			"Unreconcile Payment Entries",
		)
		# Call AccountsController.on_cancel() directly (two levels up) to avoid
		# EmployeePaymentEntry re-running party logic during cancellation.
		from erpnext.controllers.accounts_controller import AccountsController
		AccountsController.on_cancel(self)
		self.make_gl_entries(cancel=1)
		self.set_status()

	# ── helpers: petty-specific validate steps ────────────────────────────────

	def _petty_set_missing_values(self):
		"""
		Replacement for set_missing_values() in petty expense mode.
		- Clears party fields to prevent stale data reaching downstream methods.
		- Populates paid_from account metadata (currency, balance, type).
		- Sets paid_to = paid_from so set_exchange_rate() doesn't error on a
		  blank paid_to.
		"""
		for field in (
			"party", "party_type", "party_balance",
			"total_allocated_amount", "base_total_allocated_amount",
			"unallocated_amount",
		):
			self.set(field, None)
		self.references = []

		if self.paid_from and not self.paid_from_account_currency:
			from erpnext.accounts.doctype.payment_entry.payment_entry import get_account_details
			acc = get_account_details(self.paid_from, self.posting_date, self.cost_center)
			self.paid_from_account_currency = acc.account_currency
			self.paid_from_account_balance  = acc.account_balance
			self.paid_from_account_type     = acc.account_type

		# set_exchange_rate() reads paid_to_account_currency — mirror from paid_from.
		if not self.paid_to:
			self.paid_to                  = self.paid_from
			self.paid_to_account_currency = self.paid_from_account_currency
			self.paid_to_account_balance  = self.paid_from_account_balance
			self.paid_to_account_type     = self.paid_from_account_type

		self.party_account_currency = self.paid_from_account_currency

	def _petty_validate_mandatory(self):
		"""Lightweight mandatory check — only what petty expense actually needs."""
		for field in ("paid_from", "source_exchange_rate"):
			if not self.get(field):
				frappe.throw(_("{0} is mandatory").format(self.meta.get_label(field)))

	def _petty_validate_fields(self):
		"""
		Validate the petty_expense_items child table and sync paid_amount /
		received_amount to the sum of all expense rows.
		"""
		if not self.petty_expense_items:
			frappe.throw(
				_("Please add at least one row in the Expense Items table for Petty Expense.")
			)

		total = flt(0)
		for row in self.petty_expense_items:
			if not row.expense_account:
				frappe.throw(
					_("Row #{0}: Expense Account is mandatory.").format(row.idx)
				)
			if flt(row.expense_amount) <= 0:
				frappe.throw(
					_("Row #{0}: Amount must be greater than zero.").format(row.idx)
				)
			root_type = frappe.db.get_value("Account", row.expense_account, "root_type")
			if root_type != "Expense":
				frappe.throw(
					_("Row #{0}: {1} is not an Expense type account.").format(
						row.idx, frappe.bold(row.expense_account)
					)
				)
			total += flt(row.expense_amount)

		# Sync paid_amount / received_amount to the child-table total so that
		# set_amounts() and validate_amounts() work correctly.
		self.paid_amount     = total
		self.received_amount = total

	# ── set_difference_amount override ────────────────────────────────────────

	def set_difference_amount(self):
		"""
		For petty expense the GL entries are perfectly balanced
		(sum of DR rows = single CR), so difference_amount is always 0.
		Without this override, set_amounts() computes a non-zero value
		(base_total_allocated_amount = 0 with no references) and on_submit()
		would throw.
		"""
		if self.is_petty_expense:
			self.difference_amount = 0
			return
		super().set_difference_amount()

	# ── title and remarks ─────────────────────────────────────────────────────

	def _petty_set_title(self):
		if frappe.flags.in_import and self.title:
			return
		# Format: "<document name> - <paid_from account>"
		# e.g. "ACC-PAY-2024-00001 - Cash"
		ref = self.name or "Petty Expense"
		self.title = "{0} - {1}".format(ref, self.paid_from)

	def set_remarks(self):
		if self.is_petty_expense:
			if self.custom_remarks:
				return
			lines = []
			for row in (self.petty_expense_items or []):
				lines.append(
					_("{0}: {1} {2}").format(
						row.expense_account,
						self.paid_from_account_currency,
						flt(row.expense_amount),
					)
				)
			total = sum(flt(r.expense_amount) for r in (self.petty_expense_items or []))
			remark = _("Petty Expense paid via {0} (Total: {1} {2})").format(
				self.paid_from,
				self.paid_from_account_currency,
				total,
			)
			if lines:
				remark += "\n" + "\n".join(lines)
			if self.get("petty_expense_description"):
				remark += "\n" + self.get("petty_expense_description")
			self.set("remarks", remark)
			return
		super().set_remarks()

	# ── GL entries ────────────────────────────────────────────────────────────

	def build_gl_map(self):
		"""
		Petty expense path: produces one DR per expense row plus one CR for the
		total against paid_from.  Standard party GL entries are skipped entirely.
		"""
		if not self.is_petty_expense:
			return super().build_gl_map()

		if self.payment_type in ("Receive", "Pay") and not self.get("party_account_field"):
			self.setup_party_account_field()

		gl_entries = []
		self._add_petty_expense_gl_entries(gl_entries)
		self.add_deductions_gl_entries(gl_entries)  # no-op if table is empty
		self.add_tax_gl_entries(gl_entries)          # no-op if table is empty
		return gl_entries

	def _add_petty_expense_gl_entries(self, gl_entries):
		"""
		GL pattern for petty expense:

		  For each row in petty_expense_items:
		    DR  row.expense_account   row.expense_amount

		  Single credit for the total:
		    CR  paid_from             sum(expense_amount)

		All amounts are converted to base currency using source_exchange_rate.
		"""
		default_cost_center = (
			self.get("petty_expense_cost_center")
			or self.cost_center
			or frappe.db.get_value("Company", self.company, "cost_center")
		)

		total_amount      = flt(0)
		total_base_amount = flt(0)

		# One DEBIT entry per expense row
		for row in self.petty_expense_items:
			amount      = flt(row.expense_amount)
			base_amount = flt(
				amount * flt(self.source_exchange_rate),
				self.precision("base_paid_amount"),
			)
			total_amount      += amount
			total_base_amount += base_amount

			# Row-level cost center takes priority; fall back to header-level default
			row_cost_center = row.cost_center or default_cost_center

			# Build per-row remarks: include user_remarks if provided
			row_remarks = self.remarks
			if row.user_remarks:
				row_remarks = "{0}\n{1}".format(self.remarks, row.user_remarks) if self.remarks else row.user_remarks

			expense_currency = get_account_currency(row.expense_account)
			gl_entries.append(
				self.get_gl_dict(
					{
						"account":                   row.expense_account,
						"account_currency":          expense_currency,
						"against":                   self.paid_from,
						"debit_in_account_currency": amount,
						"debit":                     base_amount,
						"cost_center":               row_cost_center,
						"remarks":                   row_remarks,
					},
					item=row,
				)
			)

		# Single CREDIT entry against paid_from (cash / bank)
		against_accounts = ", ".join(
			r.expense_account for r in self.petty_expense_items if r.expense_account
		)
		gl_entries.append(
			self.get_gl_dict(
				{
					"account":                    self.paid_from,
					"account_currency":           self.paid_from_account_currency,
					"against":                    against_accounts,
					"credit_in_account_currency": total_amount,
					"credit":                     total_base_amount,
					"cost_center":                default_cost_center,
					"post_net_value":             True,
					"remarks":                    self.remarks,
				},
				item=self,
			)
		)
