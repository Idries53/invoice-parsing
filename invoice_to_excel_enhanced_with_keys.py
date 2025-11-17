import streamlit as st
import os
import json
import pandas as pd
import tempfile
from datetime import datetime
from llama_parse import LlamaParse
import google.generativeai as genai
import re

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Invoice → Excel Converter",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-weight: 600;
        border-radius: 8px;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API Key Configuration - WITH YOUR KEYS ALREADY INCLUDED!
LLAMA_KEY = "llx-XpzUz6H19piWqW5g7m0tQ9vrIuiR8nB3kEMVdbRSe6kgZVNC"
GOOGLE_KEY = "AIzaSyCYB9ng6ceMQE2_wEu6YW3_LgYJ3OcIHik"

# Check if keys are valid
if not (LLAMA_KEY and GOOGLE_KEY):
    st.error("⚠️ Missing API keys. Please contact support.")
    st.stop()

genai.configure(api_key=GOOGLE_KEY)

# Enhanced Gemini Prompt
GEMINI_PROMPT = """You are an expert invoice data extraction system.
Analyze the invoice document and extract the following information with precision:

1. INVOICE NUMBER: Extract the invoice/reference number
2. INVOICE DATE: Extract the date (MM/DD/YYYY or DD/MM/YYYY format)
3. VENDOR NAME: Extract the company name of the supplier/vendor who issued this invoice
4. VENDOR ADDRESS: Extract the complete address of the vendor
5. DESCRIPTION: Extract the main service/product description
6. QUANTITY: Extract the quantity of items/services
7. UNIT PRICE: Extract the unit price (as a number)
8. TOTAL AMOUNT: Extract the total invoice amount (as a number)
9. TAX AMOUNT: Extract the tax/VAT amount (as a number, if mentioned)
10. CURRENCY: Extract the currency (AED, USD, EUR, etc.)

IMPORTANT GUIDELINES:
- Focus on PURCHASE invoices (invoices you received from vendors/suppliers)
- If something is not available, write "Not specified"
- Return ONLY a JSON object with the extracted data
- Ensure all monetary values are extracted as clean numbers (remove currency symbols)
- Double-check the vendor name - this should be the supplier, not your company

Format your response as a clean JSON object only:
{
    "invoice_number": "value",
    "invoice_date": "value", 
    "vendor_name": "value",
    "vendor_address": "value",
    "description": "value",
    "quantity": value,
    "unit_price": value,
    "total_amount": value,
    "tax_amount": value,
    "currency": "value"
}"""

# Initialize LlamaParse with your API key
def init_llama_parser():
    try:
        parser = LlamaParse(
            api_key=LLAMA_KEY,
            result_type="markdown",
            language="en"
        )
        return parser
    except Exception as e:
        st.error(f"❌ Failed to initialize PDF parser: {str(e)}")
        return None

# Process PDF with LlamaParse
def parse_pdf_with_llama(pdf_file):
    parser = init_llama_parser()
    if not parser:
        return None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_file.read())
            temp_file.flush()
            
            docs = parser.parse(temp_file.name)
            
            if docs and hasattr(docs, 'text') and docs.text:
                return docs.text
            else:
                st.error("❌ No text extracted from PDF")
                return None
                
    except Exception as e:
        st.error(f"❌ Error parsing PDF: {str(e)}")
        return None
    finally:
        if 'temp_file' in locals():
            try:
                os.unlink(temp_file.name)
            except:
                pass

# Extract data using Gemini
def extract_invoice_data_with_gemini(pdf_text, prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        full_prompt = f"{prompt}\n\nInvoice content to analyze:\n{pdf_text}"
        
        response = model.generate_content(full_prompt)
        
        if response and response.text:
            # Clean the response - remove markdown code blocks if present
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Try to parse as JSON
            try:
                data = json.loads(response_text)
                return data
            except json.JSONDecodeError as json_error:
                st.error(f"❌ JSON parsing error: {str(json_error)}")
                st.error(f"Raw response: {response_text}")
                return None
        else:
            st.error("❌ No response from Gemini AI")
            return None
            
    except Exception as e:
        st.error(f"❌ Error with Gemini AI: {str(e)}")
        return None

# Create Excel file with multiple sheets
def create_excel_file(invoices_data, summary_data):
    try:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"invoices_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main invoices sheet
            invoices_df = pd.DataFrame(invoices_data)
            invoices_df.to_excel(writer, sheet_name='Invoices', index=False)
            
            # Summary sheet
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Company info sheet
            company_info = pd.DataFrame([
                {'Field': 'Company Name', 'Value': 'Andez Business Consultancy'},
                {'Field': 'Processing Date', 'Value': datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                {'Field': 'Total Invoices', 'Value': len(invoices_data)},
                {'Field': 'System Type', 'Value': 'Purchase Invoice Processor'},
            ])
            company_info.to_excel(writer, sheet_name='Company Info', index=False)
        
        return filename
        
    except Exception as e:
        st.error(f"❌ Error creating Excel file: {str(e)}")
        return None

# Main Streamlit App
def main():
    st.markdown('<h1 class="main-header">📄 Invoice → Excel Converter</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>🔧 Purchase Invoice Processor</strong><br>
        Upload your purchase invoices (invoices you received from vendors) and extract data to Excel format.
    </div>
    """, unsafe_allow_html=True)
    
    # File upload
    uploaded_files = st.file_uploader(
        "📤 Upload PDF invoices",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more PDF invoice files"
    )
    
    if uploaded_files:
        if st.button("🚀 Process Invoices", type="primary"):
            
            invoices_data = []
            summary_data = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    # Update progress
                    progress = (i + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {uploaded_file.name}...")
                    
                    # Parse PDF
                    pdf_text = parse_pdf_with_llama(uploaded_file)
                    if not pdf_text:
                        continue
                    
                    # Extract data
                    invoice_data = extract_invoice_data_with_gemini(pdf_text, GEMINI_PROMPT)
                    if invoice_data:
                        # Add filename to data
                        invoice_data['filename'] = uploaded_file.name
                        invoices_data.append(invoice_data)
                        
                        # Add to summary
                        total_amount = invoice_data.get('total_amount', 0)
                        if isinstance(total_amount, str):
                            try:
                                total_amount = float(total_amount.replace(',', ''))
                            except:
                                total_amount = 0
                        
                        summary_data.append({
                            'Invoice': invoice_data.get('invoice_number', 'Unknown'),
                            'Vendor': invoice_data.get('vendor_name', 'Unknown'),
                            'Date': invoice_data.get('invoice_date', 'Unknown'),
                            'Amount': total_amount,
                            'Currency': invoice_data.get('currency', 'AED'),
                            'Status': '✅ Extracted'
                        })
                
                except Exception as e:
                    summary_data.append({
                        'Invoice': uploaded_file.name,
                        'Vendor': 'Error',
                        'Date': 'Error',
                        'Amount': 0,
                        'Currency': 'N/A',
                        'Status': f'❌ Error: {str(e)}'
                    })
            
            # Create Excel file
            if invoices_data:
                excel_filename = create_excel_file(invoices_data, summary_data)
                
                if excel_filename:
                    st.markdown("""
                    <div class="success-box">
                        <strong>✅ Processing Complete!</strong><br>
                        Successfully processed all invoices and created Excel file.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display summary
                    st.subheader("📊 Summary")
                    
                    total_invoices = len(invoices_data)
                    total_amount = sum([inv.get('total_amount', 0) for inv in invoices_data])
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Invoices", total_invoices)
                    
                    with col2:
                        st.metric("Total Amount", f"{total_amount:,.2f}")
                    
                    with col3:
                        unique_vendors = len(set([inv.get('vendor_name', 'Unknown') for inv in invoices_data]))
                        st.metric("Unique Vendors", unique_vendors)
                    
                    # Show summary table
                    st.subheader("📋 Invoice Details")
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df, use_container_width=True)
                    
                    # Download button
                    with open(excel_filename, 'rb') as f:
                        st.download_button(
                            label="📥 Download Excel File",
                            data=f,
                            file_name=excel_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.error("❌ Failed to create Excel file")
            else:
                st.warning("⚠️ No invoices were successfully processed")

if __name__ == "__main__":
    main()
