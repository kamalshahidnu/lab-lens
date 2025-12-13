#!/usr/bin/env python3
"""
Simple Gemini training script that processes MIMIC-III data
"""

import os
import sys
import json
import csv
from pathlib import Path
from typing import List, Dict
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Gemini model (minimal dependencies)
try:
  import google.generativeai as genai
  from dotenv import load_dotenv
  load_dotenv()
except ImportError as e:
  print(f" Error importing dependencies: {e}")
  sys.exit(1)


class SimpleGeminiTrainer:
  """Simple trainer that processes data and generates summaries"""
 
  def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.3):
    """Initialize Gemini model"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
      raise ValueError("GOOGLE_API_KEY not found in environment variables")
   
    genai.configure(api_key=api_key)
   
    try:
      self.model = genai.GenerativeModel(model_name)
      self.model_name = model_name
      self.temperature = temperature
      print(f" Initialized Gemini model: {model_name}")
    except Exception as e:
      print(f"⚠️ Model {model_name} not available, trying gemini-1.5-pro...")
      try:
        self.model = genai.GenerativeModel("gemini-1.5-pro")
        self.model_name = "gemini-1.5-pro"
        print(f" Using fallback model: gemini-1.5-pro")
      except Exception as e2:
        print(f" Failed to initialize Gemini model: {e2}")
        raise
 
  def summarize(self, text: str, max_length: int = 150) -> str:
    """Generate summary for medical text"""
    system_prompt = """You are a medical expert assistant. Your task is to create concise,
accurate summaries of medical discharge summaries. Focus on:
- Chief complaint and primary diagnosis
- Key treatments and procedures
- Discharge medications
- Important follow-up instructions

Keep the summary clear, professional, and medically accurate."""
   
    prompt = f"""{system_prompt}

Please summarize the following medical discharge summary in approximately {max_length} words:

{text[:5000]}

Summary:"""
   
    try:
      response = self.model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
          temperature=self.temperature,
          max_output_tokens=2048,
        )
      )
      return response.text.strip()
    except Exception as e:
      print(f"⚠️ Error generating summary: {e}")
      return f"[Error: {str(e)[:50]}]"
 
  def process_csv(self, input_path: str, output_path: str, limit: int = None, batch_size: int = 10):
    """Process CSV file and generate summaries"""
    print(f"\n📊 Processing data from: {input_path}")
   
    # Read CSV
    results = []
    processed = 0
   
    try:
      with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
       
        if limit:
          rows = rows[:limit]
       
        total = len(rows)
        print(f" Loaded {total} records")
        print(f"📝 Generating summaries...\n")
       
        for i, row in enumerate(rows, 1):
          text = row.get('cleaned_text', '') or row.get('cleaned_text_final', '')
         
          if not text or len(text) < 100:
            continue
         
          try:
            print(f"[{i}/{total}] Processing record {row.get('hadm_id', i)}...", end=' ', flush=True)
            summary = self.summarize(text, max_length=150)
            print("")
           
            results.append({
              'hadm_id': row.get('hadm_id', ''),
              'subject_id': row.get('subject_id', ''),
              'original_text_length': len(text),
              'summary': summary,
              'summary_length': len(summary)
            })
           
            processed += 1
           
            # Rate limiting
            if i % batch_size == 0:
              time.sleep(1)
             
          except Exception as e:
            print(f"⚠️ Error: {str(e)[:50]}")
            continue
       
    except Exception as e:
      print(f" Error reading CSV: {e}")
      return False
   
    # Save results
    print(f"\n💾 Saving {processed} summaries to: {output_path}")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
   
    try:
      with open(output_path, 'w', encoding='utf-8', newline='') as f:
        if results:
          writer = csv.DictWriter(f, fieldnames=results[0].keys())
          writer.writeheader()
          writer.writerows(results)
     
      print(f" Successfully saved {processed} summaries!")
      print(f"📁 Output: {output_path}")
      return True
     
    except Exception as e:
      print(f" Error saving results: {e}")
      return False


def main():
  """Main function"""
  import argparse
 
  parser = argparse.ArgumentParser(description='Train Gemini model on MIMIC-III data')
  parser.add_argument('--input', type=str,
            default='data_pipeline/data/processed/processed_discharge_summaries.csv',
            help='Input CSV file path')
  parser.add_argument('--output', type=str,
            default='models/gemini/processed_with_summaries.csv',
            help='Output CSV file path')
  parser.add_argument('--limit', type=int, default=None,
            help='Limit number of records to process')
  parser.add_argument('--model', type=str, default='gemini-2.5-flash',
            help='Gemini model name')
 
  args = parser.parse_args()
 
  print("=" * 60)
  print("🚀 Gemini Model Training on MIMIC-III Data")
  print("=" * 60)
 
  try:
    trainer = SimpleGeminiTrainer(model_name=args.model)
    success = trainer.process_csv(args.input, args.output, limit=args.limit)
   
    if success:
      print("\n" + "=" * 60)
      print(" Training Complete!")
      print("=" * 60)
    else:
      print("\n Training failed")
      sys.exit(1)
     
  except Exception as e:
    print(f"\n Error: {e}")
    sys.exit(1)


if __name__ == '__main__':
  main()




