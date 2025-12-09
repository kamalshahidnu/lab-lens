#!/usr/bin/env python3
"""
Integrated Training Script: Summarization + Risk Prediction
Processes discharge summaries and predicts risk levels
"""

import os
import sys
import csv
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.training.risk_prediction import MedicalRiskPredictor

# Import simple trainer
try:
    from scripts.train_gemini_simple import SimpleGeminiTrainer
except ImportError:
    print("Error: Could not import SimpleGeminiTrainer")
    sys.exit(1)


def process_with_risk_prediction(input_path: str, output_path: str, limit: int = None, use_gemini_risk: bool = False):
    """
    Process data with both summarization and risk prediction
    
    Args:
        input_path: Input CSV file
        output_path: Output CSV file
        limit: Limit number of records
        use_gemini_risk: Use Gemini for risk prediction (slower but more accurate)
    """
    print("=" * 80)
    print("🚀 Integrated Processing: Summarization + Risk Prediction")
    print("=" * 80)
    
    # Initialize components
    print("\n📋 Initializing components...")
    summarizer = SimpleGeminiTrainer(model_name='gemini-2.5-flash')
    risk_predictor = MedicalRiskPredictor(use_gemini=use_gemini_risk)
    print("✓ Components initialized")
    
    # Load data
    print(f"\n📥 Loading data from: {input_path}")
    records = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            records.append(row)
    
    print(f"✓ Loaded {len(records)} records")
    
    # Process records
    results = []
    print(f"\n🔄 Processing {len(records)} records...")
    print("   (This will take a while - generating summaries and predicting risk)\n")
    
    for i, record in enumerate(records, 1):
        try:
            print(f"[{i}/{len(records)}] Processing record {record.get('hadm_id', i)}...", end=' ', flush=True)
            
            # Generate summary
            text = record.get('cleaned_text', '') or record.get('cleaned_text_final', '')
            if not text or len(text) < 100:
                print("⚠️  (skipped - insufficient text)")
                continue
            
            summary = summarizer.summarize(text, max_length=150)
            
            # Predict risk
            risk_result = risk_predictor.predict(record)
            
            # Combine results
            result = {
                'hadm_id': record.get('hadm_id', ''),
                'subject_id': record.get('subject_id', ''),
                'original_text_length': len(text),
                'summary': summary,
                'summary_length': len(summary),
                'risk_level': risk_result['risk_level'],
                'risk_score': risk_result['risk_score'],
                'age': risk_result['risk_factors'].get('age', 0),
                'abnormal_labs': risk_result['risk_factors'].get('abnormal_labs', 0),
                'diagnosis_count': risk_result['risk_factors'].get('diagnosis_count', 0),
                'high_risk_keywords': risk_result['risk_factors'].get('high_risk_keywords', 0),
                'complexity_score': risk_result['risk_factors'].get('complexity_score', 0)
            }
            
            results.append(result)
            print(f"✓ (Risk: {risk_result['risk_level']}, Score: {risk_result['risk_score']:.2f})")
            
            # Rate limiting
            if i % 10 == 0:
                import time
                time.sleep(1)
                
        except Exception as e:
            print(f"⚠️  Error: {str(e)[:50]}")
            continue
    
    # Save results
    print(f"\n💾 Saving {len(results)} results to: {output_path}")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if results:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = results[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        # Print summary
        print(f"\n✅ Successfully saved {len(results)} records!")
        print(f"📁 Output: {output_path}")
        
        # Risk distribution
        risk_counts = {}
        for r in results:
            level = r['risk_level']
            risk_counts[level] = risk_counts.get(level, 0) + 1
        
        print(f"\n📊 Risk Distribution:")
        for level in ['LOW', 'MEDIUM', 'HIGH']:
            count = risk_counts.get(level, 0)
            pct = (count / len(results)) * 100 if results else 0
            print(f"   {level}: {count} ({pct:.1f}%)")
        
        avg_risk_score = sum(r['risk_score'] for r in results) / len(results)
        print(f"\n📈 Average Risk Score: {avg_risk_score:.3f}")
        
        print("\n" + "=" * 80)
        print("✅ Processing Complete!")
        print("=" * 80)
    else:
        print("❌ No results to save")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Process data with summarization and risk prediction')
    parser.add_argument('--input', type=str,
                       default='data-pipeline/data/processed/processed_discharge_summaries.csv',
                       help='Input CSV file')
    parser.add_argument('--output', type=str,
                       default='models/gemini/summaries_with_risk.csv',
                       help='Output CSV file')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of records')
    parser.add_argument('--use-gemini-risk', action='store_true',
                       help='Use Gemini for risk prediction (slower but more accurate)')
    
    args = parser.parse_args()
    
    process_with_risk_prediction(
        args.input,
        args.output,
        limit=args.limit,
        use_gemini_risk=args.use_gemini_risk
    )


if __name__ == '__main__':
    main()




