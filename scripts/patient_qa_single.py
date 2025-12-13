#!/usr/bin/env python3
"""
Single Patient Q&A - Load only one patient's discharge summary for Q&A
Designed for efficient single-patient use cases
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


def view_patient_record(hadm_id: int, data_path: str):
  """View a patient's discharge summary"""
  print("\n" + "="*70)
  print(f"PATIENT DISCHARGE SUMMARY - HADM ID: {hadm_id}")
  print("="*70)
 
  df = pd.read_csv(data_path)
  record = df[df['hadm_id'] == float(hadm_id)]
 
  if len(record) == 0:
    print(f"\n No record found with HADM ID: {hadm_id}")
    return False
 
  record = record.iloc[0]
 
  print(f"\n📋 Patient Information:")
  print(f"  Subject ID: {record.get('subject_id', 'N/A')}")
  print(f"  Age: {record.get('age_at_admission', 'N/A')}")
  print(f"  Gender: {record.get('gender', 'N/A')}")
 
  # Show text preview
  text_column = 'cleaned_text_final' if 'cleaned_text_final' in record else 'cleaned_text'
  text = str(record.get(text_column, ''))
 
  if text:
    print(f"\n📄 Discharge Summary Preview (first 800 characters):")
    print("-"*70)
    print(text[:800] + "..." if len(text) > 800 else text)
    print("-"*70)
  else:
    print("\n⚠️ No text content found in this record")
    return False
 
  print("\n" + "="*70 + "\n")
  return True


def interactive_single_patient(hadm_id: int, data_path: str):
  """Interactive Q&A for a single patient"""
  print("\n" + "="*70)
  print(f"SINGLE PATIENT Q&A - HADM ID: {hadm_id}")
  print("="*70)
  print("\nThis system loads ONLY this patient's discharge summary.")
  print("All questions will be answered based on this patient's report.\n")
 
  print("Initializing RAG system (loading only this patient's data)...")
  print("This will be fast since we're only processing one record!\n")
 
  try:
    qa_system = PatientQA(
      data_path=data_path,
      hadm_id=hadm_id # Single-patient mode
    )
    print(" RAG System ready!\n")
  except Exception as e:
    print(f"\n Failed to initialize RAG system: {e}")
    print("\nTroubleshooting:")
    print("1. Verify the HADM ID exists in the dataset")
    print("2. Install dependencies: pip install sentence-transformers faiss-cpu")
    print("3. Set GOOGLE_API_KEY: export GOOGLE_API_KEY='your-key'")
    return
 
  print("="*70)
  print("INTERACTIVE Q&A SESSION")
  print("="*70)
  print("\nYou can ask questions about this patient's discharge summary.")
  print("Type 'exit' or 'quit' to end the session.")
  print("Type 'help' for example questions.")
  print("Type 'summary' to see the full record summary.\n")
 
  while True:
    try:
      question = input("❓ Your question: ").strip()
     
      if not question:
        continue
     
      if question.lower() in ['exit', 'quit', 'q']:
        print("\n👋 Thank you for using Patient Q&A. Take care!")
        break
     
      if question.lower() == 'help':
        print("\n💡 Example questions you can ask:")
        print(" • What are my diagnoses?")
        print(" • What medications do I need to take?")
        print(" • When is my follow-up appointment?")
        print(" • What were the lab results?")
        print(" • What happened during my hospital stay?")
        print(" • What are my discharge instructions?")
        print(" • What should I watch for at home?")
        print(" • Can you explain my condition in simple terms?")
        print()
        continue
     
      if question.lower() == 'summary':
        summary = qa_system.get_record_summary(hadm_id)
        if summary:
          print("\n" + "="*70)
          print("RECORD SUMMARY")
          print("="*70)
          for key, value in summary.items():
            if key not in ['text_length']:
              print(f" {key.replace('_', ' ').title()}: {value}")
          print("="*70 + "\n")
        continue
     
      # Answer the question (no need for hadm_id filter since we're in single-patient mode)
      print("\n🔍 Searching the discharge summary...")
      result = qa_system.ask_question(question)
     
      print("\n" + "="*70)
      print("ANSWER")
      print("="*70)
      print(f"\n{result.get('answer', 'No answer available')}\n")
     
      if result.get('sources'):
        print("-"*70)
        print(f"📚 Sources: {len(result['sources'])} relevant sections found")
        print(f"  Top relevance score: {result['sources'][0]['score']:.3f}")
        print("-"*70)
     
      if 'error' in result:
        print(f"\n⚠️ Error: {result['error']}")
     
      print("="*70 + "\n")
   
    except KeyboardInterrupt:
      print("\n\n👋 Session interrupted. Goodbye!")
      break
    except Exception as e:
      print(f"\n Error: {e}\n")
      logger.error(f"Error in interactive mode: {e}", exc_info=True)


def main():
  parser = argparse.ArgumentParser(
    description='Single Patient Q&A - Load only one patient\'s discharge summary',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
 # Interactive Q&A for a specific patient (recommended)
 python scripts/patient_qa_single.py --hadm-id 130656

 # View patient record first, then ask questions
 python scripts/patient_qa_single.py --hadm-id 130656 --view

 # Ask a single question
 python scripts/patient_qa_single.py --hadm-id 130656 --question "What are my diagnoses?"
    """
  )
 
  parser.add_argument(
    '--hadm-id',
    type=int,
    required=True,
    help='HADM ID of the patient (required)'
  )
 
  parser.add_argument(
    '--data-path',
    type=str,
    default='data_pipeline/data/processed/processed_discharge_summaries.csv',
    help='Path to processed discharge summaries CSV'
  )
 
  parser.add_argument(
    '--view',
    action='store_true',
    help='View patient record summary before Q&A'
  )
 
  parser.add_argument(
    '--question',
    type=str,
    help='Single question to answer (if not provided, enters interactive mode)'
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
    print(f"\n Data file not found: {data_path}")
    sys.exit(1)
 
  # View record if requested
  if args.view:
    view_patient_record(args.hadm_id, str(data_path))
 
  # Single question mode
  if args.question:
    print("\n" + "="*70)
    print(f"SINGLE PATIENT Q&A - HADM ID: {args.hadm_id}")
    print("="*70)
    print("\nLoading only this patient's discharge summary...\n")
   
    try:
      qa_system = PatientQA(
        data_path=str(data_path),
        hadm_id=args.hadm_id,
        embedding_model=args.embedding_model,
        gemini_model=args.gemini_model
      )
      print(" RAG System ready!\n")
     
      result = qa_system.ask_question(args.question)
     
      print("="*70)
      print("QUESTION")
      print("="*70)
      print(f"\n{args.question}\n")
     
      print("="*70)
      print("ANSWER")
      print("="*70)
      print(f"\n{result.get('answer', 'No answer available')}\n")
     
      if result.get('sources'):
        print(f"📚 Sources: {len(result['sources'])} relevant sections found")
     
      print("="*70 + "\n")
   
    except Exception as e:
      print(f"\n Error: {e}")
      sys.exit(1)
 
  else:
    # Interactive mode
    interactive_single_patient(args.hadm_id, str(data_path))


if __name__ == "__main__":
  main()






