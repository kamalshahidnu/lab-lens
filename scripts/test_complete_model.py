#!/usr/bin/env python3
"""
Complete Model Testing Script with Development & Validation
Tests medical model functionalities with MIMIC data:
1. Discharge Summary Generation/Simplification
2. Risk Prediction from Discharge Summaries
3. Model Development/Training (optional)
4. Model Validation with ROUGE/BLEU metrics (optional)

Features:
- Model Testing: Test on single or multiple records
- Model Development: Train/develop models before testing (--train)
- Model Validation: Validate performance with ROUGE/BLEU metrics (--validate)
- Batch Processing: Test multiple records with aggregate statistics

Testing Modes:
- Single record: Use --index or --hadm-id to test a specific record
- Multiple records: Use --num-records N to test the first N records
- Sample data: Use --use-sample to test with hardcoded sample data

Data Sources:
- MIMIC data from processed CSV files (default)
- Hardcoded sample data (if --use-sample flag is provided)

Examples:
  # Test first 5 records
  python scripts/test_complete_model.py --num-records 5
  
  # Test with validation metrics
  python scripts/test_complete_model.py --num-records 10 --validate
  
  # Train model, then test with validation
  python scripts/test_complete_model.py --train --num-records 20 --validate
  
  # Test specific record by index
  python scripts/test_complete_model.py --index 10
  
  # Test specific record by HADM ID
  python scripts/test_complete_model.py --hadm-id 130656
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.training.gemini_inference import GeminiInference
    from src.training.risk_prediction import MedicalRiskPredictor
    from src.training.model_validation import ModelValidator
    from src.training.train_with_tracking import CompleteModelTrainer
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some imports failed: {e}")
    IMPORTS_AVAILABLE = False
    ModelValidator = None
    CompleteModelTrainer = None

# Sample test data
SAMPLE_DISCHARGE_SUMMARY = """
CHIEF COMPLAINT: 65-year-old male with chest pain and shortness of breath.

HISTORY OF PRESENT ILLNESS:
Patient presented to the emergency department with acute onset chest pain radiating 
to the left arm, associated with diaphoresis and nausea. History significant for 
hypertension, diabetes mellitus type 2, and previous myocardial infarction in 2018.

HOSPITAL COURSE:
Patient was admitted to the cardiac care unit. Initial troponin elevated at 2.5 ng/mL. 
EKG showed ST elevation in leads II, III, and aVF consistent with inferior STEMI. 
Emergency cardiac catheterization revealed 95% occlusion of the right coronary artery. 
Primary PCI performed with successful stent placement. Post-procedurally, patient 
remained stable with resolution of symptoms. Echo showed EF of 45% with inferior 
wall hypokinesis.

DISCHARGE DIAGNOSIS:
1. ST-elevation myocardial infarction (STEMI), inferior wall
2. Hypertension, uncontrolled
3. Type 2 diabetes mellitus
4. Hyperlipidemia

DISCHARGE MEDICATIONS:
- Aspirin 81mg daily
- Clopidogrel 75mg daily
- Atorvastatin 80mg daily
- Metoprolol 50mg twice daily
- Lisinopril 10mg daily
- Metformin 1000mg twice daily

FOLLOW-UP:
Cardiology follow-up in 2 weeks. Continue all medications as prescribed. 
Call 911 if chest pain recurs.
"""


class CompleteModelTester:
    """Test medical model functionalities with optional development and validation"""
    
    def __init__(self, enable_validation: bool = False):
        """
        Initialize models
        
        Args:
            enable_validation: Whether to enable model validation metrics
        """
        print("="*70)
        print("INITIALIZING MODEL TESTING")
        print("="*70)
        
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'discharge_summary_test': {},
            'risk_prediction_test': {},
            'validation_metrics': {},
            'overall_status': 'not_started'
        }
        
        self.enable_validation = enable_validation
        self.validator = None
        
        # Initialize validation if requested
        if enable_validation and ModelValidator:
            try:
                print("\n0. Initializing Model Validator...")
                self.validator = ModelValidator()
                print("   ✓ Model Validator ready (ROUGE/BLEU metrics enabled)")
            except Exception as e:
                print(f"   ⚠ Failed to initialize validator: {e}")
                self.validator = None
        
        # Initialize models
        try:
            print("\n1. Initializing Discharge Summary Model...")
            self.summary_model = GeminiInference(model_name="gemini-2.0-flash-exp")
            print("   ✓ Discharge Summary Model ready")
        except Exception as e:
            print(f"   ✗ Failed to initialize summary model: {e}")
            self.summary_model = None
        
        try:
            print("\n2. Initializing Risk Prediction Model...")
            self.risk_model = MedicalRiskPredictor(use_gemini=True, model_name="gemini-2.0-flash-exp")
            print("   ✓ Risk Prediction Model ready")
        except Exception as e:
            print(f"   ✗ Failed to initialize risk model: {e}")
            self.risk_model = None
        
        print("\n" + "="*70)
        print("INITIALIZATION COMPLETE")
        print("="*70)
    
    def test_discharge_summary(self, text: str = SAMPLE_DISCHARGE_SUMMARY) -> Dict:
        """
        Test 1: Discharge Summary Generation/Simplification
        
        Args:
            text: Sample discharge summary text
            
        Returns:
            Test results dictionary
        """
        print("\n" + "="*70)
        print("TEST 1: DISCHARGE SUMMARY GENERATION/SIMPLIFICATION")
        print("="*70)
        
        result = {
            'status': 'failed',
            'input_length': len(text),
            'summary': None,
            'error': None
        }
        
        if not self.summary_model:
            result['error'] = 'Summary model not initialized'
            print("✗ Test failed: Summary model not available")
            return result
        
        try:
            print(f"\nInput text length: {len(text)} characters")
            print("\nGenerating simplified summary...")
            
            # Generate summary
            summary = self.summary_model.summarize(text, max_length=200)
            
            result['summary'] = summary
            result['summary_length'] = len(summary)
            result['status'] = 'success'
            
            print("\n✓ Summary generated successfully!")
            print(f"\n{'─'*70}")
            print("GENERATED SUMMARY:")
            print(f"{'─'*70}")
            print(summary)
            print(f"{'─'*70}")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"\n✗ Test failed: {e}")
        
        self.test_results['discharge_summary_test'] = result
        return result
    
    def test_risk_prediction(
        self, 
        discharge_text: str = SAMPLE_DISCHARGE_SUMMARY,
        patient_info: Optional[Dict] = None
    ) -> Dict:
        """
        Test 2: Risk Prediction from Discharge Summary
        
        Args:
            discharge_text: Discharge summary text
            patient_info: Optional patient information (age, gender, etc.)
            
        Returns:
            Test results dictionary
        """
        print("\n" + "="*70)
        print("TEST 2: RISK PREDICTION FROM DISCHARGE SUMMARY")
        print("="*70)
        
        result = {
            'status': 'failed',
            'risk_level': None,
            'risk_score': None,
            'risk_factors': None,
            'recommendations': None,
            'error': None
        }
        
        if not self.risk_model:
            result['error'] = 'Risk prediction model not initialized'
            print("✗ Test failed: Risk prediction model not available")
            return result
        
        try:
            # Prepare patient record - merge patient_info with discharge_text
            if patient_info is None:
                patient_info = {
                    'age': 65,
                    'gender': 'M',
                    'cleaned_text': discharge_text,
                    'abnormal_lab_count': 5,
                    'diagnosis_count': 4,
                    'length_of_stay': 3
                }
            else:
                # Ensure cleaned_text is set from discharge_text if not already present
                if 'cleaned_text' not in patient_info or not patient_info.get('cleaned_text'):
                    patient_info['cleaned_text'] = discharge_text
            
            # Ensure we have cleaned_text_final as well (some models might look for this)
            if 'cleaned_text_final' not in patient_info:
                patient_info['cleaned_text_final'] = discharge_text
            
            print(f"\nPatient Info:")
            print(f"  HADM ID: {patient_info.get('hadm_id', 'N/A')}")
            print(f"  Subject ID: {patient_info.get('subject_id', 'N/A')}")
            print(f"  Age: {patient_info.get('age', patient_info.get('age_at_admission', 'N/A'))}")
            print(f"  Gender: {patient_info.get('gender', 'N/A')}")
            print(f"  Discharge summary length: {len(discharge_text)} characters")
            if 'abnormal_lab_count' in patient_info:
                print(f"  Abnormal labs: {patient_info.get('abnormal_lab_count', 0)}")
            if 'diagnosis_count' in patient_info:
                print(f"  Diagnoses: {patient_info.get('diagnosis_count', 0)}")
            
            print("\nPredicting risk level...")
            
            # Predict risk
            risk_prediction = self.risk_model.predict(patient_info)
            
            result['risk_level'] = risk_prediction.get('risk_level')
            result['risk_score'] = risk_prediction.get('risk_score')
            result['risk_factors'] = risk_prediction.get('risk_factors', {})
            result['recommendations'] = risk_prediction.get('recommendations', [])
            result['status'] = 'success'
            
            print("\n✓ Risk prediction completed!")
            print(f"\n{'─'*70}")
            print("RISK PREDICTION RESULTS:")
            print(f"{'─'*70}")
            print(f"Risk Level: {risk_prediction.get('risk_level', 'Unknown').upper()}")
            print(f"Risk Score: {risk_prediction.get('risk_score', 0)}/100")
            
            if risk_prediction.get('risk_factors'):
                print(f"\nRisk Factors:")
                for factor, value in risk_prediction['risk_factors'].items():
                    print(f"  • {factor}: {value}")
            
            if risk_prediction.get('recommendations'):
                print(f"\nRecommendations:")
                for rec in risk_prediction['recommendations']:
                    print(f"  • {rec}")
            
            print(f"{'─'*70}")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"\n✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
        
        self.test_results['risk_prediction_test'] = result
        return result
    
    def validate_model_performance(
        self,
        predictions: list,
        references: list,
        include_rouge: bool = True,
        include_bleu: bool = True
    ) -> Dict:
        """
        Validate model performance using ROUGE and BLEU metrics
        
        Args:
            predictions: List of predicted summaries
            references: List of reference texts (full discharge summaries)
            include_rouge: Whether to calculate ROUGE metrics
            include_bleu: Whether to calculate BLEU metrics
            
        Returns:
            Dictionary with validation metrics
        """
        if not self.validator:
            return {'error': 'Model validator not initialized'}
        
        if len(predictions) != len(references):
            return {'error': f'Mismatch: {len(predictions)} predictions vs {len(references)} references'}
        
        print("\n" + "="*70)
        print("MODEL VALIDATION WITH ROUGE/BLEU METRICS")
        print("="*70)
        
        try:
            metrics = self.validator.validate_model(
                predictions=predictions,
                references=references,
                include_rouge=include_rouge,
                include_bleu=include_bleu
            )
            
            print(f"\n{'─'*70}")
            print("VALIDATION METRICS:")
            print(f"{'─'*70}")
            
            if include_rouge:
                print(f"\nROUGE Scores:")
                print(f"  ROUGE-1 F1: {metrics.get('rouge1_f', 0):.4f}")
                print(f"  ROUGE-2 F1: {metrics.get('rouge2_f', 0):.4f}")
                print(f"  ROUGE-L F1: {metrics.get('rougeL_f', 0):.4f}")
                print(f"  ROUGE-Lsum F1: {metrics.get('rougeLsum_f', 0):.4f}")
            
            if include_bleu:
                print(f"\nBLEU Scores:")
                print(f"  BLEU: {metrics.get('bleu', 0):.4f}")
                if 'sacrebleu' in metrics:
                    print(f"  SacreBLEU: {metrics.get('sacrebleu', 0):.4f}")
            
            if 'overall_score' in metrics:
                print(f"\nOverall Score: {metrics['overall_score']:.4f}")
            
            print(f"{'─'*70}")
            
            self.test_results['validation_metrics'] = metrics
            return metrics
            
        except Exception as e:
            error_msg = f"Validation failed: {e}"
            print(f"\n✗ {error_msg}")
            import traceback
            traceback.print_exc()
            return {'error': error_msg}
    
    def run_all_tests(
        self, 
        discharge_text: str = SAMPLE_DISCHARGE_SUMMARY,
        patient_info: Optional[Dict] = None
    ) -> Dict:
        """
        Run all tests
        
        Args:
            discharge_text: Sample discharge summary
            patient_info: Optional patient information
            
        Returns:
            Complete test results
        """
        print("\n" + "="*70)
        print("RUNNING MODEL TESTS")
        print("="*70)
        
        # Test 1: Discharge Summary
        summary_result = self.test_discharge_summary(discharge_text)
        
        # Test 2: Risk Prediction
        risk_result = self.test_risk_prediction(discharge_text, patient_info)
        
        # Overall status
        all_successful = (
            summary_result['status'] == 'success' and
            risk_result['status'] == 'success'
        )
        
        self.test_results['overall_status'] = 'success' if all_successful else 'partial'
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"\n1. Discharge Summary: {'✓ PASS' if summary_result['status'] == 'success' else '✗ FAIL'}")
        print(f"2. Risk Prediction: {'✓ PASS' if risk_result['status'] == 'success' else '✗ FAIL'}")
        print(f"\nOverall Status: {self.test_results['overall_status'].upper()}")
        print("="*70)
        
        # Save results
        self.save_results()
        
        return self.test_results
    
    def run_batch_tests(self, records: list) -> Dict:
        """
        Run tests on multiple records
        
        Args:
            records: List of dictionaries with 'discharge_text' and 'patient_info'
            
        Returns:
            Complete test results for all records
        """
        print("\n" + "="*70)
        print(f"RUNNING BATCH MODEL TESTS ON {len(records)} RECORDS")
        print("="*70)
        
        batch_results = {
            'timestamp': datetime.now().isoformat(),
            'num_records': len(records),
            'record_results': [],
            'summary': {
                'total_tested': 0,
                'successful': 0,
                'failed': 0,
                'discharge_summary_success': 0,
                'risk_prediction_success': 0
            }
        }
        
        for i, record_data in enumerate(records, 1):
            discharge_text = record_data['discharge_text']
            patient_info = record_data['patient_info']
            
            print(f"\n{'='*70}")
            print(f"RECORD {i}/{len(records)}")
            print(f"{'='*70}")
            print(f"HADM ID: {patient_info.get('hadm_id', 'N/A')}")
            print(f"Subject ID: {patient_info.get('subject_id', 'N/A')}")
            print(f"Age: {patient_info.get('age', 'N/A')}")
            print(f"Gender: {patient_info.get('gender', 'N/A')}")
            print(f"Text length: {patient_info.get('text_length', len(discharge_text))} characters")
            
            # Test 1: Discharge Summary
            summary_result = self.test_discharge_summary(discharge_text)
            
            # Test 2: Risk Prediction
            risk_result = self.test_risk_prediction(discharge_text, patient_info)
            
            # Record results
            record_result = {
                'record_index': patient_info.get('record_index', i - 1),
                'hadm_id': patient_info.get('hadm_id'),
                'subject_id': patient_info.get('subject_id'),
                'discharge_summary_test': summary_result,
                'risk_prediction_test': risk_result,
                'overall_status': 'success' if (
                    summary_result['status'] == 'success' and
                    risk_result['status'] == 'success'
                ) else 'partial'
            }
            
            batch_results['record_results'].append(record_result)
            batch_results['summary']['total_tested'] += 1
            
            if summary_result['status'] == 'success':
                batch_results['summary']['discharge_summary_success'] += 1
            if risk_result['status'] == 'success':
                batch_results['summary']['risk_prediction_success'] += 1
            
            if record_result['overall_status'] == 'success':
                batch_results['summary']['successful'] += 1
            else:
                batch_results['summary']['failed'] += 1
        
        # Run validation if enabled
        if self.enable_validation and self.validator:
            print("\n" + "="*70)
            print("RUNNING MODEL VALIDATION ON BATCH RESULTS")
            print("="*70)
            
            # Collect predictions and references for validation
            predictions = []
            references = []
            
            for record_result in batch_results['record_results']:
                summary_result = record_result.get('discharge_summary_test', {})
                if summary_result.get('status') == 'success' and summary_result.get('summary'):
                    predictions.append(summary_result['summary'])
                    # Use original discharge text as reference
                    # Find the matching record
                    hadm_id = record_result.get('hadm_id')
                    for record_data in records:
                        if record_data['patient_info'].get('hadm_id') == hadm_id:
                            references.append(record_data['discharge_text'])
                            break
            
            if len(predictions) > 0 and len(predictions) == len(references):
                validation_metrics = self.validate_model_performance(
                    predictions=predictions,
                    references=references
                )
                batch_results['validation_metrics'] = validation_metrics
        
        # Print batch summary
        print("\n" + "="*70)
        print("BATCH TEST SUMMARY")
        print("="*70)
        print(f"\nTotal Records Tested: {batch_results['summary']['total_tested']}")
        print(f"Successful: {batch_results['summary']['successful']}")
        print(f"Failed/Partial: {batch_results['summary']['failed']}")
        print(f"\nDischarge Summary Tests:")
        print(f"  Passed: {batch_results['summary']['discharge_summary_success']}/{batch_results['summary']['total_tested']}")
        print(f"  Pass Rate: {100 * batch_results['summary']['discharge_summary_success'] / batch_results['summary']['total_tested']:.1f}%")
        print(f"\nRisk Prediction Tests:")
        print(f"  Passed: {batch_results['summary']['risk_prediction_success']}/{batch_results['summary']['total_tested']}")
        print(f"  Pass Rate: {100 * batch_results['summary']['risk_prediction_success'] / batch_results['summary']['total_tested']:.1f}%")
        
        if 'validation_metrics' in batch_results and 'error' not in batch_results['validation_metrics']:
            print(f"\nModel Validation Metrics:")
            metrics = batch_results['validation_metrics']
            if 'rougeL_f' in metrics:
                print(f"  ROUGE-L F1: {metrics['rougeL_f']:.4f}")
            if 'bleu' in metrics:
                print(f"  BLEU: {metrics['bleu']:.4f}")
            if 'overall_score' in metrics:
                print(f"  Overall Score: {metrics['overall_score']:.4f}")
        
        print("="*70)
        
        self.test_results = batch_results
        return batch_results
    
    def save_results(self, output_path: str = "test_results.json"):
        """
        Save test results to JSON file
        
        Args:
            output_path: Path to output JSON file
        """
        try:
            output_file = project_root / output_path
            with open(output_file, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            print(f"\n✓ Test results saved to: {output_file}")
        except Exception as e:
            print(f"\n⚠ Could not save results: {e}")


def load_mimic_data(
    data_path: str = "data-pipeline/data/processed/processed_discharge_summaries.csv",
    index: Optional[int] = None,
    hadm_id: Optional[int] = None,
    num_records: Optional[int] = None
) -> Optional[Dict]:
    """
    Load record(s) from MIMIC processed data
    
    Args:
        data_path: Path to processed MIMIC CSV file
        index: Row index to select (0-based) - single record
        hadm_id: Hospital admission ID to select - single record
        num_records: Number of records to load from the start (first n records)
        
    Returns:
        Dictionary with patient record data:
        - For single record: {'discharge_text': str, 'patient_info': dict}
        - For multiple records: {'records': [{'discharge_text': str, 'patient_info': dict}, ...]}
        Returns None if not found
    """
    file_path = project_root / data_path
    
    if not file_path.exists():
        print(f"⚠ Warning: MIMIC data file not found at {file_path}")
        print(f"   Using hardcoded sample data instead")
        return None
    
    try:
        print(f"\nLoading MIMIC data from: {file_path}")
        df = pd.read_csv(file_path)
        print(f"   Loaded {len(df)} records")
        
        # Handle multiple records (first n)
        if num_records is not None and num_records > 0:
            num_to_load = min(num_records, len(df))
            print(f"\n   Selecting first {num_to_load} records")
            records_df = df.head(num_to_load)
            
            records = []
            for idx, record in records_df.iterrows():
                # Extract discharge summary text
                discharge_text = str(record.get('cleaned_text_final', record.get('cleaned_text', '')))
                
                # Build patient info dictionary
                patient_info = {
                    'hadm_id': int(record.get('hadm_id', 0)),
                    'subject_id': int(record.get('subject_id', 0)),
                    'age': int(float(record.get('age_at_admission', 0))),
                    'gender': str(record.get('gender', 'U')).upper(),
                    'cleaned_text': discharge_text,
                    'abnormal_lab_count': int(record.get('abnormal_count', 0)),
                    'diagnosis_count': int(record.get('diagnosis_count', 0)),
                    'text_length': len(discharge_text),
                    'record_index': int(idx),
                }
                
                # Add optional fields if available
                for field in ['ethnicity', 'insurance', 'admission_type', 'length_of_stay', 
                             'complexity_score', 'urgency_indicator']:
                    if field in record and pd.notna(record[field]):
                        patient_info[field] = record[field]
                
                records.append({
                    'discharge_text': discharge_text,
                    'patient_info': patient_info
                })
                
                print(f"   Record {len(records)}: HADM ID {patient_info['hadm_id']}, "
                      f"Age {patient_info['age']}, Gender {patient_info['gender']}, "
                      f"Text length: {patient_info['text_length']} chars")
            
            print(f"\n✓ Loaded {len(records)} records")
            return {'records': records}
        
        # Handle single record selection
        if hadm_id is not None:
            matching_records = df[df['hadm_id'] == hadm_id]
            if len(matching_records) > 0:
                record = matching_records.iloc[0]
            else:
                print(f"⚠ Warning: hadm_id {hadm_id} not found. Using first record.")
                record = df.iloc[0]
        elif index is not None:
            if 0 <= index < len(df):
                record = df.iloc[index]
            else:
                print(f"⚠ Warning: Index {index} out of range. Using first record.")
                record = df.iloc[0]
        else:
            # Use first record by default
            record = df.iloc[0]
        
        # Extract discharge summary text (prefer cleaned_text_final, fallback to cleaned_text)
        discharge_text = str(record.get('cleaned_text_final', record.get('cleaned_text', '')))
        
        # Build patient info dictionary
        patient_info = {
            'hadm_id': int(record.get('hadm_id', 0)),
            'subject_id': int(record.get('subject_id', 0)),
            'age': int(float(record.get('age_at_admission', 0))),
            'gender': str(record.get('gender', 'U')).upper(),
            'cleaned_text': discharge_text,
            'abnormal_lab_count': int(record.get('abnormal_count', 0)),
            'diagnosis_count': int(record.get('diagnosis_count', 0)),
            'text_length': len(discharge_text),
        }
        
        # Add optional fields if available
        for field in ['ethnicity', 'insurance', 'admission_type', 'length_of_stay', 
                     'complexity_score', 'urgency_indicator']:
            if field in record and pd.notna(record[field]):
                patient_info[field] = record[field]
        
        print(f"\n✓ Selected MIMIC record:")
        print(f"   HADM ID: {patient_info['hadm_id']}")
        print(f"   Subject ID: {patient_info['subject_id']}")
        print(f"   Age: {patient_info['age']}")
        print(f"   Gender: {patient_info['gender']}")
        print(f"   Discharge summary length: {patient_info['text_length']} characters")
        
        return {
            'discharge_text': discharge_text,
            'patient_info': patient_info
        }
        
    except Exception as e:
        print(f"⚠ Error loading MIMIC data: {e}")
        print(f"   Using hardcoded sample data instead")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test medical model functionalities with MIMIC data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with first MIMIC record (default)
  python scripts/test_complete_model.py
  
  # Test first n records (e.g., first 5 records)
  python scripts/test_complete_model.py --num-records 5
  
  # Test with validation metrics (ROUGE/BLEU)
  python scripts/test_complete_model.py --num-records 10 --validate
  
  # Test with specific record by index
  python scripts/test_complete_model.py --index 5
  
  # Test with specific record by hadm_id
  python scripts/test_complete_model.py --hadm-id 130656
  
  # Test with hardcoded sample data (ignore MIMIC)
  python scripts/test_complete_model.py --use-sample
  
  # Train model before testing (development mode)
  python scripts/test_complete_model.py --train --num-records 20 --validate
  
  # Override patient info from MIMIC data
  python scripts/test_complete_model.py --index 0 --age 70 --gender F
        """
    )
    
    parser.add_argument(
        '--data-path',
        type=str,
        default='data-pipeline/data/processed/processed_discharge_summaries.csv',
        help='Path to processed MIMIC CSV file'
    )
    
    parser.add_argument(
        '--num-records',
        type=int,
        default=None,
        help='Number of records to test (first n records). Use this to test multiple records.'
    )
    
    parser.add_argument(
        '--index',
        type=int,
        default=None,
        help='Row index (0-based) to select from MIMIC data (single record)'
    )
    
    parser.add_argument(
        '--hadm-id',
        type=int,
        default=None,
        help='Hospital admission ID (hadm_id) to select from MIMIC data (single record)'
    )
    
    parser.add_argument(
        '--use-sample',
        action='store_true',
        help='Use hardcoded sample data instead of MIMIC data'
    )
    
    parser.add_argument(
        '--age',
        type=int,
        default=None,
        help='Override patient age for risk prediction'
    )
    
    parser.add_argument(
        '--gender',
        type=str,
        default=None,
        help='Override patient gender (M/F) for risk prediction'
    )
    
    parser.add_argument(
        '--symptoms',
        type=str,
        default=None,
        help='Patient symptoms (not used if loading from MIMIC)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='test_results.json',
        help='Output file for test results'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Enable model validation with ROUGE/BLEU metrics'
    )
    
    parser.add_argument(
        '--train',
        action='store_true',
        help='Train/develop model before testing (requires data path)'
    )
    
    parser.add_argument(
        '--train-config',
        type=str,
        default=None,
        help='Path to training configuration file (for --train mode)'
    )
    
    parser.add_argument(
        '--model-dir',
        type=str,
        default='models/gemini',
        help='Directory to save trained models (for --train mode)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.num_records and (args.index is not None or args.hadm_id is not None):
        print("⚠ Warning: --num-records is mutually exclusive with --index and --hadm-id")
        print("   Using --num-records and ignoring --index/--hadm-id")
        args.index = None
        args.hadm_id = None
    
    # Load data
    discharge_text = SAMPLE_DISCHARGE_SUMMARY
    patient_info = None
    batch_records = None
    
    if not args.use_sample:
        # Try to load from MIMIC data
        mimic_data = load_mimic_data(
            data_path=args.data_path,
            index=args.index,
            hadm_id=args.hadm_id,
            num_records=args.num_records
        )
        
        if mimic_data:
            # Check if multiple records were loaded
            if 'records' in mimic_data:
                batch_records = mimic_data['records']
                print(f"\n✓ Loaded {len(batch_records)} MIMIC data records for batch testing")
            else:
                # Single record
                discharge_text = mimic_data['discharge_text']
                patient_info = mimic_data['patient_info']
                print(f"\n✓ Using MIMIC data record")
        else:
            print(f"\n⚠ Falling back to hardcoded sample data")
    
    # Override patient info if provided via command line (only for single record mode)
    if batch_records is None and (args.age or args.gender or args.symptoms):
        if patient_info is None:
            patient_info = {}
        
        if args.age:
            patient_info['age'] = args.age
            print(f"\n⚠ Overriding age to: {args.age}")
        if args.gender:
            patient_info['gender'] = args.gender.upper()
            print(f"⚠ Overriding gender to: {args.gender.upper()}")
        if args.symptoms:
            patient_info['symptoms'] = args.symptoms
    
    # Train model if requested
    if args.train:
        if args.use_sample:
            print("\n⚠ Warning: Cannot train with --use-sample. Training requires data file.")
            print("   Skipping training step.")
        elif CompleteModelTrainer is None:
            print("\n⚠ Warning: CompleteModelTrainer not available. Skipping training step.")
        else:
            print("\n" + "="*70)
            print("MODEL DEVELOPMENT/TRAINING")
            print("="*70)
            try:
                trainer = CompleteModelTrainer(
                    config_path=args.train_config,
                    output_dir=args.model_dir,
                    enable_hyperparameter_tuning=False,  # Can be enabled via config
                    enable_bias_detection=True,
                    enable_sensitivity_analysis=False
                )
                
                print(f"\nTraining model with data from: {args.data_path}")
                print(f"Model output directory: {args.model_dir}")
                
                # Load data and train
                train_df, val_df, test_df = trainer.load_data_from_pipeline(
                    data_path=args.data_path,
                    train_split=0.8,
                    val_split=0.1
                )
                
                print(f"\nData splits:")
                print(f"  Training: {len(train_df)} records")
                print(f"  Validation: {len(val_df)} records")
                print(f"  Test: {len(test_df)} records")
                
                # Train model (this will generate summaries and validate)
                results = trainer.train_and_evaluate(
                    data_path=args.data_path,
                    train_split=0.8,
                    val_split=0.1,
                    run_name=f"training-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                )
                
                print("\n✓ Model training/development completed!")
                print(f"   Results saved to: {args.model_dir}")
                
            except Exception as e:
                print(f"\n✗ Model training failed: {e}")
                print("   Continuing with testing using existing model...")
                import traceback
                traceback.print_exc()
    
    # Run tests
    try:
        tester = CompleteModelTester(enable_validation=args.validate)
        
        # Check if we're running batch tests or single test
        if batch_records is not None:
            # Batch testing mode
            results = tester.run_batch_tests(batch_records)
            
            # Save results with custom output path
            tester.save_results(output_path=args.output)
            
            # Exit with appropriate code based on success rate
            success_rate = results['summary']['successful'] / results['summary']['total_tested'] if results['summary']['total_tested'] > 0 else 0
            if success_rate >= 0.8:  # 80% success rate
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            # Single record testing mode
            results = tester.run_all_tests(
                discharge_text=discharge_text,
                patient_info=patient_info
            )
            
            # Run validation if enabled (for single record)
            if args.validate and tester.validator:
                print("\n" + "="*70)
                print("RUNNING MODEL VALIDATION")
                print("="*70)
                
                summary_result = results.get('discharge_summary_test', {})
                if summary_result.get('status') == 'success' and summary_result.get('summary'):
                    validation_metrics = tester.validate_model_performance(
                        predictions=[summary_result['summary']],
                        references=[discharge_text]
                    )
                    results['validation_metrics'] = validation_metrics
            
            # Save results with custom output path
            if args.output != 'test_results.json':
                tester.save_results(output_path=args.output)
            
            # Exit with appropriate code
            if results['overall_status'] == 'success':
                sys.exit(0)
            else:
                sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

