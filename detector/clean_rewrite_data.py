#!/usr/bin/env python3
"""
Clean rewrite data by removing entries with invalid rewrites.

This script:
1. Loads rewritten_data.json and similarity_data.json
2. Filters out invalid rewrites (formulas, doctests, non-functions)
3. Optionally removes entries with fewer than min_rewrites valid rewrites
4. Saves cleaned data to new files (or overwrites original with --in-place flag)
"""

import json
import argparse
from pathlib import Path
from validate_rewrites import is_valid_function_rewrite, clean_rewrite_entry


def load_json(filepath: Path) -> list:
    """Load JSON data from file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json(data: list, filepath: Path, indent: int = 2) -> None:
    """Save data to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent)


def clean_dataset(data: list, min_rewrites: int = 4) -> tuple:
    """
    Clean dataset by filtering invalid rewrites.

    Args:
        data: List of entries with rewrites
        min_rewrites: Minimum number of valid rewrites to keep entry

    Returns:
        Tuple of (cleaned_data, stats_dict)
    """
    cleaned = []
    stats = {
        'total_entries': len(data),
        'entries_removed': 0,
        'entries_kept': 0,
        'total_rewrites_before': 0,
        'total_rewrites_after': 0,
        'invalid_rewrites_removed': 0,
        'removed_by_type': {
            'formula': 0,
            'doctest': 0,
            'no_function': 0,
            'syntax_error': 0,
            'insufficient_valid': 0
        }
    }

    for entry in data:
        if 'rewrites' not in entry:
            stats['entries_removed'] += 1
            continue

        original_count = len(entry['rewrites'])
        stats['total_rewrites_before'] += original_count

        # Track types of invalid rewrites
        for rewrite in entry['rewrites']:
            if not is_valid_function_rewrite(rewrite):
                stats['invalid_rewrites_removed'] += 1

                # Categorize the type of invalid rewrite
                if '>>>' in rewrite:
                    stats['removed_by_type']['doctest'] += 1
                elif 'def ' not in rewrite:
                    if '=' in rewrite:
                        stats['removed_by_type']['formula'] += 1
                    else:
                        stats['removed_by_type']['no_function'] += 1
                else:
                    stats['removed_by_type']['syntax_error'] += 1

        # Clean the entry
        cleaned_entry = clean_rewrite_entry(entry, min_rewrites)

        if cleaned_entry:
            cleaned.append(cleaned_entry)
            stats['entries_kept'] += 1
            stats['total_rewrites_after'] += len(cleaned_entry['rewrites'])
        else:
            stats['entries_removed'] += 1
            stats['removed_by_type']['insufficient_valid'] += 1

    return cleaned, stats


def print_stats(stats: dict) -> None:
    """Print cleaning statistics."""
    print("\n" + "="*60)
    print("CLEANING STATISTICS")
    print("="*60)
    print(f"\nTotal entries processed: {stats['total_entries']}")
    print(f"Entries kept: {stats['entries_kept']}")
    print(f"Entries removed: {stats['entries_removed']}")
    print(f"Removal rate: {stats['entries_removed']/stats['total_entries']*100:.1f}%")

    print(f"\nTotal rewrites before: {stats['total_rewrites_before']}")
    print(f"Total rewrites after: {stats['total_rewrites_after']}")
    print(f"Invalid rewrites removed: {stats['invalid_rewrites_removed']}")
    print(f"Removal rate: {stats['invalid_rewrites_removed']/stats['total_rewrites_before']*100:.1f}%")

    print(f"\nInvalid rewrites by type:")
    print(f"  - Doctests: {stats['removed_by_type']['doctest']}")
    print(f"  - Formulas: {stats['removed_by_type']['formula']}")
    print(f"  - No function def: {stats['removed_by_type']['no_function']}")
    print(f"  - Syntax errors: {stats['removed_by_type']['syntax_error']}")
    print(f"  - Entries with insufficient valid rewrites: {stats['removed_by_type']['insufficient_valid']}")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Clean rewrite data by removing invalid entries'
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Input JSON file (default: detector/rewritten_data.json or detector/similarity_data.json)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file (default: adds _cleaned suffix)'
    )
    parser.add_argument(
        '--min-rewrites',
        type=int,
        default=4,
        help='Minimum number of valid rewrites required (default: 4)'
    )
    parser.add_argument(
        '--in-place',
        action='store_true',
        help='Overwrite input file with cleaned data'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Clean both rewritten_data.json and similarity_data.json'
    )

    args = parser.parse_args()

    # Determine files to process
    files_to_process = []

    if args.all:
        files_to_process = [
            'detector/rewritten_data.json',
            'detector/similarity_data.json'
        ]
    elif args.input:
        files_to_process = [args.input]
    else:
        # Default to similarity_data.json
        files_to_process = ['detector/similarity_data.json']

    # Process each file
    for input_file in files_to_process:
        input_path = Path(input_file)

        if not input_path.exists():
            print(f"Error: File {input_path} not found")
            continue

        print(f"\nProcessing: {input_path}")

        # Determine output file
        if args.in_place:
            output_path = input_path
        elif args.output:
            output_path = Path(args.output)
        else:
            # Add _cleaned suffix
            output_path = input_path.parent / f"{input_path.stem}_cleaned{input_path.suffix}"

        # Load data
        print(f"Loading data from {input_path}...")
        data = load_json(input_path)

        # Clean data
        print(f"Cleaning data (minimum {args.min_rewrites} valid rewrites required)...")
        cleaned_data, stats = clean_dataset(data, args.min_rewrites)

        # Print statistics
        print_stats(stats)

        # Save cleaned data
        print(f"Saving cleaned data to {output_path}...")
        save_json(cleaned_data, output_path)

        print(f"✓ Successfully cleaned {input_path}")
        print(f"  Cleaned data saved to: {output_path}")


if __name__ == '__main__':
    main()
