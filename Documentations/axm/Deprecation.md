# Deprecation System

`axm/deprecation.py` — handle deprecated syntax, warn user, but still works.

---

## Overview

Deprecated syntax still works, but shows a warning to encourage migration.

**Config** (`GAME_CONFIG.json`):

    "DEPRECATION_MODE": "warn"

| Mode | Behavior |
|------|----------|
| `"warn"` | Print warning, continue (default) |
| `"error"` | Raise `SyntaxError`, stop script |
| `"ignore"` | No warning, continue |

---

## Deprecated Syntax Map

`DEPR_KEYWORDS` (in `lexer.py`):

    DEPR_KEYWORDS = {
        "FUN": "TASK",
        # Add more as needed:
        # "VAR": "LET",
        # "RETURN": "GIVE",
        # "SAY": "SPEAK",
    }

---

## Flow

1. **Lexer** — tokenize `FUN`
2. **Check** — `word in DEPR_KEYWORDS` → `FUN` deprecated
3. **Warn** — `warn_deprecated("FUN", line)` → print `[AXIOM WARNING]`
4. **Token** — `Token("FUN", "FUN")` — still works
5. **Parser** — `parse_function_def` — handle `FUN` (same as `TASK`)

---

## Example

**File**: `test.axm`

    FUN add(a, b)
      RETURN a + b

**Output** (`DEPRECATION_MODE: "warn"`):

    [AXIOM WARNING] Deprecated syntax 'FUN' - use 'TASK' instead. (line 1)
    [AXIOM] add(1, 2) = 3

**Output** (`DEPRECATION_MODE: "error"`):

    [AXIOM] Error: Deprecated syntax 'FUN' - use 'TASK' instead. (line 1)

**Output** (`DEPRECATION_MODE: "ignore"`):

    [AXIOM] add(1, 2) = 3

---

## Migration

**Old**:

    FUN add(a, b)
      RETURN a + b

**New**:

    TASK add(a, b)
      RETURN a + b