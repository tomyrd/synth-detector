"""
Utility functions for the synthetic code detection pipeline
"""

import re


def print_status(message: str):
    """Print status message with formatting"""
    print(f"[STATUS] {message}")


def clean_code(code: str) -> str:
    """Remove comments and normalize whitespace"""
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    code = '\n'.join(line for line in code.split('\n') if line.strip())
    return code.strip()
