# Print Pro

A bundle of modern, professional print formats for Frappe / ERPNext — styled after the **Arab App invoice layout**.

## Included Formats

| Format | DocType | Color Theme |
|---|---|---|
| **Modern Invoice** | Sales Invoice | Teal / Cyan |
| **Modern Sales Order** | Sales Order | Teal / Cyan |
| **Corporate Blue Invoice** | Sales Invoice | Navy Blue |
| **Custom Quotation** | Quotation | Burnt Orange |
| **Professional Quotation** | Quotation | Forest Green |

## Design Features (All Formats)

- ✅ **No letterhead wrapper** — `no_letterhead: 1` on all formats
- ✅ **Letter Head logo** pulled dynamically from ERPNext Letter Head
- ✅ **Seller card** — Company name, email, contact, VAT No., CR No.
- ✅ **Buyer card** — Customer/Party name, email, contact, VAT No., CR No.
- ✅ **Meta strip** — Document No., Date, Due Date / Valid Till, Currency
- ✅ **Items table** — #, Description, Type (item_group), Qty, Unit Price, Amount
- ✅ **Totals block** — Subtotal (excl. VAT), VAT rows, Amount Due
- ✅ **Terms & Conditions** — from `doc.terms`, shown only when present
- ✅ **Banking Details** — fetched from ERPNext Bank Account (company account)
- ✅ **Footer bar** — Company, VAT No., Email, Contact on dark background

## Installation

To install this app on your Frappe site:

1. **Get the app**:
    ```bash
    bench get-app https://github.com/[your-username]/print_pro.git
    ```

2. **Install the app to your site**:
    ```bash
    bench --site [your-site-name] install-app print_pro
    ```

3. **Migrate your site**:
    ```bash
    bench --site [your-site-name] migrate
    ```

## Usage

After installation, the print formats will automatically appear in the Print Format list for their respective DocTypes (Sales Invoice and Quotation).

Select them from the print view sidebar in ERPNext. The format will automatically:
- Use your company's Letter Head logo
- Pull company details from the Company DocType
- Pull customer/party details from the linked records
- Show banking details from your company's default bank account

## Local Preview

You can render a standalone HTML preview without installing into ERPNext:

```bash
python tools/preview_print_format.py modern_invoice
```

This writes a browser-openable file into `preview_output/` using sample data from `preview_samples/`.

To preview every format that has sample data:

```bash
python tools/preview_print_format.py --all
```

To see the available print format folder names:

```bash
python tools/preview_print_format.py --list
```

## Version History

| Version | Notes |
|---|---|
| `0.1.0` | Full redesign — Arab App invoice style, `no_letterhead: 1`, dynamic Letter Head logo |
| `0.0.1` | Initial release |

## License

MIT
