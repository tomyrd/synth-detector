"""
Synthetic Code Detection Modules

This package contains modular components for the synthetic code detection pipeline.
"""

from .utils import print_status, clean_code
from .generator import generate_synth_code, prepare_dataset
from .rewriter import rewrite, rewrite_dataset
from .similarity import normalized_edit_distance, compute_similarity, compute_similarities
from .detector import predict_synth_code

__all__ = [
    'print_status',
    'clean_code',
    'generate_synth_code',
    'prepare_dataset',
    'rewrite',
    'rewrite_dataset',
    'normalized_edit_distance',
    'compute_similarity',
    'compute_similarities',
    'predict_synth_code',
]
