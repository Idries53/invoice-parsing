# 📄 Invoice to Excel Converter - Enhanced Version

An intelligent PDF invoice processing tool that extracts structured data and exports to Excel using LlamaParse and Google Gemini AI.

## 🚀 Key Enhancements

### 1. **Improved Error Handling**
- ✅ Graceful error recovery for individual files
- ✅ Detailed error messages for failed processing
- ✅ Continues processing even if some files fail
- ✅ JSON parsing with regex-based cleanup

### 2. **Enhanced UI/UX**
- 🎨 Modern gradient design with custom CSS
- 📊 Real-time progress bar for batch processing
- 📈 Summary statistics dashboard (total files, success rate, amounts)
- 🔍 Filter options (All/Successful/Failed)
- 💡 Expandable "How to use" guide

### 3. **Advanced Features**
- 💰 **Additional Data Fields**: Currency code and items count
- 📁 **Source Tracking**: Tracks which file each record came from
- 🚦 **Status Indicators**: Processing status for each invoice
- 📊 **Summary Metrics**: Total amount, average amount, total tax
- 📤 **Multiple Export Options**: Excel (all data) and CSV (successful only)
- 🕐 **Timestamped Downloads**: Auto-generated filenames with timestamps

### 4. **Better Data Extraction**
- 🧹 Robust JSON cleaning (removes markdown, extracts JSON objects)
- 🔄 Improved Gemini prompt with clearer instructions
- ✅ Validation and null handling
- 📋 Structured column ordering for readability

### 5. **Professional Features**
- 📂 Multiple sheet support in Excel
- 🎯 Better column organization
- 🚨 Warning system for failed files
- 📱 Responsive layout

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8 or higher
- LlamaParse API key ([Get it here](https://cloud.llamaindex.ai))
- Google AI Studio API key ([Get it here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or download the files**
```bash
# Create a new directory
mkdir invoice-converter
cd invoice-converter
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up API keys**

**Option A: Environment Variables**
```bash
export LLAMA_CLOUD_API_KEY="your_llama_key_here"
export GOOGLE_API_KEY="your_google_key_here"
```

**Option B: Streamlit Secrets** (Recommended for deployment)

Create `.streamlit/secrets.toml`:
```toml
LLAMA_CLOUD_API_KEY = "your_llama_key_here"
GOOGLE_API_KEY = "your_google_key_here"
```

4. **Run the application**
```bash
streamlit run invoice_to_excel_enhanced.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 How to Use

1. **Upload Invoices**: Drag and drop one or multiple PDF invoices
2. **Click Convert**: Start the extraction process
3. **Review Results**: Check the summary metrics and extracted data
4. **Filter Data**: View all files, successful only, or failed only
5. **Download**: Get Excel file with all data or CSV with successful records

## 📊 Extracted Fields

| Field | Description |
|-------|-------------|
| `date` | Invoice date (YYYY-MM-DD format) |
| `invoice_number` | Invoice/bill number |
| `party_name` | Vendor/supplier name |
| `party_address` | Complete vendor address |
| `trn` | Tax Registration Number (VAT/TIN) |
| `currency` | Currency code (USD, EUR, AED, etc.) |
| `subtotal` | Amount before tax |
| `tax_amount` | Total tax/VAT amount |
| `net_total` | Final amount including tax |
| `items_count` | Number of line items |
| `source_file` | Original PDF filename |
| `processing_status` | Success or failed |

## 🎯 Comparison: Original vs Enhanced

| Feature | Original | Enhanced |
|---------|----------|----------|
| Error handling | Basic | Robust with recovery |
| UI design | Simple | Modern with gradients |
| Progress tracking | Spinner only | Progress bar + status |
| Statistics | None | Full dashboard |
| Export options | Excel only | Excel + CSV |
| Failed file handling | Stops processing | Continues + reports |
| Data fields | 8 fields | 11 fields + metadata |
| JSON parsing | Basic | Regex cleanup + validation |
| File naming | Static | Timestamped |
| Data filtering | None | All/Success/Failed views |

## 🔧 Troubleshooting

### "Missing API keys" error
- Ensure environment variables are set correctly
- Check `.streamlit/secrets.toml` file exists and has correct format
- Restart the Streamlit server after setting env vars

### Processing fails for specific PDFs
- Check the "Failed Files Details" section for error messages
- Ensure PDFs are not password-protected
- Verify PDFs contain actual text (not scanned images without OCR)

### Slow processing
- LlamaParse and Gemini API calls take time per file
- Processing time depends on PDF complexity and file size
- Consider processing in smaller batches for large volumes

## 📝 Notes

- **API Costs**: Both LlamaParse and Gemini API have usage limits/costs
- **Accuracy**: Results depend on invoice format and quality
- **Privacy**: Files are processed through external APIs
- **Timeout**: Large files or many pages may timeout - consider splitting

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in Streamlit Cloud settings
5. Deploy!

### Local Production Run

```bash
streamlit run invoice_to_excel_enhanced.py --server.port 8501 --server.address 0.0.0.0
```

## 📄 License

Open source - feel free to modify and enhance!

## 🤝 Contributing

Suggestions for improvements:
- Add support for multi-page invoices
- Implement OCR for scanned documents
- Add batch export to Google Sheets
- Create invoice templates for common formats
- Add data validation rules
- Implement invoice categorization

---

**Built with ❤️ using Streamlit, LlamaParse, and Google Gemini AI**
