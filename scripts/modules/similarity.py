"""
Similarity computation module

This module handles the computation of similarity scores between
original code and its rewrites, which is the key metric for detecting
synthetic code.
"""

import json
from difflib import SequenceMatcher
from typing import List

import numpy as np

from .utils import print_status


def normalized_edit_distance(s1: str, s2: str) -> float:
    """
    Compute normalized edit distance

    Args:
        s1: First string
        s2: Second string

    Returns:
        Float between 0 and 1, where 0 = identical, 1 = completely different
    """
    ratio = SequenceMatcher(None, s1, s2).ratio()
    return 1 - ratio


def compute_similarity(original: str, rewrites: List[str]) -> float:
    """
    Compute average similarity between original and rewrites

    Args:
        original: Original code string
        rewrites: List of rewritten code strings

    Returns:
        Similarity score (0 to 1, higher = more similar)
    """
    if not rewrites:
        return 0.0

    distances = [normalized_edit_distance(original, r) for r in rewrites]
    return 1 - np.mean(distances)


def compute_similarities(input_file: str, output_file: str) -> list:
    """
    Compute similarity scores between originals and rewrites

    This is the key metric for detecting synthetic code.

    Args:
        input_file: Path to input rewritten_data.json
        output_file: Path to save the similarity data

    Returns:
        List of dictionaries containing code samples with similarity scores
    """
    print_status("Starting similarity computation...")

    with open(input_file) as f:
        data = json.load(f)

    print_status(f"Loaded {len(data)} samples from {input_file}")

    data_with_similarities = []
    for i, elem in enumerate(data, 1):
        print_status(f"Computing similarity {i}/{len(data)}")

        elem['similarity'] = compute_similarity(elem['code'], elem['rewrites'])
        data_with_similarities.append(elem)

        print_status(f"  Similarity score: {elem['similarity']:.4f}")

    with open(output_file, 'w') as f:
        json.dump(data_with_similarities, f, indent=2)

    print_status(f"Saved similarity data to {output_file}")
    print_status("Similarity computation complete!")

    return data_with_similarities
