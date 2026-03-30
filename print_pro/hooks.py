app_name = "print_pro"
app_title = "Print Pro"
app_publisher = "Antigravity AI"
app_description = "A bundle of pre-configured print formats for easy distribution."
app_email = "your-email@example.com"
app_license = "mit"

# Apps are automatically synced on installation or 'bench migrate'.
# All standard print formats included in this app will be created/updated in the database.

# Integration
# If you want to automatically link print formats to specific DocTypes or set defaults,
# you can use 'after_install' or 'after_sync' hooks.

after_install = "print_pro.setup.after_install"
