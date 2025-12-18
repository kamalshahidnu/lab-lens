#!/usr/bin/env python3
"""
Standalone Model Testing Script
Tests all three model functionalities with direct imports
1. Discharge Summary Generation/Simplification
2. Risk Prediction from Discharge Summaries
3. Disease Detection from Biomedical Images
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Sample test data
SAMPLE_DISCHARGE_SUMMARY = """CHIEF COMPLAINT: 65-year-old male with chest pain and shortness of breath.

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
Call 911 if chest pain recurs."""


def test_discharge_summary(text: str = SAMPLE_DISCHARGE_SUMMARY) -> Dict:
    """Test 1: Discharge Summary Generation/Simplification"""
    print("\n" + "=" * 70)
    print("TEST 1: DISCHARGE SUMMARY GENERATION/SIMPLIFICATION")
    print("=" * 70)

    result = {"status": "failed", "error": None}

    try:
        # Direct import avoiding __init__.py
        from src.training.gemini_model import GeminiSummarizer

        print("\nInitializing Discharge Summary Model...")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")

        # Try different model names - use the one that works
        model_names = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        model = None
        last_error = None

        for model_name in model_names:
            try:
                print(f" Trying model: {model_name}...")
                model = GeminiSummarizer(api_key=api_key, model_name=model_name)
                # Test if it actually works by checking the model was created
                if hasattr(model, "model") and model.model is not None:
                    print(f"  Successfully initialized: {model_name}")
                    break
            except Exception as e:
                last_error = e
                print(f"  Failed: {model_name} - {str(e)[:100]}")
                continue

        if model is None:
            raise Exception(f"Failed to initialize any model. Last error: {last_error}")

        print(f"Input text length: {len(text)} characters")
        print("\nGenerating simplified summary...")

        summary = model.summarize(text, max_length=200)

        result["status"] = "success"
        result["summary"] = summary
        result["summary_length"] = len(summary)

        print("\n Summary generated successfully!")
        print(f"\n{'─'*70}")
        print("GENERATED SUMMARY:")
        print(f"{'─'*70}")
        print(summary)
        print(f"{'─'*70}")

    except Exception as e:
        result["error"] = str(e)
        print(f"\n Test failed: {e}")
        import traceback

        traceback.print_exc()

    return result


def test_risk_prediction(discharge_text: str = SAMPLE_DISCHARGE_SUMMARY, patient_info: Optional[Dict] = None) -> Dict:
    """Test 2: Risk Prediction from Discharge Summary"""
    print("\n" + "=" * 70)
    print("TEST 2: RISK PREDICTION FROM DISCHARGE SUMMARY")
    print("=" * 70)

    result = {"status": "failed", "error": None}

    try:
        # Direct import
        from src.training.risk_prediction import MedicalRiskPredictor

        print("\nInitializing Risk Prediction Model...")
        # Try different model names
        model_names = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        model = None
        last_error = None

        for model_name in model_names:
            try:
                print(f" Trying model: {model_name}...")
                model = MedicalRiskPredictor(use_gemini=True, model_name=model_name)
                if model.model is not None:  # Check if Gemini was successfully initialized
                    print(f"  Successfully initialized: {model_name}")
                    break
            except Exception as e:
                last_error = e
                print(f"  Failed: {model_name} - {str(e)[:100]}")
                continue

        if model is None or model.model is None:
            print(" ⚠ Falling back to rule-based risk prediction (no Gemini)")
            model = MedicalRiskPredictor(use_gemini=False)

        if patient_info is None:
            patient_info = {
                "age": 65,
                "gender": "M",
                "cleaned_text": discharge_text,
                "abnormal_lab_count": 5,
                "diagnosis_count": 4,
                "length_of_stay": 3,
            }

        print(f"\nPatient Info:")
        print(f" Age: {patient_info.get('age', 'N/A')}")
        print(f" Gender: {patient_info.get('gender', 'N/A')}")
        print(f" Discharge summary length: {len(discharge_text)} characters")

        print("\nPredicting risk level...")

        # Use predict() method (not predict_risk)
        risk_prediction = model.predict(patient_info)

        result["status"] = "success"
        result["risk_level"] = risk_prediction.get("risk_level")
        result["risk_score"] = risk_prediction.get("risk_score", 0) * 100  # Convert 0-1 to 0-100
        result["risk_factors"] = risk_prediction.get("risk_factors", {})
        prediction_details = risk_prediction.get("prediction_details", {})
        result["recommendations"] = (
            [prediction_details.get("recommendation", "")] if prediction_details.get("recommendation") else []
        )
        result["key_factors"] = prediction_details.get("key_factors", [])

        print("\n Risk prediction completed!")
        print(f"\n{'─'*70}")
        print("RISK PREDICTION RESULTS:")
        print(f"{'─'*70}")
        print(f"Risk Level: {risk_prediction.get('risk_level', 'Unknown').upper()}")
        risk_score = risk_prediction.get("risk_score", 0)
        if isinstance(risk_score, float) and risk_score <= 1.0:
            risk_score = risk_score * 100  # Convert to percentage
        print(f"Risk Score: {risk_score:.1f}/100")

        prediction_details = risk_prediction.get("prediction_details", {})
        if prediction_details.get("key_factors"):
            print(f"\nKey Risk Factors:")
            for factor in prediction_details["key_factors"]:
                print(f" • {factor}")

        if prediction_details.get("recommendation"):
            print(f"\nRecommendation:")
            print(f" • {prediction_details['recommendation']}")

        print(f"{'─'*70}")

    except Exception as e:
        result["error"] = str(e)
        print(f"\n Test failed: {e}")
        import traceback

        traceback.print_exc()

    return result


def test_image_disease_detection(image_path: Optional[str] = None, patient_info: Optional[Dict] = None) -> Dict:
    """Test 3: Disease Detection from Biomedical Images"""
    print("\n" + "=" * 70)
    print("TEST 3: DISEASE DETECTION FROM BIOMEDICAL IMAGES")
    print("=" * 70)

    result = {"status": "failed", "error": None}

    if not image_path:
        result["error"] = "No image path provided"
        print("⚠ Image path not provided")
        print("\nTo test image disease detection:")
        print(" python scripts/test_all_models.py --image-path /path/to/chest_xray.jpg")
        return result

    image_path = Path(image_path)

    if not image_path.exists():
        result["error"] = f"Image file not found: {image_path}"
        print(f" Image file not found: {image_path}")
        return result

    try:
        # Direct import
        from src.training.medical_image_analysis import MedicalImageAnalyzer

        print("\nInitializing Image Disease Detection Model...")
        print(" (Auto-detecting best available image-capable model...)")

        try:
            # Let MedicalImageAnalyzer auto-detect the best available model
            model = MedicalImageAnalyzer(model_name=None)  # None = auto-detect
            print(f"  Successfully initialized: {model.model_name}")
        except Exception as e:
            error_msg = f"Failed to initialize image model: {str(e)}"
            print(f"  {error_msg}")
            raise Exception(error_msg)

        print(f"\nAnalyzing image: {image_path}")
        print(f"Image type: Chest X-ray")

        if patient_info:
            print(f"\nPatient Info:")
            if patient_info.get("age"):
                print(f" Age: {patient_info['age']}")
            if patient_info.get("gender"):
                print(f" Gender: {patient_info['gender']}")
            if patient_info.get("symptoms"):
                print(f" Symptoms: {patient_info['symptoms']}")

        print("\nAnalyzing image for disease detection...")

        analysis_result = model.analyze_chest_xray(image_path, patient_info=patient_info)

        result["status"] = "success"
        result["diseases_detected"] = analysis_result.get("diagnosis", [])
        result["severity"] = analysis_result.get("severity", "unknown")
        result["findings"] = analysis_result.get("findings", [])
        result["impression"] = analysis_result.get("impression", "")
        result["has_disease"] = result["severity"] != "normal" and len(result["diseases_detected"]) > 0

        print("\n Image analysis completed!")
        print(f"\n{'─'*70}")
        print("DISEASE DETECTION RESULTS:")
        print(f"{'─'*70}")

        if result["has_disease"]:
            print(f"⚠ DISEASE DETECTED")
            print(f"\n🔴 Severity Level: {result['severity'].upper()}")
            print(f"\nDiseases Found:")
            for disease in result["diseases_detected"]:
                print(f" • {disease}")
        else:
            print(f" NO DISEASE DETECTED (Normal chest X-ray)")
            print(f"\nSeverity: {result['severity'].upper()}")

        if result["findings"]:
            print(f"\n📊 Detailed Findings:")
            for finding in result["findings"]:
                print(f" • {finding}")

        if result["impression"]:
            print(f"\n💡 Clinical Impression & Summary:")
            print(f" {result['impression']}")

        # Brief Disease Summary
        print(f"\n📝 Brief Disease Summary:")
        if result["has_disease"]:
            print(f" • Status: Disease/Abnormality detected")
            print(f" • Severity: {result['severity'].upper()}")
            if result["diseases_detected"]:
                diseases_str = (
                    ", ".join(str(d) for d in result["diseases_detected"])
                    if isinstance(result["diseases_detected"], list)
                    else str(result["diseases_detected"])
                )
                print(f" • Conditions: {diseases_str}")
            if result["severity"] == "severe":
                print(f" • Action Required: IMMEDIATE medical attention recommended")
            elif result["severity"] == "moderate":
                print(f" • Action Required: Prompt follow-up with healthcare provider recommended")
            elif result["severity"] == "mild":
                print(f" • Action Required: Clinical correlation and monitoring recommended")
        else:
            print(f" • Status: Normal (no significant abnormalities)")
            print(f" • Recommendation: No immediate action required, routine follow-up as needed")

        print(f"{'─'*70}")

    except Exception as e:
        result["error"] = str(e)
        print(f"\n Test failed: {e}")
        import traceback

        traceback.print_exc()

    return result


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test all three model functionalities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
 # Test discharge summary and risk prediction (no image)
 python scripts/test_all_models.py

 # Test with image
 python scripts/test_all_models.py --image-path path/to/chest_xray.jpg

 # Test with custom patient info
 python scripts/test_all_models.py --image-path xray.jpg --age 65 --gender M
    """,
    )

    parser.add_argument("--image-path", type=str, default=None, help="Path to medical image (chest X-ray, etc.)")
    parser.add_argument("--age", type=int, default=None, help="Patient age")
    parser.add_argument("--gender", type=str, default=None, help="Patient gender (M/F)")
    parser.add_argument("--symptoms", type=str, default=None, help="Patient symptoms")
    parser.add_argument("--output", type=str, default="test_results.json", help="Output file for test results")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode: prompts for image path if not provided")

    args = parser.parse_args()

    # Interactive mode: prompt for image if not provided
    if args.interactive and not args.image_path:
        print("\n" + "=" * 70)
        print("INTERACTIVE MODE")
        print("=" * 70)
        print("\nNo image path provided. Please enter the path to your medical image:")
        print(" Supported formats: .jpg, .jpeg, .png, .bmp, .tiff, .tif, .dcm")
        image_input = input("\nImage path (or press Enter to skip): ").strip()
        if image_input:
            args.image_path = image_input.strip("\"'")

    # Prepare patient info
    patient_info = None
    if args.age or args.gender or args.symptoms:
        patient_info = {}
        if args.age:
            patient_info["age"] = args.age
        if args.gender:
            patient_info["gender"] = args.gender
        if args.symptoms:
            patient_info["symptoms"] = args.symptoms
    elif args.interactive and args.image_path:
        # Prompt for patient info in interactive mode
        print("\n" + "─" * 70)
        print("OPTIONAL: Provide patient information for better analysis")
        print(" (Press Enter to skip)")
        print("─" * 70)
        patient_info = {}
        age_input = input("\nPatient age: ").strip()
        if age_input:
            try:
                patient_info["age"] = int(age_input)
            except ValueError:
                pass
        gender_input = input("Patient gender (M/F): ").strip().upper()
        if gender_input in ["M", "F"]:
            patient_info["gender"] = gender_input
        symptoms_input = input("Patient symptoms (optional): ").strip()
        if symptoms_input:
            patient_info["symptoms"] = symptoms_input
        if not patient_info:
            patient_info = None

    # Run tests
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "discharge_summary_test": {},
        "risk_prediction_test": {},
        "image_disease_detection_test": {},
        "overall_status": "not_started",
    }

    print("\n" + "=" * 70)
    print("RUNNING COMPLETE MODEL TESTS")
    print("=" * 70)

    # Test 1: Discharge Summary
    summary_result = test_discharge_summary(SAMPLE_DISCHARGE_SUMMARY)
    test_results["discharge_summary_test"] = summary_result

    # Test 2: Risk Prediction
    risk_result = test_risk_prediction(SAMPLE_DISCHARGE_SUMMARY, patient_info)
    test_results["risk_prediction_test"] = risk_result

    # Test 3: Image Disease Detection (if image provided)
    image_result = test_image_disease_detection(args.image_path, patient_info)
    test_results["image_disease_detection_test"] = image_result

    # Overall status
    all_successful = summary_result["status"] == "success" and risk_result["status"] == "success"

    if args.image_path and image_result["status"] != "success":
        all_successful = False

    test_results["overall_status"] = "success" if all_successful else "partial"

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"\n1. Discharge Summary: {' PASS' if summary_result['status'] == 'success' else ' FAIL'}")
    print(f"2. Risk Prediction: {' PASS' if risk_result['status'] == 'success' else ' FAIL'}")

    if args.image_path:
        print(f"3. Image Disease Detection: {' PASS' if image_result['status'] == 'success' else ' FAIL'}")
    else:
        print(f"3. Image Disease Detection: ⚠ SKIPPED (no image provided)")

    print(f"\nOverall Status: {test_results['overall_status'].upper()}")
    print("=" * 70)

    # Save results
    try:
        output_file = project_root / args.output
        with open(output_file, "w") as f:
            json.dump(test_results, f, indent=2, default=str)
        print(f"\n Test results saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠ Could not save results: {e}")

    sys.exit(0 if test_results["overall_status"] == "success" else 1)


if __name__ == "__main__":
    main()
