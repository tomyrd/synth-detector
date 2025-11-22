# Rewriter Validation & Cleanup Solution

## Problem Summary

The rewriter was generating invalid entries with two main issues:

1. **Non-function rewrites**: Formulas like `"SA = 4 * pi * radius^2"` instead of Python functions
2. **Doctest examples**: Test code like `">>> my_list = [1, 2, 3]..."` instead of function definitions
3. **Incomplete entries**: Entries with fewer than 4 rewrites due to parsing failures

## Impact

From the analysis of `similarity_data.json` (200 entries):
- **74 invalid rewrites** found (10.1% of all rewrites)
  - 10 doctests
  - 37 formulas
  - 20 entries with no function definition
  - 7 syntax errors
- **93 entries removed** (46.5%) for having fewer than 4 valid rewrites
- **107 clean entries** remain (53.5%) with guaranteed 4+ valid function rewrites

## Solution Components

### 1. Validation Module (`validate_rewrites.py`)

A comprehensive validation system that checks if code is a valid Python function:

```python
from validate_rewrites import is_valid_function_rewrite

# Returns True only for valid Python function definitions
is_valid_function_rewrite("def foo(): return 42")  # ✓ True
is_valid_function_rewrite("SA = 4 * pi * r^2")     # ✗ False (formula)
is_valid_function_rewrite(">>> foo()")             # ✗ False (doctest)
```

**Validation checks:**
- ✓ Valid Python syntax (using AST parsing)
- ✓ Contains at least one function definition
- ✓ Has top-level function (not just imports)
- ✗ Rejects doctests (lines starting with `>>>`)
- ✗ Rejects formulas without function definitions
- ✗ Rejects empty or whitespace-only strings

### 2. Updated Rewriter (`rewritter.ipynb`)

The notebook now includes:

**Automatic validation**: Every generated rewrite is validated before being added
```python
if is_valid_function_rewrite(rewrite_code):
    rewrites.append(rewrite_code)
```

**Retry logic**: Attempts up to `max_attempts` (default: 10) to get enough valid rewrites
```python
def rewrite(code: str, n_samples: int = 4, max_attempts: int = 10)
```

**Better error reporting**: Distinguishes between parsing failures and validation failures

### 3. Data Cleanup Script (`clean_rewrite_data.py`)

A standalone script to clean existing data files:

```bash
# Clean similarity_data.json (creates similarity_data_cleaned.json)
python detector/clean_rewrite_data.py

# Clean both data files
python detector/clean_rewrite_data.py --all

# Clean with custom minimum rewrites (default is 4)
python detector/clean_rewrite_data.py --min-rewrites 3

# Overwrite original file (careful!)
python detector/clean_rewrite_data.py --in-place

# Clean specific file
python detector/clean_rewrite_data.py --input detector/rewritten_data.json
```

**Statistics output:**
- Total entries processed/kept/removed
- Total rewrites before/after cleaning
- Invalid rewrites by type (doctests, formulas, etc.)
- Entries removed for insufficient valid rewrites

## Usage Guide

### For New Rewrite Generation

Just use the updated `rewritter.ipynb`:

```python
from validate_rewrites import is_valid_function_rewrite

# The rewrite() function now automatically validates
rewrites = rewrite(code, n_samples=4)  # Returns only valid function rewrites
```

### For Cleaning Existing Data

```bash
# Preview what will be cleaned (creates new file)
python detector/clean_rewrite_data.py --input detector/similarity_data.json

# Clean both data files
python detector/clean_rewrite_data.py --all

# Apply changes in-place (overwrites original)
python detector/clean_rewrite_data.py --all --in-place
```

### For Custom Validation

```python
from validate_rewrites import (
    is_valid_function_rewrite,      # Check single rewrite
    filter_valid_rewrites,           # Filter list of rewrites
    is_complete_rewrite_entry,       # Check if entry has enough valid rewrites
    clean_rewrite_entry              # Clean an entry dict
)

# Example: Filter rewrites manually
valid_only = filter_valid_rewrites(all_rewrites)

# Example: Check if entry is complete
if is_complete_rewrite_entry(entry, min_rewrites=4):
    process(entry)
```

## Results

After applying the cleanup to `similarity_data.json`:

**Before:**
- 200 entries total
- 730 total rewrites
- 74 invalid rewrites (formulas, doctests, non-functions)
- 93 entries with < 4 valid rewrites

**After (`similarity_data_cleaned.json`):**
- 107 entries (53.5% kept)
- 428 valid rewrites (all validated)
- 0 invalid rewrites
- 100% of entries have ≥4 valid function rewrites

## Files Modified/Created

1. **Created:** `detector/validate_rewrites.py` - Validation utilities
2. **Created:** `detector/clean_rewrite_data.py` - Data cleanup script
3. **Modified:** `detector/rewritter.ipynb` - Added validation to rewrite generation
4. **Created:** `detector/similarity_data_cleaned.json` - Cleaned dataset

## Testing

Run validation tests:
```bash
python detector/validate_rewrites.py
```

Expected output:
```
Running validation tests...

✓ Valid function: expected=True, got=True
✓ Formula without function: expected=False, got=False
✓ Doctest example: expected=False, got=False
✓ Multiple functions: expected=True, got=True
✓ Empty string: expected=False, got=False
✓ Whitespace only: expected=False, got=False
✓ Function with import: expected=True, got=True
✓ Import only, no function: expected=False, got=False

All tests passed!
```

## Recommendations

1. **Use cleaned data**: Switch to `similarity_data_cleaned.json` for higher quality
2. **Regenerate with validation**: Consider re-running rewriter with new validation on removed entries
3. **Monitor validation rate**: Track how often rewrites fail validation
4. **Adjust max_attempts**: Increase if validation failures are common for complex code

## Technical Details

### AST-Based Validation

The validation uses Python's `ast` module to parse and analyze code structure:

```python
tree = ast.parse(code)
has_function = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
```

This ensures:
- Syntax is valid Python
- Code structure is analyzed (not just text patterns)
- Function definitions are properly detected at AST level

### Retry Strategy

The rewriter now uses a while loop with attempt tracking:
- Keeps trying until `n_samples` valid rewrites are collected
- Stops after `max_attempts` to avoid infinite loops
- Logs warnings when insufficient valid rewrites are generated

### Data Integrity

The cleanup script preserves data integrity:
- Never modifies original files unless `--in-place` is used
- Creates `_cleaned` suffix files by default
- Maintains all original fields (`code`, `is_human`, `similarity`)
- Only filters the `rewrites` array
