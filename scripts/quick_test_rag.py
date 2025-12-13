#!/usr/bin/env python3
"""
Quick RAG Test - Simple script to test RAG with a single question
Avoids embedding generation issues by checking for cached embeddings first
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.patient_qa import PatientQA


def quick_test(hadm_id: int, question: str = None, data_path: str = None):
    """Quick test of RAG system with minimal setup"""
    
    if data_path is None:
        data_path = "data_pipeline/data/processed/processed_discharge_summaries.csv"
    
    data_path = Path(data_path)
    if not data_path.exists():
        print(f"\n❌ Data file not found: {data_path}")
        return
    
    print("\n" + "="*70)
    print("QUICK RAG TEST")
    print("="*70)
    print(f"\n📋 HADM ID: {hadm_id}")
    
    if question is None:
        question = "What are my diagnoses?"
    
    print(f"❓ Question: {question}\n")
    
    # Check for cached embeddings
    cache_dir = Path("models/rag_embeddings")
    cache_files = list(cache_dir.glob("*.pkl")) if cache_dir.exists() else []
    
    if cache_files:
        print(f"✅ Found cached embeddings ({len(cache_files)} file(s))")
        print("   This will load quickly...\n")
    else:
        print("⚠️  No cached embeddings found.")
        print("   First run will create embeddings (may take 2-5 minutes)...\n")
    
    print("📂 Loading RAG system...")
    print("   This may take a moment...\n")
    
    try:
        # Initialize Q&A system
        qa_system = PatientQA(data_path=str(data_path))
        print("✅ RAG System ready!\n")
        
        # Ask question
        print("🔍 Processing question...\n")
        result = qa_system.ask_question(question, hadm_id=hadm_id)
        
        # Display results
        print("="*70)
        print("ANSWER")
        print("="*70)
        print(f"\n{result.get('answer', 'No answer available')}\n")
        
        if result.get('sources'):
            print("-"*70)
            print(f"📚 Sources: {len(result['sources'])} relevant sections found")
            print(f"   Top relevance score: {result['sources'][0]['score']:.3f}")
            print("-"*70)
        
        if 'error' in result:
            print(f"\n⚠️  Error: {result['error']}")
        
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check that GOOGLE_API_KEY is set")
        print("2. Verify the data file exists")
        print("3. Install dependencies: pip install sentence-transformers faiss-cpu")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description='Quick RAG Test')
    parser.add_argument('--hadm-id', type=int, required=True, help='HADM ID to test')
    parser.add_argument('--question', type=str, help='Question to ask (default: "What are my diagnoses?")')
    parser.add_argument('--data-path', type=str, help='Path to discharge summaries CSV')
    
    args = parser.parse_args()
    
    quick_test(args.hadm_id, args.question, args.data_path)


if __name__ == "__main__":
    main()






