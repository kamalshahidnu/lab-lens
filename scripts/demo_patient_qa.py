#!/usr/bin/env python3
"""
Quick Demo Script for Patient Q&A System
Demonstrates basic RAG functionality
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.patient_qa import PatientQA


def demo():
  """Quick demo of patient Q&A system"""
  print("="*70)
  print("PATIENT Q&A SYSTEM DEMO")
  print("="*70)
  print("\nThis demo shows how patients can ask questions about their discharge summaries.")
  print("Note: First run will take a few minutes to create embeddings.\n")
 
  # Initialize system
  data_path = "data_pipeline/data/processed/processed_discharge_summaries.csv"
 
  if not Path(data_path).exists():
    print(f" Data file not found: {data_path}")
    print("\nPlease ensure the processed discharge summaries CSV exists.")
    return
 
  print(f"📂 Loading data from: {data_path}")
  print("⏳ Creating embeddings (this may take a few minutes on first run)...\n")
 
  try:
    qa_system = PatientQA(data_path=data_path)
    print(" System ready!\n")
  except Exception as e:
    print(f"\n Failed to initialize system: {e}")
    print("\nTroubleshooting:")
    print("1. Install dependencies: pip install sentence-transformers faiss-cpu")
    print("2. Set GOOGLE_API_KEY: export GOOGLE_API_KEY='your-key'")
    print("3. Check that the data file exists")
    return
 
  # Demo questions
  demo_questions = [
    "What are my diagnoses?",
    "What medications do I need to take?",
    "When is my follow-up appointment?",
    "What happened during my hospital stay?"
  ]
 
  print("="*70)
  print("DEMO: Answering Sample Questions")
  print("="*70)
  print("\nNote: Using first available record. Use --hadm-id for specific patients.\n")
 
  # Get first HADM ID for demo
  import pandas as pd
  df = pd.read_csv(data_path)
  if len(df) > 0:
    first_hadm_id = int(df.iloc[0]['hadm_id'])
    print(f"📋 Using HADM ID: {first_hadm_id} (first record)\n")
  else:
    first_hadm_id = None
    print("⚠️ No records found in data file\n")
 
  # Answer questions
  for i, question in enumerate(demo_questions, 1):
    print(f"\n{'─'*70}")
    print(f"QUESTION {i}: {question}")
    print(f"{'─'*70}")
   
    result = qa_system.ask_question(question, hadm_id=first_hadm_id)
   
    print(f"\n📝 Answer:")
    print(f"{result['answer']}\n")
   
    if result.get('sources'):
      print(f"📚 Sources: {len(result['sources'])} relevant sections found")
      print(f"  Top source score: {result['sources'][0]['score']:.3f}\n")
 
  print("="*70)
  print("DEMO COMPLETE")
  print("="*70)
  print("\n💡 Try interactive mode:")
  print("  python scripts/patient_qa_interactive.py")
  print("\n💡 Ask your own questions:")
  print("  python scripts/patient_qa_interactive.py --question 'Your question here'")
  print("="*70 + "\n")


if __name__ == "__main__":
  demo()



