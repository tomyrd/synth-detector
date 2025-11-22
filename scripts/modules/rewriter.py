"""
Code rewriting module

This module handles the generation of code rewrites to measure
consistency and variability in code generation.
"""

import json
import re
from typing import List, Optional

import ollama

from .utils import print_status, clean_code


def rewrite(code: str, n_samples: int = 4, model: str = "codellama:7b-instruct",
            temperature: float = 0.8, top_p: float = 0.95,
            seed: Optional[int] = None) -> List[str]:
    """
    Generate n rewritten versions of the code

    Args:
        code: Original code to rewrite
        n_samples: Number of rewrites to generate
        model: LLM model to use
        temperature: Sampling temperature
        top_p: Nucleus sampling parameter
        seed: Random seed for reproducibility (None for random)

    Returns:
        List of rewritten code samples
    """
    cleaned_code = clean_code(code)

    prompt = f"""### Code:
{cleaned_code}

### Instruction:
 Please explain the functionality of the given code, then rewrite it in a single markdown code block. No additional clarifications.
"""

    rewrites = []
    for i in range(n_samples):
        try:
            options = {
                'temperature': temperature,
                'top_p': top_p,
                'seed': seed
            }

            response = ollama.chat(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                options=options
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


def rewrite_dataset(input_file: str, output_file: str, n_rewrites: int = 4,
                   model: str = "codellama:7b-instruct", temperature: float = 0.8,
                   top_p: float = 0.95, seed: Optional[int] = None) -> list:
    """
    Generate rewrites for each code sample in the dataset

    Creates variations of each code to measure consistency.

    Args:
        input_file: Path to input detection_data.json
        output_file: Path to save the rewritten data
        n_rewrites: Number of rewrites per sample
        model: LLM model to use
        temperature: Sampling temperature
        top_p: Nucleus sampling parameter
        seed: Random seed for reproducibility

    Returns:
        List of dictionaries containing code samples with their rewrites
    """
    print_status("Starting code rewriting process...")

    with open(input_file) as f:
        data = json.load(f)

    print_status(f"Loaded {len(data)} samples from {input_file}")
    print_status(f"Rewrite settings: model={model}, n_rewrites={n_rewrites}, temperature={temperature}, top_p={top_p}, seed={seed}")

    data_with_rewrites = []
    for i, elem in enumerate(data, 1):
        print_status(f"Rewriting code sample {i}/{len(data)}")

        elem['rewrites'] = rewrite(elem['code'], n_samples=n_rewrites, model=model,
                                  temperature=temperature, top_p=top_p, seed=seed)
        elem['code'] = clean_code(elem['code'])
        data_with_rewrites.append(elem)

        print_status(f"  Generated {len(elem['rewrites'])} rewrites")

    with open(output_file, 'w') as f:
        json.dump(data_with_rewrites, f, indent=2)

    print_status(f"Saved rewritten data to {output_file}")
    return data_with_rewrites
