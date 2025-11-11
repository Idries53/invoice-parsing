# Sales Invoice Extraction System

## Overview
This system extracts structured data from **sales invoice PDFs** (invoices you send to customers) and exports them to Excel format. It's specifically designed to process invoices where YOUR company is the vendor/seller.

## Key Differences from Purchase Invoice System

| Feature | Purchase Invoices | Sales Invoices |
|---------|-------------------|----------------|
| **Your Role** | Customer (receiving invoice) | Vendor (sending invoice) |
| **Extracted Party** | Vendor/Supplier information | Customer/Client information |
| **Invoice Direction** | Incoming (you pay) | Outgoing (customer pays) |
| **Data Focus** | Who you're paying | Who is paying you |

## Key Features
- **Batch PDF Processing**: Upload multiple sales invoices at once
- **Customer Data Extraction**: Automatically extracts customer name, address, and TRN
- **Financial Details**: Captures subtotal, tax amounts, and net totals
- **Excel Export**: Generates formatted Excel files with summary statistics
- **Error Handling**: Robust processing with detailed error reporting
- **Modern UI**: Clean, professional Streamlit interface

## Extracted Fields

### Customer Information
- **Customer Name**: Company/person being billed
- **Customer Address**: Full customer address
- **Customer TRN**: Tax Registration Number (if available)

### Invoice Details
- **Invoice Date**: Date of invoice issuance
- **Invoice Number**: Unique invoice identifier
- **Currency**: Invoice currency (e.g., AED, USD)
- **Payment Terms**: Payment terms if specified

### Financial Information
- **Subtotal**: Amount before tax
- **Tax Amount**: VAT/Tax applied
- **Net Total**: Final amount receivable
- **Description**: Item/service description
- **Items Count**: Number of line items

## Files Included

### Main Application
- `sales_invoice_to_excel.py` - Streamlit web application

### Documentation
- `README_SALES.md` - This file
- `requirements.txt` - Python dependencies

### Configuration
- `.env.example` - Environment variable template
- `.streamlit/secrets.toml.example` - Streamlit secrets template

## API Keys Required

### LlamaCloud API
- **Purpose**: PDF parsing and text extraction
- **Get Key**: https://cloud.llamaindex.ai/
- **Environment Variable**: `LLAMA_CLOUD_API_KEY`

### Google Gemini API
- **Purpose**: AI-powered data extraction
- **Get Key**: https://makersuite.google.com/app/apikey
- **Environment Variable**: `GOOGLE_API_KEY`

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

**Option A: Using .env file**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

**Option B: Using Streamlit secrets**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your API keys
```

## Usage

### Run the Application
```bash
streamlit run sales_invoice_to_excel.py
```

### Process Invoices
1. Open the web interface (usually http://localhost:8501)
2. Upload one or more sales invoice PDFs
3. Click "Extract and Generate Excel"
4. Download the generated Excel file

## Excel Output Structure

### Sheet 1: Invoices
Contains detailed information for each processed invoice:
- Invoice Date
- Invoice Number
- Customer Name
- Customer Address
- Customer TRN
- Subtotal
- Tax Amount
- Net Total
- Currency
- Description
- Payment Terms
- Items Count
- Filename

### Sheet 2: Summary
Contains aggregated statistics:
- Total Invoices
- Successfully Processed
- Failed
- Success Rate
- Total Subtotal
- Total Tax
- Total Amount
- Currency

### Sheet 3: Errors (if any)
Lists failed invoices with error messages

## Important Notes

### Invoice Type
This system is designed for **SALES INVOICES** (invoices you send to customers):
- ✅ Extracts **Customer/Client** information (the company you're billing)
- ✅ Your company is the vendor/issuer
- ❌ NOT for purchase invoices (where you receive invoices from suppliers)

### Data Accuracy
The system correctly identifies:
- **Customer**: The company/person you're billing (in "Bill To" section)
- **Vendor**: Your company (the invoice issuer)

## Comparison with Purchase Invoice System

### Use Purchase Invoice System When:
- ✅ You received the invoice from a supplier
- ✅ You need to track expenses/purchases
- ✅ You're extracting vendor information

### Use Sales Invoice System When:
- ✅ Your company issued the invoice
- ✅ You need to track revenue/receivables
- ✅ You're extracting customer information

## Technical Stack
- **Frontend**: Streamlit
- **PDF Parsing**: LlamaParse
- **AI Extraction**: Google Gemini (gemini-2.0-flash-exp)
- **Data Processing**: Pandas
- **Excel Generation**: xlsxwriter

## Error Handling
- Individual invoice failures don't stop batch processing
- Detailed error messages for each failed invoice
- Progress tracking during processing
- Summary statistics include success/failure counts

## Testing
Ready for testing with your sales invoice PDFs. Simply upload and process!

## Author
MiniMax Agent

## Date Created
2025-11-11
