#!/usr/bin/env python3
"""
Interactive Patient Q&A Script
Allows patients to ask questions about their discharge summaries using RAG
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.patient_qa import PatientQA
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def print_answer(result: dict, show_sources: bool = False):
    """Print answer in a formatted way"""
    print("\n" + "="*70)
    print("ANSWER")
    print("="*70)
    print(f"\n{result.get('answer', 'No answer available')}\n")
    
    if 'error' in result:
        print(f"⚠️  Error: {result['error']}\n")
    
    if show_sources and result.get('sources'):
        print("-"*70)
        print(f"📚 Sources ({result.get('num_sources', 0)} relevant sections found)")
        print("-"*70)
        for i, source in enumerate(result['sources'][:3], 1):  # Show top 3 sources
            print(f"\n[{i}] Relevance Score: {source['score']:.3f}")
            print(f"    HADM ID: {source.get('hadm_id', 'N/A')}")
            print(f"    Preview: {source['chunk'][:150]}...")
    
    print("="*70 + "\n")


def interactive_mode(qa_system: PatientQA, hadm_id: Optional[int] = None):
    """Interactive Q&A session"""
    print("\n" + "="*70)
    print("PATIENT DISCHARGE SUMMARY Q&A")
    print("="*70)
    print("\nYou can ask questions about your discharge summary.")
    print("Type 'exit' or 'quit' to end the session.")
    print("Type 'help' for example questions.")
    print("Type 'summary' to see your record summary (if HADM ID provided).")
    print("-"*70 + "\n")
    
    if hadm_id:
        print(f"📋 Session for HADM ID: {hadm_id}\n")
        summary = qa_system.get_record_summary(hadm_id)
        if summary:
            print("Patient Information:")
            print(f"  Age: {summary.get('age', 'N/A')}")
            print(f"  Gender: {summary.get('gender', 'N/A')}")
            print(f"  Diagnoses: {summary.get('diagnosis', 'N/A')[:100]}...")
            print()
    
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
                print("  • What are my diagnoses?")
                print("  • What medications do I need to take?")
                print("  • When is my follow-up appointment?")
                print("  • What were the lab results?")
                print("  • What happened during my hospital stay?")
                print("  • What are my discharge instructions?")
                print("  • What should I watch for at home?")
                print("  • Can you explain my condition in simple terms?")
                print()
                continue
            
            if question.lower() == 'summary' and hadm_id:
                summary = qa_system.get_record_summary(hadm_id)
                if summary:
                    print("\n" + "="*70)
                    print("RECORD SUMMARY")
                    print("="*70)
                    for key, value in summary.items():
                        if key not in ['text_length']:
                            print(f"  {key.replace('_', ' ').title()}: {value}")
                    print("="*70 + "\n")
                else:
                    print("\n⚠️  Summary not available for this HADM ID.\n")
                continue
            
            # Answer the question
            print("\n🔍 Searching your discharge summary...")
            result = qa_system.ask_question(question, hadm_id=hadm_id)
            print_answer(result, show_sources=True)
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            logger.error(f"Error in interactive mode: {e}", exc_info=True)


def batch_mode(qa_system: PatientQA, questions: list, hadm_id: Optional[int] = None):
    """Answer multiple questions at once"""
    print("\n" + "="*70)
    print("BATCH Q&A MODE")
    print("="*70)
    print(f"Answering {len(questions)} questions...\n")
    
    results = qa_system.ask_multiple_questions(questions, hadm_id=hadm_id)
    
    for i, (question, result) in enumerate(zip(questions, results), 1):
        print(f"\n{'='*70}")
        print(f"QUESTION {i}/{len(questions)}")
        print("="*70)
        print(f"\n❓ {question}\n")
        print_answer(result, show_sources=False)
    
    print("\n✅ All questions answered!\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Interactive Patient Q&A System for Discharge Summaries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (general questions)
  python scripts/patient_qa_interactive.py
  
  # Interactive mode for specific patient
  python scripts/patient_qa_interactive.py --hadm-id 130656
  
  # Answer a single question
  python scripts/patient_qa_interactive.py --question "What are my diagnoses?"
  
  # Answer multiple questions
  python scripts/patient_qa_interactive.py --questions "What are my diagnoses?" "What medications do I need?"
  
  # Answer questions for specific patient
  python scripts/patient_qa_interactive.py --hadm-id 130656 --question "What are my medications?"
        """
    )
    
    parser.add_argument(
        '--data-path',
        type=str,
        default='data_pipeline/data/processed/processed_discharge_summaries.csv',
        help='Path to processed discharge summaries CSV'
    )
    
    parser.add_argument(
        '--hadm-id',
        type=int,
        default=None,
        help='Hospital admission ID (filters to specific patient record)'
    )
    
    parser.add_argument(
        '--question',
        type=str,
        default=None,
        help='Single question to answer'
    )
    
    parser.add_argument(
        '--questions',
        type=str,
        nargs='+',
        default=None,
        help='Multiple questions to answer'
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
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Save results to JSON file'
    )
    
    args = parser.parse_args()
    
    # Initialize Q&A system
    print("Initializing Patient Q&A System...")
    print(f"Loading data from: {args.data_path}")
    print("This may take a minute on first run (creating embeddings)...")
    
    try:
        qa_system = PatientQA(
            data_path=args.data_path,
            embedding_model=args.embedding_model,
            gemini_model=args.gemini_model
        )
        print("✅ Q&A System ready!\n")
    except Exception as e:
        print(f"\n❌ Failed to initialize Q&A system: {e}")
        print("\nTroubleshooting:")
        print("1. Check that the data file exists")
        print("2. Install required packages: pip install sentence-transformers faiss-cpu")
        print("3. Set GOOGLE_API_KEY environment variable")
        sys.exit(1)
    
    # Handle different modes
    import json
    
    if args.question:
        # Single question mode
        print(f"\n❓ Question: {args.question}\n")
        result = qa_system.ask_question(args.question, hadm_id=args.hadm_id)
        print_answer(result, show_sources=True)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ Results saved to {args.output}\n")
    
    elif args.questions:
        # Batch mode
        batch_mode(qa_system, args.questions, hadm_id=args.hadm_id)
        
        if args.output:
            results = qa_system.ask_multiple_questions(args.questions, hadm_id=args.hadm_id)
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✅ Results saved to {args.output}\n")
    
    else:
        # Interactive mode
        interactive_mode(qa_system, hadm_id=args.hadm_id)


if __name__ == "__main__":
    main()

