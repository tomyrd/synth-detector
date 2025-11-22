# Synthetic Code Detection Modules

This directory contains the modular components of the synthetic code detection pipeline. Each module is focused on a specific aspect of the pipeline, making the codebase easier to understand, test, and maintain.

## Module Structure

```
modules/
├── __init__.py       # Package initialization and exports
├── utils.py          # Utility functions
├── generator.py      # Synthetic code generation
├── rewriter.py       # Code rewriting
├── similarity.py     # Similarity computation
└── detector.py       # Detection and classification
```

## Modules Overview

### utils.py
**Purpose:** Common utility functions used across the pipeline

**Key Functions:**
- `print_status(message)` - Formatted status message printing
- `clean_code(code)` - Remove comments and normalize whitespace

**Dependencies:** None (standard library only)

### generator.py
**Purpose:** Generate synthetic code using LLMs

**Key Functions:**
- `generate_synth_code(prompt, model, temperature, top_p)` - Generate synthetic code from a prompt
- `prepare_dataset(input_file, output_file, ...)` - Create balanced dataset of human/synthetic code

**Dependencies:** `ollama`, `utils`

**Configuration Parameters:**
- `model`: LLM model to use
- `temperature`: Sampling temperature
- `top_p`: Nucleus sampling parameter

### rewriter.py
**Purpose:** Generate code rewrites to measure consistency

**Key Functions:**
- `rewrite(code, n_samples, model, temperature, top_p, seed)` - Generate multiple rewrites of code
- `rewrite_dataset(input_file, output_file, ...)` - Process entire dataset

**Dependencies:** `ollama`, `utils`

**Configuration Parameters:**
- `n_samples`: Number of rewrites to generate
- `model`: LLM model to use
- `temperature`: Sampling temperature (default: 0.8)
- `top_p`: Nucleus sampling parameter (default: 0.95)
- `seed`: Random seed for reproducibility

### similarity.py
**Purpose:** Compute similarity scores between code samples

**Key Functions:**
- `normalized_edit_distance(s1, s2)` - Calculate normalized edit distance
- `compute_similarity(original, rewrites)` - Average similarity between original and rewrites
- `compute_similarities(input_file, output_file)` - Process entire dataset

**Dependencies:** `numpy`, `difflib`, `utils`

**Key Metric:** Similarity score (0-1, higher = more similar)

### detector.py
**Purpose:** Classify code as human or synthetic

**Key Functions:**
- `predict_synth_code(data, threshold)` - Run detection and compute metrics

**Dependencies:** `utils`

**Configuration Parameters:**
- `threshold`: Similarity threshold for classification (default: 0.7)

**Returns:** Dictionary with accuracy, false positive rate, false negative rate, and counts

## Using the Modules

### Direct Import
```python
from modules import generate_synth_code, rewrite, compute_similarity

# Generate synthetic code
code = generate_synth_code("Write a function to sort a list", model="codellama:7b-instruct")

# Generate rewrites
rewrites = rewrite(code, n_samples=4, temperature=0.8)

# Compute similarity
similarity = compute_similarity(code, rewrites)
```

### Individual Module Import
```python
from modules.generator import generate_synth_code, prepare_dataset
from modules.rewriter import rewrite, rewrite_dataset
from modules.similarity import compute_similarity, compute_similarities
from modules.detector import predict_synth_code
from modules.utils import print_status, clean_code
```

## Development Guidelines

### Adding New Features
1. Identify which module the feature belongs to
2. Add the function to the appropriate module
3. Update `__init__.py` if the function should be exported
4. Add tests for the new functionality
5. Update this README with the new function

### Module Responsibilities
- **utils**: Generic utilities with no domain-specific logic
- **generator**: Anything related to creating synthetic code
- **rewriter**: Anything related to generating code variations
- **similarity**: Anything related to measuring code similarity
- **detector**: Anything related to classification and metrics

### Best Practices
- Keep modules focused on their specific responsibility
- Avoid circular dependencies between modules
- Use type hints for function signatures
- Document all public functions with docstrings
- Keep external dependencies isolated to specific modules

## Testing

To test individual modules:

```python
# Test generator
from modules.generator import generate_synth_code
code = generate_synth_code("Write a function to add two numbers")
print(code)

# Test rewriter
from modules.rewriter import rewrite
from modules.utils import clean_code
original = "def add(a, b):\n    return a + b"
rewrites = rewrite(original, n_samples=2)
print(f"Generated {len(rewrites)} rewrites")

# Test similarity
from modules.similarity import compute_similarity
score = compute_similarity(original, rewrites)
print(f"Similarity: {score:.4f}")
```

## Module Dependencies

```
synth_detector.py (main)
    ├── modules.generator
    │   └── modules.utils
    ├── modules.rewriter
    │   └── modules.utils
    ├── modules.similarity
    │   └── modules.utils
    └── modules.detector
        └── modules.utils
```

All modules depend on `utils`, but are otherwise independent of each other.
