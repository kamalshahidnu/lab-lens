#!/usr/bin/env python3
"""
Interactive File Q&A Script
Upload text, PDF, or image files and ask questions about them
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.file_qa import FileQA
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def print_answer(result: dict):
    """Print answer in a formatted way"""
    print("\n" + "="*70)
    print("ANSWER")
    print("="*70)
    print(f"\n{result.get('answer', 'No answer available')}\n")
    
    if 'error' in result:
        print(f"⚠️  Error: {result['error']}\n")
    
    if result.get('sources'):
        print("-"*70)
        print(f"📚 Sources: {result.get('num_sources', 0)} relevant sections found")
        if len(result['sources']) > 0:
            first_source = result['sources'][0]
            if 'score' in first_source:
                print(f"   Top relevance score: {first_source['score']:.3f}")
            if 'chunk' in first_source:
                print(f"\n   Top source preview:")
                print(f"   {first_source['chunk'][:150]}...")
        print("-"*70)
    
    print("="*70 + "\n")


def interactive_mode(qa_system: FileQA):
    """Interactive Q&A session"""
    print("\n" + "="*70)
    print("FILE-BASED Q&A SYSTEM")
    print("="*70)
    print("\nYou can ask questions about the loaded document(s).")
    print("Type 'exit' or 'quit' to end the session.")
    print("Type 'help' for example questions.")
    print("Type 'reload' to load a new file.")
    print("-"*70 + "\n")
    
    while True:
        try:
            question = input("❓ Your question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Thank you for using File Q&A. Goodbye!")
                break
            
            if question.lower() == 'help':
                print("\n💡 Example questions you can ask:")
                print("  • What is the main diagnosis?")
                print("  • What medications are mentioned?")
                print("  • What are the key findings?")
                print("  • What are the lab results?")
                print("  • Can you summarize the document?")
                print("  • What procedures were performed?")
                print("  • What are the discharge instructions?")
                print()
                continue
            
            if question.lower() == 'reload':
                file_path = input("Enter file path (or press Enter to cancel): ").strip()
                if file_path:
                    try:
                        result = qa_system.load_file(file_path)
                        if result.get('success'):
                            print(f"\n✅ File loaded: {result['file_name']}")
                            print(f"   Type: {result['file_type']}")
                            print(f"   Text length: {result['text_length']} characters")
                            print(f"   Created {result['num_chunks']} chunks\n")
                        else:
                            print(f"\n❌ Failed to load file: {result.get('error', 'Unknown error')}\n")
                    except Exception as e:
                        print(f"\n❌ Error loading file: {e}\n")
                continue
            
            # Answer the question
            result = qa_system.ask_question(question)
            print_answer(result)
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            logger.error(f"Error in interactive mode: {e}", exc_info=True)


def detect_input_type(input_str: str) -> str:
    """
    Automatically detect if input is a file path or raw text
    
    Args:
        input_str: Input string to analyze
        
    Returns:
        'file' if it's a file path, 'text' if it's raw text
    """
    input_path = Path(input_str)
    
    # Check if it's an existing file
    if input_path.exists() and input_path.is_file():
        return 'file'
    
    # Check if it looks like a file path (has extension and reasonable length)
    if input_path.suffix and len(input_str) < 500:
        # Might be a file path that doesn't exist yet
        return 'file'
    
    # Otherwise, treat as raw text
    return 'text'


def main():
    parser = argparse.ArgumentParser(
        description='Interactive File Q&A - Upload documents and ask questions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect: File path (text, PDF, or image)
  python scripts/file_qa_interactive.py report.pdf
  python scripts/file_qa_interactive.py report.txt
  python scripts/file_qa_interactive.py scan.jpg
  
  # Auto-detect: Multiple files
  python scripts/file_qa_interactive.py report1.pdf report2.txt scan.jpg
  
  # Auto-detect: Raw text (if not a file path)
  python scripts/file_qa_interactive.py "Patient report content..."
  
  # Interactive mode without loading anything
  python scripts/file_qa_interactive.py
  
  # Answer a single question
  python scripts/file_qa_interactive.py report.pdf --question "What is the diagnosis?"
        """
    )
    
    parser.add_argument(
        'input',
        nargs='*',
        help='File path(s) or raw text content (auto-detected)'
    )
    
    parser.add_argument(
        '--question',
        type=str,
        help='Single question to answer (non-interactive)'
    )
    
    parser.add_argument(
        '--embedding-model',
        type=str,
        default='all-MiniLM-L6-v2',
        help='Sentence transformer model for embeddings'
    )
    
    parser.add_argument(
        '--gemini-model',
        type=str,
        default='gemini-2.0-flash-exp',
        help='Gemini model for answer generation'
    )
    
    args = parser.parse_args()
    
    # Initialize File QA system
    print("\n" + "="*70)
    print("INITIALIZING FILE Q&A SYSTEM")
    print("="*70)
    print("\n⏳ Setting up RAG system...\n")
    
    try:
        # Get API key from environment
        api_key = os.getenv('GOOGLE_API_KEY')
        
        qa_system = FileQA(
            embedding_model=args.embedding_model,
            gemini_model=args.gemini_model,
            gemini_api_key=api_key
        )
        print("✅ File Q&A System ready!\n")
    except Exception as e:
        print(f"\n❌ Failed to initialize system: {e}")
        print("\nTroubleshooting:")
        print("1. Install dependencies: pip install sentence-transformers faiss-cpu")
        print("2. For PDF: pip install PyPDF2 or pip install pdfplumber")
        print("3. For images: pip install pytesseract pillow")
        print("4. Set GOOGLE_API_KEY: export GOOGLE_API_KEY='your-key'")
        sys.exit(1)
    
    # Load documents - auto-detect input type
    documents_loaded = False
    
    if args.input:
        # Auto-detect: multiple inputs = multiple files
        if len(args.input) > 1:
            # Multiple files
            try:
                result = qa_system.load_multiple_files(args.input)
                if result.get('success'):
                    print("="*70)
                    print("FILES LOADED")
                    print("="*70)
                    print(f"\n📄 Files: {result['num_files']} files")
                    print(f"   Total chunks: {result['num_chunks']}")
                    print(f"   Files: {', '.join(result['files'])}")
                    print("\n" + "="*70 + "\n")
                    documents_loaded = True
                else:
                    print(f"\n❌ Failed to load files: {result.get('error', 'Unknown error')}")
                    sys.exit(1)
            except Exception as e:
                print(f"\n❌ Error loading files: {e}")
                sys.exit(1)
        
        else:
            # Single input - auto-detect if file or text
            input_str = args.input[0]
            input_type = detect_input_type(input_str)
            
            if input_type == 'file':
                # It's a file path
                try:
                    result = qa_system.load_file(input_str)
                    if result.get('success'):
                        print("="*70)
                        print("FILE LOADED")
                        print("="*70)
                        print(f"\n📄 File: {result['file_name']}")
                        print(f"   Type: {result['file_type']}")
                        print(f"   Text length: {result['text_length']} characters")
                        print(f"   Created {result['num_chunks']} chunks")
                        print(f"\n📝 Preview:")
                        print(f"   {result['preview']}")
                        print("\n" + "="*70 + "\n")
                        documents_loaded = True
                    else:
                        print(f"\n❌ Failed to load file: {result.get('error', 'Unknown error')}")
                        sys.exit(1)
                except Exception as e:
                    print(f"\n❌ Error loading file: {e}")
                    sys.exit(1)
            else:
                # It's raw text
                try:
                    result = qa_system.load_text(input_str)
                    if result.get('success'):
                        print("="*70)
                        print("TEXT LOADED")
                        print("="*70)
                        print(f"\n📄 Source: {result['source_name']}")
                        print(f"   Text length: {result['text_length']} characters")
                        print(f"   Created {result['num_chunks']} chunks")
                        print(f"\n📝 Preview:")
                        print(f"   {result['preview']}")
                        print("\n" + "="*70 + "\n")
                        documents_loaded = True
                    else:
                        print(f"\n❌ Failed to load text")
                        sys.exit(1)
                except Exception as e:
                    print(f"\n❌ Error loading text: {e}")
                    sys.exit(1)
    
    if not documents_loaded:
        print("\n⚠️  No documents loaded. Starting interactive mode.")
        print("   You can type 'reload' and enter a file path to load a document.\n")
    
    # Answer single question or start interactive mode
    if args.question:
        if not documents_loaded:
            print("❌ No documents loaded. Please provide --file, --files, or --text")
            sys.exit(1)
        
        print("="*70)
        print("QUESTION")
        print("="*70)
        print(f"\n{args.question}\n")
        
        result = qa_system.ask_question(args.question)
        print_answer(result)
    else:
        # Interactive mode
        interactive_mode(qa_system)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

