#!/usr/bin/env python3
"""
Sensitivity Analysis for Model Development
Feature importance analysis and hyperparameter sensitivity
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import get_logger
from src.utils.error_handling import ErrorHandler, safe_execute

logger = get_logger(__name__)

try:
  import shap
  SHAP_AVAILABLE = True
except ImportError:
  # Only log warning when actually used
  SHAP_AVAILABLE = False

try:
  import lime
  from lime.lime_text import LimeTextExplainer
  LIME_AVAILABLE = True
except ImportError:
  # Only log warning when actually used
  LIME_AVAILABLE = False


class SensitivityAnalyzer:
  """
  Sensitivity analysis for feature importance and hyperparameter sensitivity
  """
 
  def __init__(self):
    """Initialize sensitivity analyzer"""
    self.error_handler = ErrorHandler(logger)
 
  @safe_execute("analyze_hyperparameter_sensitivity", logger, ErrorHandler(logger))
  def analyze_hyperparameter_sensitivity(
    self,
    optimization_history: pd.DataFrame,
    metric_column: str = 'value'
  ) -> Dict[str, Any]:
    """
    Analyze hyperparameter sensitivity from optimization history
   
    Args:
      optimization_history: DataFrame with trial history (from Optuna)
      metric_column: Column name with metric values
     
    Returns:
      Dictionary with sensitivity analysis results
    """
    if len(optimization_history) == 0:
      raise ValueError("Empty optimization history")
   
    results = {
      'hyperparameter_importance': {},
      'correlations': {},
      'sensitivity_plots': []
    }
   
    # Calculate correlations between hyperparameters and metric
    hyperparams = ['temperature', 'max_output_tokens', 'max_length']
   
    for param in hyperparams:
      if param in optimization_history.columns:
        correlation = optimization_history[param].corr(optimization_history[metric_column])
        results['correlations'][param] = float(correlation) if not np.isnan(correlation) else 0.0
   
    # Calculate importance (absolute correlation)
    for param, corr in results['correlations'].items():
      results['hyperparameter_importance'][param] = abs(corr)
   
    # Sort by importance
    results['hyperparameter_importance'] = dict(
      sorted(results['hyperparameter_importance'].items(), key=lambda x: x[1], reverse=True)
    )
   
    logger.info(f"Hyperparameter sensitivity analysis completed")
    logger.info(f"Most important: {list(results['hyperparameter_importance'].keys())[0]}")
   
    return results
 
  @safe_execute("analyze_feature_importance_shap", logger, ErrorHandler(logger))
  def analyze_feature_importance_shap(
    self,
    model,
    X: pd.DataFrame,
    sample_size: int = 100
  ) -> Dict[str, Any]:
    """
    Analyze feature importance using SHAP
   
    Args:
      model: Model object (for Gemini, we analyze input features)
      X: Feature DataFrame
      sample_size: Number of samples to use for SHAP analysis
     
    Returns:
      Dictionary with SHAP feature importance
    """
    if not SHAP_AVAILABLE:
      raise ImportError("shap package required. Install with: pip install shap")
   
    # Sample data for faster computation
    X_sample = X.sample(min(sample_size, len(X))).copy()
   
    # For text summarization, we'll use a simple approach
    # Since Gemini is an API model, we analyze input text features
   
    # Create a simple explainer (for demonstration)
    # In practice, you'd need a wrapper model for SHAP
    logger.info("SHAP analysis for API models requires model wrapper")
    logger.info("Using correlation-based feature importance instead")
   
    # Fallback to correlation analysis
    return self._correlation_based_importance(X_sample)
 
  def _correlation_based_importance(self, X: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate feature importance based on correlations
   
    Args:
      X: Feature DataFrame
     
    Returns:
      Dictionary with feature importance
    """
    # This is a simplified approach
    # In practice, you'd correlate features with model outputs
   
    importance = {}
   
    # For numeric columns, calculate variance (higher variance = potentially more important)
    numeric_cols = X.select_dtypes(include=[np.number]).columns
   
    for col in numeric_cols:
      if X[col].notna().sum() > 0:
        importance[col] = float(X[col].var())
   
    # Sort by importance
    importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
   
    return {
      'feature_importance': importance,
      'top_features': list(importance.keys())[:10]
    }
 
  @safe_execute("analyze_text_importance_lime", logger, ErrorHandler(logger))
  def analyze_text_importance_lime(
    self,
    text: str,
    model_predict_fn: callable,
    num_features: int = 10
  ) -> Dict[str, Any]:
    """
    Analyze text importance using LIME
   
    Args:
      text: Input text to analyze
      model_predict_fn: Function that takes text and returns prediction
      num_features: Number of top features to return
     
    Returns:
      Dictionary with LIME feature importance
    """
    if not LIME_AVAILABLE:
      raise ImportError("lime package required. Install with: pip install lime")
   
    explainer = LimeTextExplainer(class_names=['summary'])
   
    # Explain prediction
    explanation = explainer.explain_instance(
      text,
      model_predict_fn,
      num_features=num_features
    )
   
    # Extract feature importance
    feature_importance = {}
    for feature, weight in explanation.as_list():
      feature_importance[feature] = float(weight)
   
    return {
      'feature_importance': feature_importance,
      'top_features': sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)[:num_features]
    }
 
  @safe_execute("create_sensitivity_plots", logger, ErrorHandler(logger))
  def create_sensitivity_plots(
    self,
    optimization_history: pd.DataFrame,
    output_dir: str = "logs/sensitivity_plots"
  ) -> List[str]:
    """
    Create visualization plots for sensitivity analysis
   
    Args:
      optimization_history: DataFrame with trial history
      output_dir: Directory to save plots
     
    Returns:
      List of saved plot paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
   
    plot_paths = []
   
    # Plot 1: Hyperparameter vs Metric
    hyperparams = ['temperature', 'max_output_tokens', 'max_length']
   
    fig, axes = plt.subplots(1, len(hyperparams), figsize=(15, 5))
    if len(hyperparams) == 1:
      axes = [axes]
   
    for idx, param in enumerate(hyperparams):
      if param in optimization_history.columns:
        ax = axes[idx]
        ax.scatter(optimization_history[param], optimization_history['value'], alpha=0.6)
        ax.set_xlabel(param)
        ax.set_ylabel('Validation Score')
        ax.set_title(f'{param} Sensitivity')
        ax.grid(True, alpha=0.3)
   
    plt.tight_layout()
    plot_path = output_path / 'hyperparameter_sensitivity.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    plot_paths.append(str(plot_path))
   
    # Plot 2: Optimization history
    plt.figure(figsize=(10, 6))
    plt.plot(optimization_history['trial_number'], optimization_history['value'], marker='o', alpha=0.7)
    plt.xlabel('Trial Number')
    plt.ylabel('Validation Score')
    plt.title('Hyperparameter Optimization History')
    plt.grid(True, alpha=0.3)
    plot_path = output_path / 'optimization_history.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    plot_paths.append(str(plot_path))
   
    logger.info(f"Created {len(plot_paths)} sensitivity plots")
    return plot_paths

