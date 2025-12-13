#!/usr/bin/env python3
"""
Gemini Model Module - Import wrapper
This module provides the GeminiSummarizer class by importing from the actual location
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import from the actual location
try:
  # Try importing from model_development/scripts
  sys.path.insert(0, str(project_root / "model_development" / "scripts"))
  from gemini_model import GeminiSummarizer, load_gemini_model
except ImportError:
  # Fallback: create a simple wrapper that uses Gemini directly
  try:
    import google.generativeai as genai
    from src.utils.logging_config import get_logger
   
    logger = get_logger(__name__)
   
    class GeminiSummarizer:
      """
      Simple Gemini Summarizer wrapper
      """
     
      def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash-exp"):
        """Initialize Gemini model"""
        api_key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
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
     
      def summarize(self, text: str, max_length: int = 150) -> str:
        """Generate summary for text"""
        prompt = f"""Summarize the following medical text in a clear, concise manner (maximum {max_length} words):

{text}

Summary:"""
       
        try:
          response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
              temperature=0.3,
              max_output_tokens=2048,
            )
          )
          return response.text.strip()
        except Exception as e:
          logger.error(f"Error generating summary: {e}")
          return f"Error generating summary: {str(e)}"
     
      def batch_summarize(self, texts: List[str], max_length: int = 150, batch_size: int = 10) -> List[str]:
        """Generate summaries for multiple texts"""
        summaries = []
        for i in range(0, len(texts), batch_size):
          batch = texts[i:i+batch_size]
          batch_summaries = [self.summarize(text, max_length) for text in batch]
          summaries.extend(batch_summaries)
        return summaries
     
      def process_dataframe(self, df: pd.DataFrame, input_column: str = 'cleaned_text',
                output_column: str = 'gemini_summary', max_length: int = 150) -> pd.DataFrame:
        """Process DataFrame and add summaries"""
        df = df.copy()
        df[output_column] = df[input_column].apply(lambda x: self.summarize(str(x), max_length))
        return df
   
    def load_gemini_model(api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash-exp"):
      """Load Gemini model"""
      return GeminiSummarizer(api_key=api_key, model_name=model_name)
     
  except ImportError as e:
    raise ImportError(f"Could not import GeminiSummarizer: {e}. Please ensure google-generativeai is installed.")

__all__ = ['GeminiSummarizer', 'load_gemini_model']

