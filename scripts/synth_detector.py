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
import argparse
from pathlib import Path

from modules import (
    print_status,
    prepare_dataset,
    rewrite_dataset,
    compute_similarities,
    predict_synth_code
)


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

    # General parameters
    parser.add_argument('--input', type=str, help='Input MBPP data file')
    parser.add_argument('--num-samples', type=int, help='Number of samples to process (default: all)')
    parser.add_argument('--output-dir', type=str, default='scripts', help='Output directory (default: scripts)')

    # LLM parameters
    parser.add_argument('--model', type=str, default='codellama:7b-instruct',
                       help='LLM model to use (default: codellama:7b-instruct)')

    # Generation parameters (for synthetic code generation)
    parser.add_argument('--gen-temperature', type=float,
                       help='Temperature for synthetic code generation (default: None)')
    parser.add_argument('--gen-top-p', type=float,
                       help='Top-p for synthetic code generation (default: None)')

    # Rewrite parameters
    parser.add_argument('--n-rewrites', type=int, default=4,
                       help='Number of rewrites per sample (default: 4)')
    parser.add_argument('--rewrite-temperature', type=float, default=0.8,
                       help='Temperature for code rewriting (default: 0.8)')
    parser.add_argument('--rewrite-top-p', type=float, default=0.95,
                       help='Top-p for code rewriting (default: 0.95)')
    parser.add_argument('--rewrite-seed', type=int,
                       help='Seed for code rewriting (default: None for random)')

    # Detection parameters
    parser.add_argument('--threshold', type=float, default=0.7,
                       help='Detection threshold (default: 0.7)')

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

        data = prepare_dataset(args.input, detection_data_file, args.num_samples,
                              model=args.model, temperature=args.gen_temperature,
                              top_p=args.gen_top_p)
        data = rewrite_dataset(detection_data_file, rewritten_data_file, args.n_rewrites,
                              model=args.model, temperature=args.rewrite_temperature,
                              top_p=args.rewrite_top_p, seed=args.rewrite_seed)
        data = compute_similarities(rewritten_data_file, similarity_data_file)
        predict_synth_code(data, args.threshold)

    # Prepare dataset only
    elif args.prepare_only:
        if not args.input:
            print("Error: --input required for dataset preparation")
            return
        prepare_dataset(args.input, detection_data_file, args.num_samples,
                       model=args.model, temperature=args.gen_temperature,
                       top_p=args.gen_top_p)

    # Rewrite only
    elif args.rewrite_only:
        input_file = args.detection_data or detection_data_file
        rewrite_dataset(input_file, rewritten_data_file, args.n_rewrites,
                       model=args.model, temperature=args.rewrite_temperature,
                       top_p=args.rewrite_top_p, seed=args.rewrite_seed)

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
