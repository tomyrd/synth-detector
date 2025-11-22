#!/usr/bin/env python3
"""
Synthetic Code Detection Pipeline

This script combines all the functionality from the proof-of-concept notebooks:
1. Dataset preparation (generate synthetic code)
2. Code rewriting (generate variations)
3. Similarity computation (compare originals with rewrites)
4. Detection (classify based on similarity threshold)
"""

import json
import re
import random
import argparse
from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Dict, Any

import numpy as np
import ollama


def print_status(message: str):
    """Print status message with formatting"""
    print(f"[STATUS] {message}")


def clean_code(code: str) -> str:
    """Remove comments and normalize whitespace"""
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    code = '\n'.join(line for line in code.split('\n') if line.strip())
    return code.strip()


def generate_synth_code(prompt: str) -> str:
    """Generate synthetic code using LLM based on a text prompt"""
    response = ollama.chat(
        model="codellama:7b-instruct",
        messages=[
            {'role': 'system', 'content': "You are a code generation assistant. Generate only the Python function code, no explanations. Also, don't add comments to the code."},
            {'role': 'user', 'content': f"Write a Python function:\n{prompt}"}
        ],
    )

    pattern = r'```\n(.*?)```'
    match = re.search(pattern, response['message']['content'], re.DOTALL)
    if match:
        return match.group(1)
    return response['message']['content']


def rewrite(code: str, n_samples: int = 4) -> List[str]:
    """Generate n rewritten versions of the code"""
    cleaned_code = clean_code(code)

    prompt = f"""### Code:
{cleaned_code}

### Instruction:
 Please explain the functionality of the given code, then rewrite it in a single markdown code block. No additional clarifications.
"""

    rewrites = []
    for i in range(n_samples):
        try:
            response = ollama.chat(
                model="codellama:7b-instruct",
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': 0.8,
                    'top_p': 0.95,
                    'seed': None
                }
            )

            content = response['message']['content']
            code_blocks = re.findall(r'```\w*\n(.*?)```', content, re.DOTALL)

            if code_blocks:
                rewrite_code = clean_code(code_blocks[0])
                rewrites.append(rewrite_code)
            else:
                print(f"  Warning: Failed to parse rewrite {i+1}")

        except Exception as e:
            print(f"  Warning: Rewrite {i+1} failed: {e}")
            continue

    return rewrites


def normalized_edit_distance(s1: str, s2: str) -> float:
    """Compute normalized edit distance (0 = identical, 1 = completely different)"""
    ratio = SequenceMatcher(None, s1, s2).ratio()
    return 1 - ratio


def compute_similarity(original: str, rewrites: List[str]) -> float:
    """Compute average similarity between original and rewrites"""
    if not rewrites:
        return 0.0

    distances = [normalized_edit_distance(original, r) for r in rewrites]
    return 1 - np.mean(distances)


def prepare_dataset(input_file: str, output_file: str, num_samples: int = None):
    """
    Step 1: Prepare dataset by generating synthetic code
    Reads human-written code and generates synthetic versions
    """
    print_status("Starting dataset preparation...")

    with open(input_file) as f:
        data = json.load(f)

    if num_samples:
        data = data[:num_samples]

    print_status(f"Loaded {len(data)} samples from {input_file}")

    # Clean data
    cleaned_data = [{
        'text': elem['text'],
        'code': elem['code'].replace('\r\n', '\n'),
        'task_id': elem['task_id'],
        'is_human': 1
    } for elem in data]

    # Generate synthetic versions
    result = []
    print_status("Generating synthetic code samples...")
    for i, elem in enumerate(cleaned_data, 1):
        result.append(elem)

        print_status(f"Generating synthetic code {i}/{len(cleaned_data)}")
        synth_code = generate_synth_code(elem['text'])

        result.append({
            'text': elem['text'],
            'code': synth_code,
            'task_id': elem['task_id'],
            'is_human': 0
        })

    # Strip unnecessary fields and shuffle
    result = [{'code': elem['code'], 'is_human': elem['is_human']} for elem in result]
    random.shuffle(result)

    print_status(f"Dataset created: {len(result)} total samples")
    print_status(f"  Human: {sum(1 for d in result if d['is_human'] == 1)}")
    print_status(f"  Synthetic: {sum(1 for d in result if d['is_human'] == 0)}")

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print_status(f"Saved dataset to {output_file}")
    return result


def rewrite_dataset(input_file: str, output_file: str, n_rewrites: int = 4):
    """
    Step 2: Generate rewrites for each code sample
    Creates variations of each code to measure consistency
    """
    print_status("Starting code rewriting process...")

    with open(input_file) as f:
        data = json.load(f)

    print_status(f"Loaded {len(data)} samples from {input_file}")

    data_with_rewrites = []
    for i, elem in enumerate(data, 1):
        print_status(f"Rewriting code sample {i}/{len(data)}")

        elem['rewrites'] = rewrite(elem['code'], n_rewrites)
        elem['code'] = clean_code(elem['code'])
        data_with_rewrites.append(elem)

        print_status(f"  Generated {len(elem['rewrites'])} rewrites")

    with open(output_file, 'w') as f:
        json.dump(data_with_rewrites, f, indent=2)

    print_status(f"Saved rewritten data to {output_file}")
    return data_with_rewrites


def compute_similarities(input_file: str, output_file: str):
    """
    Step 3: Compute similarity scores between originals and rewrites
    This is the key metric for detecting synthetic code
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


def predict_synth_code(data: List[Dict[str, Any]], threshold: float = 0.7):
    """
    Step 4 (Optional): Detect synthetic code based on similarity threshold
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
    print_status("Detection Results:")
    print_status(f"  Correct: {(correct_predictions/total)*100:.2f}%")
    print_status(f"  False positives: {(false_positives/total)*100:.2f}%")
    print_status(f"  False negatives: {(false_negatives/total)*100:.2f}%")


def main():
    parser = argparse.ArgumentParser(
        description="Synthetic Code Detection Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline from MBPP data
  python synth_detector.py --input data/mbpp/data.json --full-pipeline

  # Run only similarity computation on existing rewritten data
  python synth_detector.py --rewritten-data detector/rewritten_data.json --similarity-only

  # Run detection on existing similarity data
  python synth_detector.py --similarity-data scripts/similarity_data.json --detect-only --threshold 0.9
        """
    )

    parser.add_argument('--input', type=str, help='Input MBPP data file')
    parser.add_argument('--num-samples', type=int, help='Number of samples to process (default: all)')
    parser.add_argument('--output-dir', type=str, default='scripts', help='Output directory (default: scripts)')
    parser.add_argument('--n-rewrites', type=int, default=4, help='Number of rewrites per sample (default: 4)')
    parser.add_argument('--threshold', type=float, default=0.7, help='Detection threshold (default: 0.7)')

    # Pipeline options
    parser.add_argument('--full-pipeline', action='store_true', help='Run complete pipeline')
    parser.add_argument('--prepare-only', action='store_true', help='Only prepare dataset')
    parser.add_argument('--rewrite-only', action='store_true', help='Only rewrite code')
    parser.add_argument('--similarity-only', action='store_true', help='Only compute similarities')
    parser.add_argument('--detect-only', action='store_true', help='Only run detection')

    # Input files for partial pipeline
    parser.add_argument('--detection-data', type=str, help='Input detection_data.json for rewrite step')
    parser.add_argument('--rewritten-data', type=str, help='Input rewritten_data.json for similarity step')
    parser.add_argument('--similarity-data', type=str, help='Input similarity_data.json for detection step')

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    detection_data_file = output_dir / 'detection_data.json'
    rewritten_data_file = output_dir / 'rewritten_data.json'
    similarity_data_file = output_dir / 'similarity_data.json'

    print_status("="*60)
    print_status("Synthetic Code Detection Pipeline")
    print_status("="*60)

    # Full pipeline
    if args.full_pipeline:
        if not args.input:
            print("Error: --input required for full pipeline")
            return

        data = prepare_dataset(args.input, detection_data_file, args.num_samples)
        data = rewrite_dataset(detection_data_file, rewritten_data_file, args.n_rewrites)
        data = compute_similarities(rewritten_data_file, similarity_data_file)
        predict_synth_code(data, args.threshold)

    # Prepare dataset only
    elif args.prepare_only:
        if not args.input:
            print("Error: --input required for dataset preparation")
            return
        prepare_dataset(args.input, detection_data_file, args.num_samples)

    # Rewrite only
    elif args.rewrite_only:
        input_file = args.detection_data or detection_data_file
        rewrite_dataset(input_file, rewritten_data_file, args.n_rewrites)

    # Similarity only
    elif args.similarity_only:
        input_file = args.rewritten_data or rewritten_data_file
        compute_similarities(input_file, similarity_data_file)

    # Detect only
    elif args.detect_only:
        input_file = args.similarity_data or similarity_data_file
        with open(input_file) as f:
            data = json.load(f)
        predict_synth_code(data, args.threshold)

    else:
        parser.print_help()
        return

    print_status("="*60)
    print_status("Pipeline completed successfully!")
    print_status("="*60)


if __name__ == '__main__':
    main()
