# axm/deprecation.py
# Handle deprecated syntax - warn user, but still works

# Map: deprecated -> new
DEPRECATED_SYNTAX = {
    "FUN": "TASK",
    # Add more as needed.
}

# Warning mode: "warn" (default), "error", "ignore"
WARNING_MODE = "warn"


def set_warning_mode(mode):
    """Set warning mode: 'warn', 'error', 'ignore'."""
    global WARNING_MODE
    if mode in ("warn", "error", "ignore"):
        WARNING_MODE = mode
    else:
        raise ValueError(f"Invalid warning mode: {mode}")


def is_deprecated(keyword):
    """Check if keyword is deprecated."""
    return keyword in DEPRECATED_SYNTAX


def get_new_syntax(keyword):
    """Get new syntax for deprecated keyword."""
    return DEPRECATED_SYNTAX.get(keyword, keyword)


def warn_deprecated(keyword, line=None):
    """Warn user about deprecated syntax."""
    if WARNING_MODE == "ignore":
        return

    new_syntax = get_new_syntax(keyword)
    msg = f"Deprecated syntax '{keyword}' - use '{new_syntax}' instead."
    if line:
        msg += f" (line {line})"

    if WARNING_MODE == "error":
        raise SyntaxError(msg)
    else:
        print(f"[AXIOM WARNING] {msg}")