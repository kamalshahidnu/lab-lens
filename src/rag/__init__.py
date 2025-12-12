"""
RAG (Retrieval-Augmented Generation) Module for Patient Report Q&A
Enables patients to ask questions about their discharge summaries
"""

from .rag_system import RAGSystem
from .document_processor import DocumentProcessor
from .file_qa import FileQA
from .vector_db import VectorDatabase

__all__ = ['RAGSystem', 'DocumentProcessor', 'FileQA', 'VectorDatabase']

# NOTE:
# Avoid importing PatientQA at package import time. PatientQA pulls in optional
# Gemini/training dependencies which are not required for FileQA and can break
# deployments that only run the Streamlit file Q&A interface.
try:
    from .patient_qa import PatientQA  # noqa: F401
    __all__.append('PatientQA')
except Exception:
    # Keep the package importable even if optional deps are missing.
    PatientQA = None  # type: ignore



