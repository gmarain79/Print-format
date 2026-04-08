app_name = "ne_customization"
app_title = "NE Customization"
app_publisher = "ubaid"
app_description = "NE Customization - ERPNext custom workflows including Petty Expense"
app_email = "ubaidkhanzada8@gmail.com"
app_license = "MIT"

# ─── Installation ────────────────────────────────────────────────────────────
after_install = "ne_customization.install.after_install"
before_uninstall = "ne_customization.uninstall.before_uninstall"

# ─── DocType Class Override ───────────────────────────────────────────────────
# Inherits from EmployeePaymentEntry (HRMS) → PaymentEntry (ERPNext).
# IMPORTANT: ne_customization must be installed AFTER hrms so this override
# takes precedence in Frappe's override chain.
override_doctype_class = {
	"Payment Entry": "ne_customization.overrides.petty_payment_entry.PettyExpensePaymentEntry"
}

# ─── Client-Side JS ──────────────────────────────────────────────────────────
# Loaded alongside (not replacing) the standard payment_entry.js.
# Frappe merges all doctype_js handlers from all installed apps.
doctype_js = {
	"Payment Entry": "public/js/payment_entry.js"
}

# ─── Fixtures ───────────────────────────────────────────────────────────────
fixtures = [
    {
        "dt": "Report",
        "filters": [
            ["name", "in", [
                "Meezan bank template", 
                "Meezan bank template(miscellaneous payment)"
            ]]
        ]
    }
]
