import pandas as pd
from datetime import datetime

# Extracted sales invoice data with customer information
sales_invoices_data = [
    {
        'Invoice Date': '2025-08-08',
        'Invoice Number': 'GT/16',
        'Customer Name': 'UMAR BIN SALAM',
        'Customer Address': 'RAS AL KHAIMAH',
        'Customer TRN': 'Not provided',
        'Subtotal': 3800.00,
        'Tax Amount': 190.00,
        'Net Total': 3990.00,
        'Currency': 'AED',
        'Description': 'Water wells drilling, 10" casing pipe (200 feet, 1 PCS)',
        'Project Location': 'RAS AL KHAIMAH',
        'Items Count': 2
    },
    {
        'Invoice Date': '2025-08-19',
        'Invoice Number': 'GT/19',
        'Customer Name': 'SALEM BIN UBAID',
        'Customer Address': 'WADI KOOB',
        'Customer TRN': 'Not provided',
        'Subtotal': 4000.00,
        'Tax Amount': 200.00,
        'Net Total': 4200.00,
        'Currency': 'AED',
        'Description': '10" casing pipe (200 feet), Water wells drilling (1 PCS)',
        'Project Location': 'WADI KOOB',
        'Items Count': 2
    },
    {
        'Invoice Date': '2025-08-25',
        'Invoice Number': 'GT/21',
        'Customer Name': 'HAMID BIN SALAEM',
        'Customer Address': 'WADI SHOK',
        'Customer TRN': 'Not provided',
        'Subtotal': 4400.00,
        'Tax Amount': 220.00,
        'Net Total': 4620.00,
        'Currency': 'AED',
        'Description': 'Water wells drilling, 10" casing pipe (200 feet, 1 PCS)',
        'Project Location': 'WADI SHOK',
        'Items Count': 2
    }
]

# Your company information (invoice issuer)
company_info = {
    'Company Name': 'AL ATAAYA WATER WELLS DRILLING CONTRACTING LLC',
    'Address': 'SHOP NO.5, ATHN ADHEN VILLAGE, RAS AL KHAIMAH',
    'TRN': '104949613400003',
    'Phone': '+971 50 530 7863',
    'Bank': 'EMIRATES ISLAMIC',
    'Account': '3708498322501',
    'IBAN': 'AE640340003708498322501'
}

# Create DataFrame
df = pd.DataFrame(sales_invoices_data)

# Create summary data
summary_data = {
    'Metric': [
        'Your Company (Issuer)',
        'Company TRN',
        'Total Sales Invoices',
        'Successful Extractions',
        'Total Subtotal Amount',
        'Total Tax Amount (5%)',
        'Total Revenue',
        'Currency',
        'Date Range',
        'Average Invoice Value'
    ],
    'Value': [
        company_info['Company Name'],
        company_info['TRN'],
        len(sales_invoices_data),
        len(sales_invoices_data),
        f"AED {df['Subtotal'].sum():,.2f}",
        f"AED {df['Tax Amount'].sum():,.2f}",
        f"AED {df['Net Total'].sum():,.2f}",
        'AED',
        '08 Aug 2025 - 25 Aug 2025',
        f"AED {df['Net Total'].mean():,.2f}"
    ]
}
summary_df = pd.DataFrame(summary_data)

# Company info DataFrame
company_df = pd.DataFrame([company_info])

# Generate filename with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'sales_invoices_extracted_{timestamp}.xlsx'

# Write to Excel with multiple sheets
with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Sales Invoices', index=False)
    summary_df.to_excel(writer, sheet_name='Summary', index=False)
    company_df.to_excel(writer, sheet_name='Company Info', index=False)
    
    # Get workbook and worksheets
    workbook = writer.book
    invoice_sheet = writer.sheets['Sales Invoices']
    summary_sheet = writer.sheets['Summary']
    company_sheet = writer.sheets['Company Info']
    
    # Format headers
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#28a745',
        'font_color': 'white',
        'border': 1
    })
    
    # Format currency
    currency_format = workbook.add_format({
        'num_format': '#,##0.00',
        'border': 1
    })
    
    # Apply column widths and formats for Sales Invoices sheet
    invoice_sheet.set_column('A:A', 12)  # Invoice Date
    invoice_sheet.set_column('B:B', 15)  # Invoice Number
    invoice_sheet.set_column('C:C', 25)  # Customer Name
    invoice_sheet.set_column('D:D', 25)  # Customer Address
    invoice_sheet.set_column('E:E', 20)  # Customer TRN
    invoice_sheet.set_column('F:F', 12, currency_format)  # Subtotal
    invoice_sheet.set_column('G:G', 12, currency_format)  # Tax Amount
    invoice_sheet.set_column('H:H', 12, currency_format)  # Net Total
    invoice_sheet.set_column('I:I', 10)  # Currency
    invoice_sheet.set_column('J:J', 50)  # Description
    invoice_sheet.set_column('K:K', 20)  # Project Location
    invoice_sheet.set_column('L:L', 12)  # Items Count
    
    summary_sheet.set_column('A:A', 30)
    summary_sheet.set_column('B:B', 40)
    
    company_sheet.set_column('A:H', 25)

print(f"✅ Sales invoices Excel file created: {filename}")
print(f"\n📊 SALES INVOICE EXTRACTION SUMMARY:")
print(f"=" * 80)
print(f"\n🏢 YOUR COMPANY (Invoice Issuer):")
print(f"   Name: {company_info['Company Name']}")
print(f"   TRN: {company_info['TRN']}")
print(f"   Location: {company_info['Address']}")
print(f"\n👥 CUSTOMERS (Invoiced Parties):")
for idx, inv in enumerate(sales_invoices_data, 1):
    print(f"   {idx}. {inv['Customer Name']} - {inv['Project Location']}")
print(f"\n💰 FINANCIAL SUMMARY:")
print(f"   Total Invoices: {len(sales_invoices_data)}")
print(f"   Total Subtotal: AED {df['Subtotal'].sum():,.2f}")
print(f"   Total Tax (5%): AED {df['Tax Amount'].sum():,.2f}")
print(f"   Total Revenue: AED {df['Net Total'].sum():,.2f}")
print(f"\n📋 INVOICE DETAILS:")
for idx, inv in enumerate(sales_invoices_data, 1):
    print(f"   {idx}. {inv['Invoice Number']} | {inv['Invoice Date']} | {inv['Customer Name'][:20]:20} | AED {inv['Net Total']:,.2f}")
print(f"\n" + "=" * 80)
