# --- utils/validators.py ---
"""
Utility module for simple validation of generated Python code.
"""

def validate_python_code(code: str) -> bool:
    """
    Validate Python code by attempting to compile it.

    Args:
        code (str): The Python source code to validate.

    Returns:
        bool: True if code compiles without errors, False otherwise.
    """
    try:
        compile(code, '<generated_test>', 'exec')
        return True
    except Exception as e:
        # Optionally log the exception via the logger if needed
        return False
    