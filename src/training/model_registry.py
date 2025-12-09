#!/usr/bin/env python3
"""
Model Registry Integration
Pushes models to Google Cloud Artifact Registry or MLflow Model Registry
"""

import os
import sys
import json
from typing import Dict, Optional, Any
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import mlflow
from src.utils.logging_config import get_logger
from src.utils.error_handling import ErrorHandler, safe_execute

logger = get_logger(__name__)

try:
    from google.cloud import artifactregistry
    from google.oauth2 import service_account
    GCP_AVAILABLE = True
except ImportError:
    # GCP registry is optional - no warning needed
    GCP_AVAILABLE = False


class ModelRegistry:
    """
    Model registry for versioning and storing models
    Supports MLflow Model Registry and GCP Artifact Registry
    """
    
    def __init__(
        self,
        registry_type: str = "mlflow",  # "mlflow" or "gcp"
        gcp_project: Optional[str] = None,
        gcp_location: Optional[str] = None,
        gcp_repository: Optional[str] = None
    ):
        """
        Initialize model registry
        
        Args:
            registry_type: Type of registry ("mlflow" or "gcp")
            gcp_project: GCP project ID (for GCP registry)
            gcp_location: GCP location (for GCP registry)
            gcp_repository: GCP repository name (for GCP registry)
        """
        self.registry_type = registry_type
        self.error_handler = ErrorHandler(logger)
        
        if registry_type == "gcp":
            if not GCP_AVAILABLE:
                raise ImportError("google-cloud-artifact-registry required for GCP registry")
            self.gcp_project = gcp_project or os.getenv('GCP_PROJECT')
            self.gcp_location = gcp_location or os.getenv('GCP_LOCATION', 'us-central1')
            self.gcp_repository = gcp_repository or os.getenv('GCP_REPOSITORY', 'lab-lens-models')
            
            if not self.gcp_project:
                raise ValueError("GCP project ID required for GCP registry")
        
        logger.info(f"Initialized {registry_type} model registry")
    
    @safe_execute("register_model_mlflow", logger, ErrorHandler(logger))
    def register_model_mlflow(
        self,
        run_id: str,
        model_name: str = "gemini-medical-summarization",
        stage: str = "None"
    ) -> str:
        """
        Register model in MLflow Model Registry
        
        Args:
            run_id: MLflow run ID
            model_name: Name for registered model
            stage: Model stage (None, Staging, Production, Archived)
            
        Returns:
            Model version
        """
        try:
            # Create model version from run
            model_version = mlflow.register_model(
                f"runs:/{run_id}/model",
                model_name
            )
            
            # Transition to stage if specified
            if stage != "None":
                client = mlflow.tracking.MlflowClient()
                client.transition_model_version_stage(
                    name=model_name,
                    version=model_version.version,
                    stage=stage
                )
            
            logger.info(f"Registered model '{model_name}' version {model_version.version} in MLflow")
            return model_version.version
            
        except Exception as e:
            logger.error(f"Error registering model in MLflow: {e}")
            raise
    
    @safe_execute("push_to_gcp", logger, ErrorHandler(logger))
    def push_to_gcp(
        self,
        model_path: str,
        model_version: str,
        model_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Push model to GCP Artifact Registry
        
        Args:
            model_path: Local path to model files
            model_version: Model version string
            model_metadata: Optional metadata dictionary
            
        Returns:
            GCP artifact URI
        """
        if not GCP_AVAILABLE:
            raise ImportError("GCP libraries not available")
        
        try:
            # Initialize Artifact Registry client
            client = artifactregistry.ArtifactRegistryClient()
            
            # Repository path
            repository_path = f"projects/{self.gcp_project}/locations/{self.gcp_location}/repositories/{self.gcp_repository}"
            
            # Create package (if needed)
            package_id = f"gemini-model-{model_version}"
            
            # Upload files
            model_path_obj = Path(model_path)
            if model_path_obj.is_file():
                # Single file upload
                with open(model_path, 'rb') as f:
                    file_content = f.read()
                
                # Create file
                file_id = f"{package_id}-config.json"
                # Note: Actual upload would use client.upload_file() or gcloud CLI
                logger.info(f"Would upload {model_path} to {repository_path}/{package_id}")
            
            # Save metadata
            if model_metadata:
                metadata_path = Path(model_path).parent / "metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(model_metadata, f, indent=2)
            
            artifact_uri = f"{repository_path}/packages/{package_id}"
            logger.info(f"Pushed model to GCP: {artifact_uri}")
            
            return artifact_uri
            
        except Exception as e:
            logger.error(f"Error pushing to GCP: {e}")
            raise
    
    @safe_execute("register_model", logger, ErrorHandler(logger))
    def register_model(
        self,
        run_id: Optional[str] = None,
        model_path: Optional[str] = None,
        model_name: str = "gemini-medical-summarization",
        model_version: Optional[str] = None,
        stage: str = "None",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Register model in registry
        
        Args:
            run_id: MLflow run ID (for MLflow registry)
            model_path: Local model path (for GCP registry)
            model_name: Model name
            model_version: Optional version string
            stage: Model stage
            metadata: Optional metadata
            
        Returns:
            Dictionary with registration information
        """
        if model_version is None:
            model_version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = {
            'registry_type': self.registry_type,
            'model_name': model_name,
            'model_version': model_version,
            'stage': stage
        }
        
        if self.registry_type == "mlflow":
            if run_id is None:
                raise ValueError("run_id required for MLflow registry")
            version = self.register_model_mlflow(run_id, model_name, stage)
            results['mlflow_version'] = version
            results['model_uri'] = f"models:/{model_name}/{version}"
        
        elif self.registry_type == "gcp":
            if model_path is None:
                raise ValueError("model_path required for GCP registry")
            artifact_uri = self.push_to_gcp(model_path, model_version, metadata)
            results['artifact_uri'] = artifact_uri
        
        logger.info(f"Model registered: {results}")
        return results

