#!/usr/bin/env python3
"""
Test RAG System with a Specific Discharge Summary Record
Allows you to view a summary and ask questions about it
"""

import os
import sys
import argparse
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.patient_qa import PatientQA
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def view_record_summary(hadm_id: int, data_path: str):
    """Display summary information about a specific record"""
    print("\n" + "="*70)
    print(f"DISCHARGE SUMMARY - HADM ID: {hadm_id}")
    print("="*70)
    
    df = pd.read_csv(data_path)
    record = df[df['hadm_id'] == float(hadm_id)]
    
    if len(record) == 0:
        print(f"\n❌ No record found with HADM ID: {hadm_id}")
        print("\nAvailable HADM IDs (first 10):")
        print(df[['hadm_id', 'subject_id']].head(10).to_string())
        return False
    
    record = record.iloc[0]
    
    # Display key information
    print(f"\n📋 Patient Information:")
    print(f"   Subject ID: {record.get('subject_id', 'N/A')}")
    print(f"   Age: {record.get('age_at_admission', 'N/A')}")
    print(f"   Gender: {record.get('gender', 'N/A')}")
    
    # Show text preview
    text_column = 'cleaned_text_final' if 'cleaned_text_final' in record else 'cleaned_text'
    text = str(record.get(text_column, ''))
    
    if text:
        preview_length = 500
        print(f"\n📄 Discharge Summary Preview (first {preview_length} characters):")
        print("-"*70)
        print(text[:preview_length] + "..." if len(text) > preview_length else text)
        print("-"*70)
        
        # Show diagnosis if available
        if 'discharge_diagnosis' in record and pd.notna(record.get('discharge_diagnosis')):
            print(f"\n🏥 Diagnoses:")
            print(f"   {record.get('discharge_diagnosis', 'N/A')}")
        
        # Show medications if available
        if 'discharge_medications' in record and pd.notna(record.get('discharge_medications')):
            meds = str(record.get('discharge_medications', 'N/A'))
            if len(meds) > 200:
                meds = meds[:200] + "..."
            print(f"\n💊 Medications:")
            print(f"   {meds}")
    else:
        print("\n⚠️  No text content found in this record")
        return False
    
    print("\n" + "="*70 + "\n")
    return True


def test_questions(qa_system: PatientQA, hadm_id: int, questions: list = None):
    """Test the RAG system with specific questions"""
    
    if questions is None:
        # Default test questions
        questions = [
            "What are my diagnoses?",
            "What medications do I need to take?",
            "What happened during my hospital stay?",
            "What are my discharge instructions?",
            "When is my follow-up appointment?"
        ]
    
    print("\n" + "="*70)
    print("TESTING RAG SYSTEM WITH QUESTIONS")
    print("="*70)
    print(f"\n📋 Testing with HADM ID: {hadm_id}\n")
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'─'*70}")
        print(f"QUESTION {i}/{len(questions)}: {question}")
        print(f"{'─'*70}")
        
        try:
            result = qa_system.ask_question(question, hadm_id=hadm_id)
            
            print(f"\n📝 Answer:")
            print(f"{result.get('answer', 'No answer generated')}\n")
            
            if result.get('sources'):
                print(f"📚 Sources: {len(result['sources'])} relevant sections found")
                if len(result['sources']) > 0:
                    first_source = result['sources'][0]
                    if 'score' in first_source:
                        print(f"   Top source relevance score: {first_source['score']:.3f}")
                    if 'chunk' in first_source:
                        print(f"\n   Top source preview:")
                        print(f"   {first_source['chunk'][:150]}...")
            else:
                print("⚠️  No relevant sources found")
            
            if 'error' in result:
                print(f"\n⚠️  Error: {result['error']}")
        
        except Exception as e:
            print(f"\n❌ Error answering question: {e}")
            logger.error(f"Error in question {i}: {e}", exc_info=True)
    
    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70 + "\n")


def list_available_records(data_path: str, limit: int = 10):
    """List available HADM IDs"""
    df = pd.read_csv(data_path)
    print("\n" + "="*70)
    print("AVAILABLE RECORDS (Sample)")
    print("="*70)
    print(f"\nTotal records in dataset: {len(df)}\n")
    print("First {} HADM IDs:\n".format(limit))
    
    sample = df[['hadm_id', 'subject_id']].head(limit)
    print(sample.to_string(index=False))
    print("\n" + "="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Test RAG System with a Specific Discharge Summary',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available records
  python scripts/test_rag_with_record.py --list-records
  
  # View a specific record summary
  python scripts/test_rag_with_record.py --view-record 130656
  
  # Test RAG with a specific record (using default questions)
  python scripts/test_rag_with_record.py --test 130656
  
  # Test with custom questions
  python scripts/test_rag_with_record.py --test 130656 \\
    --questions "What are my diagnoses?" "What medications do I need?"
  
  # View record and then test
  python scripts/test_rag_with_record.py --view-record 130656 --test 130656
        """
    )
    
    parser.add_argument(
        '--data-path',
        type=str,
        default='data_pipeline/data/processed/processed_discharge_summaries.csv',
        help='Path to processed discharge summaries CSV'
    )
    
    parser.add_argument(
        '--list-records',
        action='store_true',
        help='List available HADM IDs'
    )
    
    parser.add_argument(
        '--view-record',
        type=int,
        help='View discharge summary for a specific HADM ID'
    )
    
    parser.add_argument(
        '--test',
        type=int,
        help='Test RAG system with a specific HADM ID'
    )
    
    parser.add_argument(
        '--questions',
        nargs='+',
        help='Custom questions to ask (use with --test)'
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
    
    data_path = Path(args.data_path)
    if not data_path.exists():
        print(f"\n❌ Data file not found: {data_path}")
        print("\nPlease ensure the processed discharge summaries CSV exists.")
        sys.exit(1)
    
    # List records
    if args.list_records:
        list_available_records(str(data_path))
        return
    
    # View record
    if args.view_record:
        view_record_summary(args.view_record, str(data_path))
    
    # Test RAG
    if args.test:
        hadm_id = args.test
        
        # Verify record exists
        df = pd.read_csv(data_path)
        if len(df[df['hadm_id'] == float(hadm_id)]) == 0:
            print(f"\n❌ No record found with HADM ID: {hadm_id}")
            print("\nUse --list-records to see available HADM IDs")
            sys.exit(1)
        
        print("\n" + "="*70)
        print("INITIALIZING RAG SYSTEM")
        print("="*70)
        print(f"\n📂 Loading data from: {data_path}")
        print(f"👤 Single-patient mode: Loading only HADM ID {hadm_id}")
        print("⏳ Creating embeddings (this may take a few minutes on first run)...\n")
        
        try:
            qa_system = PatientQA(
                data_path=str(data_path),
                embedding_model=args.embedding_model,
                gemini_model=args.gemini_model,
                hadm_id=hadm_id  # Load only this patient's record
            )
            print("✅ RAG System ready!\n")
        except Exception as e:
            print(f"\n❌ Failed to initialize RAG system: {e}")
            print("\nTroubleshooting:")
            print("1. Install dependencies: pip install sentence-transformers faiss-cpu")
            print("2. Set GOOGLE_API_KEY: export GOOGLE_API_KEY='your-key'")
            print("3. Check that the data file exists")
            sys.exit(1)
        
        # Test with questions
        test_questions(qa_system, hadm_id, args.questions)
    
    if not args.list_records and not args.view_record and not args.test:
        parser.print_help()


if __name__ == "__main__":
    main()




