"""Validation utilities for code rewrites"""

import ast
import re
from typing import List, Optional


def is_valid_function_rewrite(code: str) -> bool:
    """
    Check if a code rewrite is a valid Python function definition.

    Returns False for:
    - Invalid Python syntax
    - Code without function definitions
    - Doctest examples (starting with >>>)
    - Simple formulas or expressions
    - Empty or whitespace-only strings

    Args:
        code: The code string to validate

    Returns:
        True if the code is a valid function definition, False otherwise
    """
    if not code or not code.strip():
        return False

    # Check for doctest format (lines starting with >>>)
    if re.search(r'^\s*>>>', code, re.MULTILINE):
        return False

    # Check for mathematical formulas without function definitions
    # (e.g., "SA = 4 * pi * radius^2")
    if not 'def ' in code:
        return False

    try:
        # Parse the code to check syntax
        tree = ast.parse(code)

        # Check that at least one function definition exists
        has_function = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))

        if not has_function:
            return False

        # Check that the code isn't just imports and expressions
        # At least one FunctionDef should be at module level
        has_top_level_function = any(isinstance(node, ast.FunctionDef) for node in tree.body)

        return has_top_level_function

    except SyntaxError:
        return False
    except Exception:
        # Catch any other parsing errors
        return False


def filter_valid_rewrites(rewrites: List[str]) -> List[str]:
    """
    Filter a list of rewrites to only include valid function definitions.

    Args:
        rewrites: List of code rewrite strings

    Returns:
        List of valid rewrites only
    """
    return [rewrite for rewrite in rewrites if is_valid_function_rewrite(rewrite)]


def is_complete_rewrite_entry(entry: dict, min_rewrites: int = 4) -> bool:
    """
    Check if a rewrite entry has the minimum number of valid rewrites.

    Args:
        entry: Dictionary with 'rewrites' key
        min_rewrites: Minimum number of valid rewrites required

    Returns:
        True if entry has at least min_rewrites valid rewrites
    """
    if 'rewrites' not in entry:
        return False

    valid_rewrites = filter_valid_rewrites(entry['rewrites'])
    return len(valid_rewrites) >= min_rewrites


def clean_rewrite_entry(entry: dict, min_rewrites: int = 4) -> Optional[dict]:
    """
    Clean a rewrite entry by filtering invalid rewrites.

    Args:
        entry: Dictionary with 'code', 'is_human', 'rewrites' keys
        min_rewrites: Minimum number of valid rewrites to keep the entry

    Returns:
        Cleaned entry dict if it has enough valid rewrites, None otherwise
    """
    if 'rewrites' not in entry:
        return None

    valid_rewrites = filter_valid_rewrites(entry['rewrites'])

    if len(valid_rewrites) < min_rewrites:
        return None

    # Return a new entry with only valid rewrites
    cleaned = entry.copy()
    cleaned['rewrites'] = valid_rewrites
    return cleaned


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("def foo():\n    return 42", True, "Valid function"),
        ("SA = 4 * pi * radius^2", False, "Formula without function"),
        (">>> my_list = [1, 2, 3]\n>>> foo(my_list)", False, "Doctest example"),
        ("def bar(x):\n    return x * 2\n\ndef baz():\n    pass", True, "Multiple functions"),
        ("", False, "Empty string"),
        ("   \n\n  ", False, "Whitespace only"),
        ("import math\n\ndef calc():\n    return math.pi", True, "Function with import"),
        ("import math", False, "Import only, no function"),
    ]

    print("Running validation tests...\n")
    all_passed = True
    for code, expected, description in test_cases:
        result = is_valid_function_rewrite(code)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        print(f"{status} {description}: expected={expected}, got={result}")

    print(f"\n{'All tests passed!' if all_passed else 'Some tests failed!'}")
