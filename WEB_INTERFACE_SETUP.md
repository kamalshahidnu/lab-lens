# 🌐 Lab Lens Web Interface - Setup & Run Guide

Complete guide for setting up and running the Lab Lens File Q&A web interface.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start for Collaborators](#quick-start-for-collaborators)
3. [Detailed Setup Instructions](#detailed-setup-instructions)
4. [Running the Application](#running-the-application)
5. [Using the Interface](#using-the-interface)
6. [Troubleshooting](#troubleshooting)
7. [Development Tips](#development-tips)

---

## Prerequisites

Before running the web interface, ensure you have:

- **Python 3.9+** (Python 3.12 recommended)
- **pip** (Python package installer)
- **Git** (to clone the repository)
- **Gemini API Key** (from Google AI Studio: https://makersuite.google.com/app/apikey)

---

## Quick Start for Collaborators

If you're a collaborator cloning this repository for the first time, follow these steps:

### Step 1: Clone the Repository

```bash
git clone https://github.com/kamalshahidnu/lab-lens.git
cd lab-lens
```

**OR** if you're already in the repository and need to pull latest changes:

```bash
git pull origin main
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install --upgrade pip
pip install -r requirements.txt

# Ensure PDF processing library is installed
pip install pdfplumber
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root directory:

```bash
# Create .env file
touch .env
```

Add your Gemini API key to the `.env` file:

```env
GEMINI_API_KEY=your-gemini-api-key-here
GOOGLE_API_KEY=your-gemini-api-key-here
```

**⚠️ Important:** 
- Never commit the `.env` file to git (it's already in `.gitignore`)
- Get your API key from: https://makersuite.google.com/app/apikey
- Each collaborator needs their own API key

### Step 5: Run the Application

```bash
streamlit run scripts/file_qa_web.py
```

The application will automatically open in your browser at `http://localhost:8501`

---

## Detailed Setup Instructions

### For First-Time Setup

1. **Check Python Version**
   ```bash
   python3 --version
   # Should be 3.9 or higher
   ```

2. **Install System Dependencies (if needed)**
   ```bash
   # macOS
   brew install python3
   
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-venv
   
   # Windows
   # Download from https://www.python.org/downloads/
   ```

3. **Verify Installation**
   ```bash
   pip install --upgrade pip
   pip install streamlit
   streamlit --version
   ```

### Environment Variables Setup

You can set environment variables in multiple ways:

#### Option 1: Using `.env` file (Recommended)

Create `.env` file in project root:
```env
GEMINI_API_KEY=your-actual-api-key
GOOGLE_API_KEY=your-actual-api-key
MODEL_ID=asadwaraich/bart-medical-discharge-summarizer
```

The application will automatically load variables from `.env` if `python-dotenv` is installed (included in requirements.txt).

#### Option 2: Export in Terminal (Temporary)

```bash
# macOS/Linux
export GEMINI_API_KEY="your-api-key"
export GOOGLE_API_KEY="your-api-key"

# Windows (PowerShell)
$env:GEMINI_API_KEY="your-api-key"
$env:GOOGLE_API_KEY="your-api-key"

# Windows (CMD)
set GEMINI_API_KEY=your-api-key
set GOOGLE_API_KEY=your-api-key
```

#### Option 3: Set in System Environment Variables

**macOS/Linux:**
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export GEMINI_API_KEY="your-api-key"
export GOOGLE_API_KEY="your-api-key"
```

**Windows:**
- Open System Properties → Environment Variables
- Add new user variables with your API key

---

## Running the Application

### Standard Run

```bash
streamlit run scripts/file_qa_web.py
```

### Run with Custom Port

```bash
streamlit run scripts/file_qa_web.py --server.port 8502
```

### Run on Network (Accessible from other devices)

```bash
streamlit run scripts/file_qa_web.py --server.port 8501 --server.address 0.0.0.0
```

### Run in Headless Mode (No browser auto-open)

```bash
streamlit run scripts/file_qa_web.py --server.headless true
```

---

## Using the Interface

### 1. Upload Documents

- Click the **➕** button in the chat input area
- Or use the file upload section in the sidebar
- Supported formats:
  - **Text**: `.txt`, `.md`
  - **PDF**: `.pdf`
  - **Images**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`
- Click **"📥 Load Documents"** to process

### 2. Ask Questions

- Type your question in the chat input at the bottom
- The system will:
  - Use BioBERT embeddings for document retrieval
  - Use Gemini API for answer generation
  - Automatically simplify medical terms in responses

### 3. Get Document Summary

- Type **"summarize"** (or variations like "summary", "summarise")
- The system will use `MedicalSummarizer` (BART model + RAG + Gemini refinement)
- Returns a patient-friendly summary in 3-part format:
  - **What Happened**
  - **What Was Done**
  - **What is Next**

### 4. Chat History

- All conversations are saved in the sidebar
- Click on previous chats to resume
- Click **"➕ New Chat"** to start fresh

---

## Troubleshooting

### Issue: "ModuleNotFoundError" or Import Errors

**Solution:**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# If specific module missing:
pip install streamlit pdfplumber sentence-transformers
```

### Issue: "GEMINI_API_KEY not found"

**Solution:**
1. Check if `.env` file exists in project root
2. Verify API key is correctly set:
   ```bash
   # Test in Python
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"
   ```
3. Try exporting directly:
   ```bash
   export GEMINI_API_KEY="your-key"
   ```

### Issue: "PDF processing requires PyPDF2 or pdfplumber"

**Solution:**
```bash
pip install pdfplumber
```

### Issue: Port 8501 Already in Use

**Solution:**
```bash
# Option 1: Use different port
streamlit run scripts/file_qa_web.py --server.port 8502

# Option 2: Kill existing process
# macOS/Linux:
lsof -ti:8501 | xargs kill -9

# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

### Issue: "BioBERT model loading fails"

**Solution:**
- First-time use will download the model (~400MB)
- Ensure stable internet connection
- Check available disk space
- Model is cached after first download

### Issue: Slow Initial Load

**Solution:**
- First request loads models (MedicalSummarizer, BioBERT)
- This is normal and takes 30-60 seconds
- Subsequent requests are much faster
- Models are cached for the session

### Issue: Memory Errors

**Solution:**
- Ensure at least 4GB RAM available
- Close other applications
- MedicalSummarizer requires ~1-2GB RAM
- Consider using CPU-only mode (already default)

---

## Development Tips

### For Collaborators Working on the Code

1. **Use Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. **Install Development Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install black flake8 pytest  # Optional: for code formatting and testing
   ```

3. **Testing Changes**
   ```bash
   # Run in development mode with auto-reload
   streamlit run scripts/file_qa_web.py --server.runOnSave true
   ```

4. **Check Code Before Committing**
   ```bash
   # Ensure .env is not committed
   git status
   # Should NOT show .env file
   ```

### Common Commands Reference

```bash
# Check if Streamlit is installed
streamlit --version

# View Streamlit help
streamlit --help

# Clear Streamlit cache
streamlit cache clear

# Check Python environment
python --version
pip list | grep streamlit
```

---

## File Structure for Collaborators

```
lab-lens/
├── scripts/
│   └── file_qa_web.py          # Main web interface (Streamlit app)
├── src/
│   ├── rag/
│   │   ├── file_qa.py          # FileQA class with BioBERT support
│   │   ├── rag_system.py       # RAG system with BioBERT option
│   │   └── document_processor.py  # PDF/text/image processing
│   └── utils/
│       └── medical_utils.py    # Medical utilities (BioBERT, term simplifier)
├── model-deployment/
│   └── deployment_pipeline/
│       └── summarizer.py       # MedicalSummarizer (BART model)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (NOT in git)
└── WEB_INTERFACE_SETUP.md      # This file
```

---

## Environment Variables Reference

| Variable | Required | Description | Where to Get |
|----------|----------|-------------|--------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key | https://makersuite.google.com/app/apikey |
| `GOOGLE_API_KEY` | Optional | Alias for GEMINI_API_KEY | Same as above |
| `MODEL_ID` | No | BART model ID (default provided) | Already configured |

---

## Getting Your Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key
5. Add it to your `.env` file or export as environment variable

**Note:** Free tier includes generous usage limits. Check Google AI Studio for current limits.

---

## Next Steps

- ✅ Application running successfully
- 📖 Read [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for production deployment
- 🐛 Report issues in GitHub Issues
- 💡 Check [docs/](./docs/) for more documentation

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review error messages in the terminal
3. Check GitHub Issues: https://github.com/kamalshahidnu/lab-lens/issues
4. Contact the team or create a new issue

---

## Quick Command Cheat Sheet

```bash
# Setup (one-time)
git clone https://github.com/kamalshahidnu/lab-lens.git
cd lab-lens
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
echo "GEMINI_API_KEY=your-key" > .env

# Run (every time)
source venv/bin/activate  # If using venv
streamlit run scripts/file_qa_web.py
```

---

**Happy coding! 🚀**
