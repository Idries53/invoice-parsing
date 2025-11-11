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
</style>
""", unsafe_allow_html=True)

# API Key Configuration
LLAMA_KEY = st.secrets.get("LLAMA_CLOUD_API_KEY") or os.getenv("LLAMA_CLOUD_API_KEY")
GOOGLE_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not (LLAMA_KEY and GOOGLE_KEY):
    st.error("⚠️ Missing API keys. Please set environment variables or Streamlit secrets:")
    st.code("""
    LLAMA_CLOUD_API_KEY=your_llama_key
    GOOGLE_API_KEY=your_google_key
    """)
    st.stop()

genai.configure(api_key=GOOGLE_KEY)

# Enhanced Gemini Prompt
GEMINI_PROMPT = """You are an expert invoice data extraction system.

Analyze the invoice document and extract the following information with precision:

CRITICAL: Return ONLY a valid JSON object with NO additional text, explanations, or markdown formatting.

Required JSON structure:
{
  "date": "YYYY-MM-DD format (convert any date format to this)",
  "invoice_number": "string (invoice/bill number)",
  "party_name": "string (vendor/supplier name)",
  "party_address": "string (complete vendor address)",
  "trn": "string or null (Tax Registration Number/VAT/TIN)",
  "subtotal": number (amount before tax),
  "tax_amount": number (total tax/VAT amount),
  "net_total": number (final amount including tax),
  "currency": "string (currency code like USD, EUR, AED, etc.)",
  "items_count": number (number of line items, or null if not clear)
}

Rules:
- Use null for missing fields (not "N/A", "Unknown", or empty strings)
- All numbers must be numeric values without currency symbols
- Date must be in YYYY-MM-DD format
- Extract the most prominent company name as party_name
- Return ONLY the JSON object, no other text
"""

def clean_json_response(text: str) -> str:
    """Clean and extract JSON from Gemini response"""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    # Find JSON object
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text.strip()

def parse_invoice(pdf_file, parser, model) -> dict:
    """Parse a single invoice PDF and extract structured data"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_file.read())
            tmp_path = tmp.name
        
        # Parse PDF to markdown
        documents = parser.load_data(tmp_path)
        markdown_text = "\n".join(doc.text for doc in documents)
        
        # Clean up temp file
        os.remove(tmp_path)
        
        # Extract data with Gemini
        response = model.generate_content(GEMINI_PROMPT + "\n\nInvoice content:\n" + markdown_text)
        cleaned_response = clean_json_response(response.text)
        
        # Parse JSON
        data = json.loads(cleaned_response)
        
        # Add source filename
        data["source_file"] = pdf_file.name
        data["processing_status"] = "success"
        data["error_message"] = None
        
        return data
        
    except json.JSONDecodeError as e:
        st.warning(f"⚠️ JSON parsing error for {pdf_file.name}: {str(e)}")
        return {
            "source_file": pdf_file.name,
            "processing_status": "failed",
            "error_message": f"JSON parsing error: {str(e)}",
            "date": None, "invoice_number": None, "party_name": None,
            "party_address": None, "trn": None, "subtotal": None,
            "tax_amount": None, "net_total": None, "currency": None,
            "items_count": None
        }
    except Exception as e:
        st.error(f"❌ Error processing {pdf_file.name}: {str(e)}")
        return {
            "source_file": pdf_file.name,
            "processing_status": "failed",
            "error_message": str(e),
            "date": None, "invoice_number": None, "party_name": None,
            "party_address": None, "trn": None, "subtotal": None,
            "tax_amount": None, "net_total": None, "currency": None,
            "items_count": None
        }

def create_summary_stats(df: pd.DataFrame) -> dict:
    """Generate summary statistics from processed invoices"""
    successful = df[df['processing_status'] == 'success']
    return {
        "total_files": len(df),
        "successful": len(successful),
        "failed": len(df) - len(successful),
        "total_amount": successful['net_total'].sum() if len(successful) > 0 else 0,
        "avg_amount": successful['net_total'].mean() if len(successful) > 0 else 0,
        "total_tax": successful['tax_amount'].sum() if len(successful) > 0 else 0
    }

# ---------- UI ----------
st.markdown('<h1 class="main-header">📄 Invoice → Excel Converter</h1>', unsafe_allow_html=True)
st.markdown("---")

# Info section
with st.expander("ℹ️ How to use", expanded=False):
    st.markdown("""
    1. **Upload** one or multiple PDF invoices
    2. **Click Convert** to process all invoices
    3. **Review** the extracted data in the preview table
    4. **Download** the Excel file with all invoice data
    
    **Supported data:**
    - Invoice date, number, and party details
    - Financial amounts (subtotal, tax, total)
    - Tax registration numbers
    - Currency information
    """)

# File uploader
uploaded_files = st.file_uploader(
    "📤 Upload PDF Invoices",
    type=["pdf"],
    accept_multiple_files=True,
    help="You can upload multiple PDF invoices at once"
)

if uploaded_files:
    st.info(f"📊 {len(uploaded_files)} file(s) uploaded")

# Process button
if st.button("🚀 Convert Invoices", disabled=not uploaded_files):
    # Initialize parser and model
    parser = LlamaParse(api_key=LLAMA_KEY, result_type="markdown")
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    rows = []
    
    # Process each file
    for idx, pdf_file in enumerate(uploaded_files):
        status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {pdf_file.name}")
        
        # Reset file pointer
        pdf_file.seek(0)
        
        # Parse invoice
        invoice_data = parse_invoice(pdf_file, parser, model)
        rows.append(invoice_data)
        
        # Update progress
        progress_bar.progress((idx + 1) / len(uploaded_files))
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Reorder columns for better readability
    column_order = [
        "processing_status", "source_file", "date", "invoice_number",
        "party_name", "party_address", "trn", "currency",
        "subtotal", "tax_amount", "net_total", "items_count", "error_message"
    ]
    df = df[column_order]
    
    # Generate summary statistics
    stats = create_summary_stats(df)
    
    # Display results
    st.markdown("---")
    st.markdown("## 📊 Processing Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Files", stats["total_files"])
    with col2:
        st.metric("✅ Successful", stats["successful"])
    with col3:
        st.metric("❌ Failed", stats["failed"])
    with col4:
        st.metric("Total Amount", f"${stats['total_amount']:,.2f}")
    
    # Show warnings for failed files
    failed_files = df[df['processing_status'] == 'failed']
    if len(failed_files) > 0:
        with st.expander("⚠️ Failed Files Details", expanded=True):
            for _, row in failed_files.iterrows():
                st.error(f"**{row['source_file']}**: {row['error_message']}")
    
    # Display data table
    st.markdown("### 📋 Extracted Data")
    
    # Filter option
    show_filter = st.radio("Show:", ["All files", "Successful only", "Failed only"], horizontal=True)
    
    if show_filter == "Successful only":
        display_df = df[df['processing_status'] == 'success']
    elif show_filter == "Failed only":
        display_df = df[df['processing_status'] == 'failed']
    else:
        display_df = df
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Download section
    st.markdown("---")
    st.markdown("### 💾 Download Options")
    
    col1, col2 = st.columns(2)
    
    # Excel download (all data)
    with col1:
        excel_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        df.to_excel(excel_file.name, index=False, sheet_name="Invoices")
        
        with open(excel_file.name, "rb") as f:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                "📥 Download Excel (All Data)",
                data=f.read(),
                file_name=f"invoices_summary_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        os.remove(excel_file.name)
    
    # CSV download (successful only)
    with col2:
        successful_df = df[df['processing_status'] == 'success']
        if len(successful_df) > 0:
            csv = successful_df.drop(columns=['error_message']).to_csv(index=False)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                "📥 Download CSV (Success Only)",
                data=csv,
                file_name=f"invoices_successful_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    st.success("✅ Processing complete!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "Built with Streamlit • LlamaParse • Gemini AI"
    "</div>",
    unsafe_allow_html=True
)
