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

# ==================== API KEYS - ALREADY INCLUDED ====================
LLAMA_API_KEY = "llx-XpzUz6H19piWqW5g7m0tQ9vrIuiR8nB3kEMVdbRSe6kgZVNC"
GOOGLE_API_KEY = "AIzaSyCYB9ng6ceMQE2_wEu6YW3_LgYJ3OcIHik"

# Configure Gemini with your API key
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
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-box {
        padding: 2rem;
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        text-align: center;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(45deg, #1f77b4, #17a2b8);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ==================== HELPER FUNCTIONS ====================

def init_llama_parser():
    """Initialize LlamaParse with API key"""
    try:
        parser = LlamaParse(
            api_key=LLAMA_API_KEY,
            result_type="markdown",
            language="en"
        )
        return parser
    except Exception as e:
        st.error(f"❌ Failed to initialize PDF parser: {str(e)}")
        return None

def parse_pdf_with_llama(pdf_file, parser):
    """Parse PDF using LlamaParse"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_file.read())
            temp_file.flush()
            
            docs = parser.parse(temp_file.name)
            
            if docs and len(docs) > 0:
                return docs[0].text
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

def extract_sales_invoice_data(pdf_text):
    """Extract sales invoice data using Gemini AI"""
    
    prompt = """You are an expert at extracting data from SALES invoices (invoices issued to customers).

Analyze the invoice document and extract the following information with precision:

1. INVOICE NUMBER: Extract the invoice/reference number
2. INVOICE DATE: Extract the date (MM/DD/YYYY or DD/MM/YYYY format) 
3. CUSTOMER NAME: Extract the customer's name (who received this invoice)
4. CUSTOMER ADDRESS: Extract the customer's complete address
5. SERVICE DESCRIPTION: Extract the main service/product description
6. QUANTITY: Extract the quantity of items/services
7. UNIT PRICE: Extract the unit price (as a number)
8. TOTAL AMOUNT: Extract the total invoice amount (as a number)
9. TAX/VAT AMOUNT: Extract the tax/VAT amount (as a number, if mentioned)
10. CURRENCY: Extract the currency (AED, USD, EUR, etc.)

IMPORTANT GUIDELINES:
- Focus on SALES invoices (invoices you sent to customers)
- If something is not available, write "Not specified"  
- Return ONLY a clean JSON object with the extracted data
- Ensure all monetary values are extracted as clean numbers (remove currency symbols)
- Double-check customer name - this should be your CLIENT, not your company

Format your response as a clean JSON object only:
{
    "invoice_number": "value",
    "invoice_date": "value", 
    "customer_name": "value",
    "customer_address": "value",
    "service_description": "value",
    "quantity": value,
    "unit_price": value,
    "total_amount": value,
    "tax_amount": value,
    "currency": "value"
}"""

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

def create_sales_excel_file(invoices_data):
    """Create Excel file with sales invoice data"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sales_invoices_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            
            # Main sales data sheet
            sales_data = []
            for inv in invoices_data:
                sales_data.append({
                    'Invoice Number': inv.get('invoice_number', 'Not specified'),
                    'Invoice Date': inv.get('invoice_date', 'Not specified'),
                    'Customer Name': inv.get('customer_name', 'Not specified'),
                    'Customer Address': inv.get('customer_address', 'Not specified'),
                    'Service Description': inv.get('service_description', 'Not specified'),
                    'Quantity': inv.get('quantity', 0),
                    'Unit Price': inv.get('unit_price', 0),
                    'Total Amount': inv.get('total_amount', 0),
                    'Tax Amount': inv.get('tax_amount', 0),
                    'Currency': inv.get('currency', 'AED'),
                    'Source File': inv.get('filename', 'Unknown')
                })
            
            df_sales = pd.DataFrame(sales_data)
            df_sales.to_excel(writer, sheet_name='Sales Invoices', index=False)
            
            # Summary sheet
            summary_data = []
            total_revenue = 0
            for i, inv in enumerate(invoices_data):
                total_amount = inv.get('total_amount', 0)
                if isinstance(total_amount, str):
                    try:
                        total_amount = float(total_amount.replace(',', ''))
                    except:
                        total_amount = 0
                
                total_revenue += total_amount
                
                summary_data.append({
                    'Invoice': inv.get('invoice_number', f'INV-{i+1}'),
                    'Customer': inv.get('customer_name', 'Unknown'),
                    'Date': inv.get('invoice_date', 'Not specified'),
                    'Amount': total_amount,
                    'Currency': inv.get('currency', 'AED'),
                    'Status': '✅ Extracted'
                })
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Company info sheet  
            company_info = pd.DataFrame([
                {'Field': 'Company Name', 'Value': 'AL ATAAYA WATER WELLS DRILLING CONTRACTING LLC'},
                {'Field': 'Processing Date', 'Value': datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                {'Field': 'Total Sales Invoices', 'Value': len(invoices_data)},
                {'Field': 'Total Revenue', 'Value': f"{total_revenue:.2f} AED"},
                {'Field': 'System Type', 'Value': 'Sales Invoice Processor'},
            ])
            company_info.to_excel(writer, sheet_name='Company Info', index=False)
        
        return filename, total_revenue
        
    except Exception as e:
        st.error(f"❌ Error creating Excel file: {str(e)}")
        return None, 0

# ==================== MAIN APP ====================

def main():
    st.markdown('<h1 class="main-header">🏢 Sales Invoice → Excel Converter</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Extract customer data from your sales invoices and convert to Excel</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>💼 Sales Invoice Processor</strong><br>
        Upload your sales invoices (invoices you sent to customers) and extract customer information to Excel format.
    </div>
    """, unsafe_allow_html=True)
    
    # File upload section
    st.markdown("""
    <div class="upload-box">
        <h3>📁 Upload Sales Invoice PDFs</h3>
        <p>Select one or more sales invoice PDF files</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "📤 Upload PDF invoices",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more sales invoice PDF files"
    )
    
    if uploaded_files:
        if st.button("🚀 Process Sales Invoices", type="primary"):
            
            # Initialize parser
            parser = init_llama_parser()
            if not parser:
                st.error("❌ Could not initialize PDF parser. Please check your API keys.")
                return
            
            invoices_data = []
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    # Update progress
                    progress = (i + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                    status_text.text(f"📄 Processing {uploaded_file.name}...")
                    
                    # Parse PDF
                    pdf_text = parse_pdf_with_llama(uploaded_file, parser)
                    if not pdf_text:
                        continue
                    
                    # Extract data
                    invoice_data = extract_sales_invoice_data(pdf_text)
                    if invoice_data:
                        # Add filename to data
                        invoice_data['filename'] = uploaded_file.name
                        invoices_data.append(invoice_data)
                    
                except Exception as e:
                    st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
            
            # Create Excel file
            if invoices_data:
                excel_filename, total_revenue = create_sales_excel_file(invoices_data)
                
                if excel_filename:
                    st.markdown("""
                    <div class="success-box">
                        <strong>✅ Sales Processing Complete!</strong><br>
                        Successfully processed all sales invoices and created Excel file.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display metrics
                    total_invoices = len(invoices_data)
                    total_customers = len(set([inv.get('customer_name', 'Unknown') for inv in invoices_data]))
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Invoices", total_invoices)
                    
                    with col2:
                        st.metric("Total Revenue", f"{total_revenue:,.2f}")
                    
                    with col3:
                        st.metric("Unique Customers", total_customers)
                    
                    # Show detailed results
                    st.subheader("📊 Sales Summary")
                    
                    summary_data = []
                    for i, inv in enumerate(invoices_data):
                        total_amount = inv.get('total_amount', 0)
                        if isinstance(total_amount, str):
                            try:
                                total_amount = float(total_amount.replace(',', ''))
                            except:
                                total_amount = 0
                        
                        summary_data.append({
                            'Invoice': inv.get('invoice_number', f'SINV-{i+1}'),
                            'Customer': inv.get('customer_name', 'Unknown'),
                            'Date': inv.get('invoice_date', 'Not specified'),
                            'Amount': total_amount,
                            'Currency': inv.get('currency', 'AED'),
                            'Status': '✅ Extracted'
                        })
                    
                    df_summary = pd.DataFrame(summary_data)
                    st.dataframe(df_summary, use_container_width=True)
                    
                    # Download button
                    with open(excel_filename, 'rb') as f:
                        st.download_button(
                            label="📥 Download Sales Excel File",
                            data=f,
                            file_name=excel_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.error("❌ Failed to create Excel file")
            else:
                st.warning("⚠️ No sales invoices were successfully processed")

if __name__ == "__main__":
    main()