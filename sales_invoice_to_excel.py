import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
import tempfile

# For PDF parsing
try:
    from llama_parse import LlamaParse
except ImportError:
    st.error("⚠️ llama_parse not installed. Install with: pip install llama-parse")
    st.stop()

# For AI extraction
try:
    import google.generativeai as genai
except ImportError:
    st.error("⚠️ google-generativeai not installed. Install with: pip install google-generativeai")
    st.stop()

# ==================== CONFIGURATION ====================

def load_api_keys():
    """Load API keys from environment or Streamlit secrets"""
    llama_key = os.getenv("LLAMA_CLOUD_API_KEY") or st.secrets.get("LLAMA_CLOUD_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    
    if not llama_key or not google_key:
        st.error("❌ API keys not found! Please configure LLAMA_CLOUD_API_KEY and GOOGLE_API_KEY")
        st.info("Add them to .env file or .streamlit/secrets.toml")
        st.stop()
    
    return llama_key, google_key

# Load API keys
LLAMA_API_KEY, GOOGLE_API_KEY = load_api_keys()

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# ==================== CUSTOM CSS ====================

def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== EXTRACTION PROMPT ====================

SALES_EXTRACTION_PROMPT = """
You are an expert at extracting data from SALES INVOICES. 

IMPORTANT: This is a SALES INVOICE where:
- YOUR COMPANY is the vendor/seller (the company issuing and sending the invoice)
- The CUSTOMER is the party being billed (in "Bill To" section)

Extract the following information from this sales invoice and return ONLY valid JSON:

{
    "invoice_date": "YYYY-MM-DD format",
    "invoice_number": "Invoice number",
    "customer_name": "Customer company name (Bill To section)",
    "customer_address": "Full customer address",
    "customer_trn": "Customer TRN/Tax Registration Number if available, else null",
    "subtotal": "Subtotal amount as number (no currency symbols)",
    "tax_amount": "Tax/VAT amount as number",
    "net_total": "Final total amount as number",
    "currency": "Currency code (e.g., AED, USD)",
    "description": "Brief description of items/services",
    "payment_terms": "Payment terms if mentioned, else null",
    "items_count": "Number of line items"
}

Rules:
- Return ONLY valid JSON, no additional text
- All amounts must be numbers without currency symbols
- Date must be in YYYY-MM-DD format
- Extract customer from "Bill To" section
- Your company (the issuer) should NOT be in customer_name
"""

# ==================== CORE FUNCTIONS ====================

def parse_pdf_with_llamaparse(pdf_file):
    """Parse PDF using LlamaParse"""
    try:
        parser = LlamaParse(
            api_key=LLAMA_API_KEY,
            result_type="markdown"
        )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.getvalue())
            tmp_path = tmp_file.name
        
        # Parse the PDF
        documents = parser.load_data(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Extract text from parsed documents
        text_content = "\n\n".join([doc.text for doc in documents])
        return text_content
        
    except Exception as e:
        raise Exception(f"LlamaParse error: {str(e)}")

def extract_with_gemini(markdown_text):
    """Extract structured data using Gemini"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"{SALES_EXTRACTION_PROMPT}\n\nSALES INVOICE TEXT:\n{markdown_text}"
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        data = json.loads(response_text)
        return data
        
    except json.JSONDecodeError as e:
        raise Exception(f"JSON parsing error: {str(e)}\nResponse: {response_text[:200]}")
    except Exception as e:
        raise Exception(f"Gemini extraction error: {str(e)}")

def process_single_invoice(pdf_file, filename):
    """Process a single sales invoice"""
    try:
        # Step 1: Parse PDF
        markdown_text = parse_pdf_with_llamaparse(pdf_file)
        
        # Step 2: Extract data
        invoice_data = extract_with_gemini(markdown_text)
        
        # Add filename for reference
        invoice_data['filename'] = filename
        invoice_data['status'] = 'success'
        invoice_data['error'] = None
        
        return invoice_data
        
    except Exception as e:
        return {
            'filename': filename,
            'status': 'failed',
            'error': str(e),
            'invoice_date': None,
            'invoice_number': None,
            'customer_name': None,
            'customer_address': None,
            'customer_trn': None,
            'subtotal': 0,
            'tax_amount': 0,
            'net_total': 0,
            'currency': None,
            'description': None,
            'payment_terms': None,
            'items_count': 0
        }

def create_excel_output(invoices_data):
    """Create Excel file from extracted invoice data"""
    # Filter successful extractions
    successful = [inv for inv in invoices_data if inv['status'] == 'success']
    failed = [inv for inv in invoices_data if inv['status'] == 'failed']
    
    # Create DataFrame for invoices
    if successful:
        df_invoices = pd.DataFrame(successful)
        # Reorder columns
        column_order = [
            'invoice_date', 'invoice_number', 'customer_name', 'customer_address',
            'customer_trn', 'subtotal', 'tax_amount', 'net_total', 'currency',
            'description', 'payment_terms', 'items_count', 'filename'
        ]
        df_invoices = df_invoices[[col for col in column_order if col in df_invoices.columns]]
        
        # Rename columns for better readability
        df_invoices.columns = [
            'Invoice Date', 'Invoice Number', 'Customer Name', 'Customer Address',
            'Customer TRN', 'Subtotal', 'Tax Amount', 'Net Total', 'Currency',
            'Description', 'Payment Terms', 'Items Count', 'Filename'
        ]
    else:
        df_invoices = pd.DataFrame()
    
    # Create summary DataFrame
    summary_data = {
        'Metric': [
            'Total Invoices',
            'Successfully Processed',
            'Failed',
            'Success Rate',
            'Total Subtotal',
            'Total Tax',
            'Total Amount',
            'Currency'
        ],
        'Value': [
            len(invoices_data),
            len(successful),
            len(failed),
            f"{(len(successful)/len(invoices_data)*100):.1f}%" if invoices_data else "0%",
            f"{df_invoices['Subtotal'].sum():.2f}" if not df_invoices.empty else "0.00",
            f"{df_invoices['Tax Amount'].sum():.2f}" if not df_invoices.empty else "0.00",
            f"{df_invoices['Net Total'].sum():.2f}" if not df_invoices.empty else "0.00",
            df_invoices['Currency'].iloc[0] if not df_invoices.empty else "N/A"
        ]
    }
    df_summary = pd.DataFrame(summary_data)
    
    # Create errors DataFrame if any failed
    if failed:
        df_errors = pd.DataFrame([{
            'Filename': inv['filename'],
            'Error': inv['error']
        } for inv in failed])
    else:
        df_errors = pd.DataFrame()
    
    # Generate Excel file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sales_invoices_{timestamp}.xlsx"
    
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        if not df_invoices.empty:
            df_invoices.to_excel(writer, sheet_name='Invoices', index=False)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
        if not df_errors.empty:
            df_errors.to_excel(writer, sheet_name='Errors', index=False)
    
    return filename, df_invoices, df_summary, df_errors

# ==================== STREAMLIT UI ====================

def main():
    # Load custom CSS
    load_css()
    
    # Header
    st.markdown('<div class="main-header">📤 Sales Invoice Extraction System</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>ℹ️ About This Tool:</strong><br>
    This system extracts structured data from <strong>SALES INVOICES</strong> (invoices you send to customers).
    It captures customer information, invoice details, and financial data, then exports to Excel.
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    st.subheader("📁 Upload Sales Invoices")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more sales invoice PDFs"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        
        # Show uploaded files
        with st.expander("📋 View uploaded files"):
            for idx, file in enumerate(uploaded_files, 1):
                st.write(f"{idx}. {file.name} ({file.size / 1024:.1f} KB)")
        
        # Process button
        if st.button("🚀 Extract and Generate Excel", type="primary"):
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            invoices_data = []
            
            # Process each file
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                progress_bar.progress((idx) / len(uploaded_files))
                
                result = process_single_invoice(uploaded_file, uploaded_file.name)
                invoices_data.append(result)
            
            # Complete progress
            progress_bar.progress(1.0)
            status_text.text("✅ Processing complete!")
            
            # Generate Excel
            st.subheader("📊 Results")
            
            try:
                excel_filename, df_invoices, df_summary, df_errors = create_excel_output(invoices_data)
                
                # Display summary
                st.markdown("### 📈 Summary Statistics")
                st.dataframe(df_summary, use_container_width=True)
                
                # Display invoices
                if not df_invoices.empty:
                    st.markdown("### 📄 Extracted Invoices")
                    st.dataframe(df_invoices, use_container_width=True)
                
                # Display errors if any
                if not df_errors.empty:
                    st.markdown("### ⚠️ Failed Extractions")
                    st.dataframe(df_errors, use_container_width=True)
                
                # Download button
                with open(excel_filename, 'rb') as f:
                    st.download_button(
                        label="⬇️ Download Excel File",
                        data=f,
                        file_name=excel_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                st.success(f"✅ Excel file generated: {excel_filename}")
                
            except Exception as e:
                st.error(f"❌ Error generating Excel: {str(e)}")
    
    else:
        st.info("👆 Please upload sales invoice PDF files to begin extraction")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
    <strong>Sales Invoice Extraction System</strong><br>
    Powered by LlamaParse & Google Gemini | Created by MiniMax Agent
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
