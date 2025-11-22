"""
Detection module

This module handles the classification of code as human or synthetic
based on similarity threshold analysis.
"""

from typing import List, Dict, Any

from .utils import print_status


def predict_synth_code(data: List[Dict[str, Any]], threshold: float = 0.7) -> Dict[str, float]:
    """
    Detect synthetic code based on similarity threshold

    Args:
        data: List of dictionaries containing 'similarity' and 'is_human' keys
        threshold: Similarity threshold for classification (default: 0.7)

    Returns:
        Dictionary containing accuracy metrics
    """
    print_status(f"Running detection with threshold={threshold}")

    false_positives = 0
    false_negatives = 0
    correct_predictions = 0

    for elem in data:
        is_synth_prediction = elem['similarity'] > threshold
        if is_synth_prediction and elem['is_human']:
            false_positives += 1
        elif not is_synth_prediction and not elem['is_human']:
            false_negatives += 1
        else:
            correct_predictions += 1

    total = len(data)
    accuracy = (correct_predictions / total) * 100
    false_positive_rate = (false_positives / total) * 100
    false_negative_rate = (false_negatives / total) * 100

    print_status("Detection Results:")
    print_status(f"  Correct: {accuracy:.2f}%")
    print_status(f"  False positives: {false_positive_rate:.2f}%")
    print_status(f"  False negatives: {false_negative_rate:.2f}%")

    return {
        'accuracy': accuracy,
        'false_positive_rate': false_positive_rate,
        'false_negative_rate': false_negative_rate,
        'correct': correct_predictions,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'total': total
    }
