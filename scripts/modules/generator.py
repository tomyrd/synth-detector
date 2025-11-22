"""
Synthetic code generation module

This module handles the generation of synthetic code using LLMs and
the preparation of datasets for the detection pipeline.
"""

import json
import re
import random
from typing import Optional

import ollama

from .utils import print_status


def generate_synth_code(prompt: str, model: str = "codellama:7b-instruct",
                        temperature: Optional[float] = None,
                        top_p: Optional[float] = None) -> str:
    """
    Generate synthetic code using LLM based on a text prompt

    Args:
        prompt: Description of the code to generate
        model: LLM model to use
        temperature: Sampling temperature (None for default)
        top_p: Nucleus sampling parameter (None for default)

    Returns:
        Generated code as a string
    """
    options = {}
    if temperature is not None:
        options['temperature'] = temperature
    if top_p is not None:
        options['top_p'] = top_p

    response = ollama.chat(
        model=model,
        messages=[
            {'role': 'system', 'content': "You are a code generation assistant. Generate only the Python function code, no explanations. Also, don't add comments to the code."},
            {'role': 'user', 'content': f"Write a Python function:\n{prompt}"}
        ],
        options=options if options else None
    )

    pattern = r'```\n(.*?)```'
    match = re.search(pattern, response['message']['content'], re.DOTALL)
    if match:
        return match.group(1)
    return response['message']['content']


def prepare_dataset(input_file: str, output_file: str, num_samples: Optional[int] = None,
                   model: str = "codellama:7b-instruct",
                   temperature: Optional[float] = None,
                   top_p: Optional[float] = None) -> list:
    """
    Prepare dataset by generating synthetic code

    Reads human-written code and generates synthetic versions for comparison.

    Args:
        input_file: Path to input MBPP data file
        output_file: Path to save the prepared dataset
        num_samples: Number of samples to process (None for all)
        model: LLM model to use
        temperature: Sampling temperature for generation
        top_p: Nucleus sampling parameter for generation

    Returns:
        List of dictionaries containing code samples with is_human labels
    """
    print_status("Starting dataset preparation...")

    with open(input_file) as f:
        data = json.load(f)

    if num_samples:
        data = data[:num_samples]

    print_status(f"Loaded {len(data)} samples from {input_file}")
    print_status(f"Generation settings: model={model}, temperature={temperature}, top_p={top_p}")

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
        synth_code = generate_synth_code(elem['text'], model=model,
                                        temperature=temperature, top_p=top_p)

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
