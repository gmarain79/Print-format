// NE Customization — Payment Entry client script
// Loaded additively alongside standard payment_entry.js (Frappe merges handlers).

frappe.ui.form.on("Payment Entry", {

	// ── setup: field queries (runs once at form creation) ─────────────────
	setup(frm) {
		// Filter expense_account column inside the child table to Expense accounts only
		frm.set_query("expense_account", "petty_expense_items", (doc) => ({
			filters: {
				root_type: "Expense",
				is_group: 0,
				company: doc.company,
			},
		}));



		// Filter cost_center column inside child table to current company
		frm.set_query("cost_center", "petty_expense_items", () => ({
			filters: {
				is_group: 0,
				company: frm.doc.company,
			},
		}));

		// Filter beneficiary bank account to non-company accounts
		frm.set_query("beneficiary_bank_account", () => ({
			filters: {
				is_company_account: 0,
			},
		}));
	},

	// ── refresh: sync visibility on every form load ───────────────────────
	refresh(frm) {
		ne_cust.toggle_petty_fields(frm);
	},

	// ── payment_type change ───────────────────────────────────────────────
	payment_type(frm) {
		if (frm.doc.payment_type !== "Pay") {
			frm.set_value("is_petty_expense", 0);
		}
		ne_cust.toggle_petty_fields(frm);
	},

	// ── is_petty_expense toggle ───────────────────────────────────────────
	is_petty_expense(frm) {
		ne_cust.toggle_petty_fields(frm);

		if (frm.doc.is_petty_expense) {
			// Clear party fields — not needed and cause server-side errors
			frm.set_value("party_type", "");
			frm.set_value("party", "");
			frm.set_value("party_balance", null);

			// Mirror paid_to ← paid_from so the browser reqd check passes
			// (server also sets this, but we do it client-side for immediate feedback)
			if (frm.doc.paid_from) {
				frm.set_value("paid_to", frm.doc.paid_from);
			}

			// Clear references table
			frm.clear_table("references");
			frm.refresh_field("references");

			frappe.show_alert({
				message: __("Petty Expense mode enabled. Add expense rows in the table below."),
				indicator: "blue",
			});
		} else {
			// Restore mandatory state for standard party fields
			frm.set_df_property("party_type", "reqd", 1);
			frm.set_df_property("party", "reqd", 1);
			frm.set_df_property("paid_to", "reqd", 1);
		}
	},

	// ── paid_from: keep paid_to in sync for petty mode ───────────────────
	paid_from(frm) {
		if (frm.doc.is_petty_expense && frm.doc.paid_from) {
			frm.set_value("paid_to", frm.doc.paid_from);
		}
	},

	// ── beneficiary_bank_account: fetch details when account is selected ──
	beneficiary_bank_account(frm) {
		if (!frm.doc.beneficiary_bank_account) {
			frm.set_value("beneficiary_account_title", "");
			frm.set_value("beneficiary_bank_code", "");
			frm.set_value("beneficiary_iban", "");
			frm.set_value("beneficiary_name", "");
			return;
		}
		frappe.db.get_value(
			"Bank Account",
			frm.doc.beneficiary_bank_account,
			["account_name", "bank_code", "iban", "party"],
			(r) => {
				if (r) {
					frm.set_value("beneficiary_account_title", r.account_name || "");
					frm.set_value("beneficiary_bank_code", r.bank_code || "");
					frm.set_value("beneficiary_iban", r.iban || "");
					frm.set_value("beneficiary_name", r.party || "");
				}
			}
		);
	},
});


// ── Child table events (Petty Expense Item) ───────────────────────────────────
frappe.ui.form.on("Petty Expense Item", {

	// Recalculate total when any row amount changes
	expense_amount(frm) {
		ne_cust.sync_total_from_items(frm);
	},

	// Recalculate total when a row is removed
	petty_expense_items_remove(frm) {
		ne_cust.sync_total_from_items(frm);
	},
});


// ─── Namespace helper ─────────────────────────────────────────────────────────
var ne_cust = {

	toggle_petty_fields(frm) {
		const is_pay   = frm.doc.payment_type === "Pay";
		const is_petty = cint(frm.doc.is_petty_expense) === 1;

		// Checkbox visible only for "Pay" type
		frm.set_df_property("is_petty_expense", "hidden", is_pay ? 0 : 1);

		// Petty expense section fields
		const petty_fields = [
			"petty_expense_section",
			"petty_expense_items",
			"beneficiary_details_section",
			"beneficiary_bank_account",
			"beneficiary_account_title",
			"beneficiary_col_break",
			"beneficiary_bank_code",
			"beneficiary_iban",
			"beneficiary_name",
		];
		petty_fields.forEach(f => frm.set_df_property(f, "hidden", is_petty ? 0 : 1));

		// In petty mode, party_type / party / paid_to are not needed
		frm.set_df_property("party_type", "reqd", is_petty ? 0 : 1);
		frm.set_df_property("party",      "reqd", is_petty ? 0 : 1);
		frm.set_df_property("paid_to",    "reqd", is_petty ? 0 : 1);

		frm.refresh_fields();
	},

	sync_total_from_items(frm) {
		if (!frm.doc.is_petty_expense) return;
		let total = 0;
		(frm.doc.petty_expense_items || []).forEach(row => {
			total += flt(row.expense_amount);
		});
		frm.set_value("paid_amount", total);
		frm.set_value("received_amount", total);
	},
};
