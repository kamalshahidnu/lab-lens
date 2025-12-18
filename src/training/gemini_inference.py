#!/usr/bin/env python3
"""
Gemini Inference Module - Import wrapper
This module provides the GeminiInference class by importing from the actual location
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import from the actual location
try:
    # Try importing from model_development/scripts
    sys.path.insert(0, str(project_root / "model_development" / "scripts"))
    from gemini_inference import GeminiInference
except ImportError:
    # Fallback: create a simple wrapper that uses Gemini directly
    try:
        import google.generativeai as genai

        from src.utils.logging_config import get_logger

        logger = get_logger(__name__)

        class GeminiInference:
            """
            Simple Gemini Inference wrapper for FileQA
            """

            def __init__(self, model_name: str = "gemini-2.0-flash-exp", api_key: Optional[str] = None):
                """Initialize Gemini model"""
                api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable required")

                genai.configure(api_key=api_key)
                try:
                    self.model = genai.GenerativeModel(model_name)
                    self.model_name = model_name
                    logger.info(f"Initialized Gemini model: {model_name}")
                except Exception as e:
                    # Fallback to gemini-1.5-pro
                    logger.warning(f"Model {model_name} not available, trying gemini-1.5-pro...")
                    self.model = genai.GenerativeModel("gemini-1.5-pro")
                    self.model_name = "gemini-1.5-pro"
                    logger.info("Using gemini-1.5-pro as fallback")

            def answer_question(self, question: str, context: Optional[str] = None) -> str:
                """Answer a question with optional context"""
                if context:
                    prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {question}

Answer:"""
                else:
                    prompt = f"Answer this question: {question}"

                try:
                    response = self.model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.7,
                            max_output_tokens=2048,
                        ),
                    )
                    return response.text.strip()
                except Exception as e:
                    logger.error(f"Error generating answer: {e}")
                    return f"I encountered an error: {str(e)}"

    except ImportError as e:
        raise ImportError(f"Could not import GeminiInference: {e}. Please ensure google-generativeai is installed.")

__all__ = ["GeminiInference"]
