# Purchase Invoice Extraction System

## Overview
This system extracts structured data from **purchase invoice PDFs** and exports them to Excel format. It's specifically designed to process invoices received from vendors/suppliers.

## Key Features
- **Batch PDF Processing**: Upload multiple purchase invoices at once
- **Vendor Data Extraction**: Automatically extracts vendor name, address, and TRN
- **Financial Details**: Captures subtotal, tax amounts, and net totals
- **Excel Export**: Generates formatted Excel files with summary statistics
- **Error Handling**: Robust processing with detailed error reporting
- **Modern UI**: Clean, professional Streamlit interface

## Extracted Fields

### Vendor Information
- **Vendor Name**: Company issuing the invoice
- **Vendor Address**: Full vendor address
- **Vendor TRN**: Tax Registration Number

### Invoice Details
- **Invoice Date**: Date of invoice issuance
- **Invoice Number**: Unique invoice identifier
- **Currency**: Invoice currency (e.g., AED, USD)

### Financial Information
- **Subtotal**: Amount before tax
- **Tax Amount**: VAT/Tax applied
- **Net Total**: Final amount payable
- **Description**: Item/service description

## Files Included

### Main Application
- `invoice_to_excel_enhanced.py` - Streamlit web application (335 lines)

### Documentation
- `README.md` - Setup and usage instructions
- `ENHANCEMENTS.md` - Detailed feature comparison and improvements
- `requirements.txt` - Python dependencies

### Configuration
- `.env.example` - Environment variable template
- `.streamlit/secrets.toml.example` - Streamlit secrets template

### Test Results
- `test_results/invoices_corrected_YYYYMMDD_HHMMSS.xlsx` - Sample output

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
streamlit run invoice_to_excel_enhanced.py
```

### Process Invoices
1. Open the web interface (usually http://localhost:8501)
2. Upload one or more purchase invoice PDFs
3. Click "Extract and Generate Excel"
4. Download the generated Excel file

## Excel Output Structure

### Sheet 1: Invoices
Contains detailed information for each processed invoice:
- Invoice Date
- Invoice Number  
- Vendor Name
- Vendor Address
- Vendor TRN
- Subtotal
- Tax Amount
- Net Total
- Currency
- Description

### Sheet 2: Summary
Contains aggregated statistics:
- Total Invoices Processed
- Successful Extractions
- Total Subtotal Amount
- Total Tax Amount
- Total Net Amount
- Primary Vendor Name
- Primary Vendor TRN

## Test Results

Successfully tested with 3 purchase invoices from **Shahi Enterprises FZE**:

| Invoice # | Date | Amount | Status |
|-----------|------|--------|--------|
| SEFZE-1471 | 2025-08-21 | AED 18,900.00 | ✅ Success |
| SEFZE-1476 | 2025-09-09 | AED 18,900.00 | ✅ Success |
| SEFZE-1483 | 2025-09-29 | AED 15,750.00 | ✅ Success |

**Total Extracted**: AED 53,550.00  
**Success Rate**: 100% (3/3)

## Important Notes

### Invoice Type
This system is designed for **PURCHASE INVOICES** (invoices received from suppliers):
- ✅ Extracts **Vendor/Supplier** information (the company billing you)
- ✅ Your company appears in the "Bill To" section
- ❌ NOT for sales invoices (where you are the vendor)

### Data Accuracy
The system correctly identifies:
- **Vendor**: The company issuing the invoice (e.g., Shahi Enterprises FZE)
- **Customer**: Your company receiving the invoice (e.g., Andez Business Consultancy)

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

## Support
For issues or questions, refer to:
- ENHANCEMENTS.md for feature details
- Code comments in invoice_to_excel_enhanced.py

## Author
MiniMax Agent

## Date Created
2025-11-11
