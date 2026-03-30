# Print Pro

A bundle of modern, professional print formats for Frappe / ERPNext.

## Included Formats
- **Modern Invoice**: A clean, colorful invoice design for Sales Invoice.
- **Professional Quotation**: A bold, modern quotation format.

## Installation

To install this app on your Frappe site:

1.  **Get the app**:
    ```bash
    bench get-app https://github.com/[your-username]/print_pro.git
    ```

2.  **Install the app to your site**:
    ```bash
    bench --site [your-site-name] install-app print_pro
    ```

3.  **Migrate your site**:
    ```bash
    bench --site [your-site-name] migrate
    ```

## Usage

After installation, the print formats will automatically appear in the Print Format list for their respective DocTypes (Sales Invoice and Quotation).

You can select them from the print view sidebar in ERPNext.

## License

MIT
